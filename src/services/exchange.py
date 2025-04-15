import json
import time
from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation
from typing import List, Optional

from src.adapters.exchange.base import IExchangeAdapter
from src.schemas import ConvertRequest, ConvertResponse

CACHE_EXPIRATION = 3600


class IConversionService(ABC):
    @abstractmethod
    async def convert(self, req: ConvertRequest) -> ConvertResponse:
        """
        Convert a given cryptocurrency amount from one currency to another.
        """
        pass


class ConversionService(IConversionService):
    """
    Converts cryptocurrency amounts using rate data provided by injected exchange clients.
    Supports caching using an injected Redis client.
    """

    def __init__(
        self, redis_client, exchange_clients: Optional[List[IExchangeAdapter]] = None
    ):
        """
        Args:
            redis_client: An aioredis client instance for caching conversion results.
            exchange_clients (Optional[List[IExchangeAdapter]]): A list of exchange API wrappers.
                This list must be provided and can include instances such as BinanceExchange, KuCoinExchange, etc.
        """
        if exchange_clients is None or len(exchange_clients) == 0:
            raise ValueError("At least one exchange client must be provided.")
        self.redis = redis_client
        self.exchange_clients: List[IExchangeAdapter] = exchange_clients

    async def convert(self, req: ConvertRequest) -> ConvertResponse:
        """
        Converts a cryptocurrency amount using data from multiple exchanges.
        Checks the cache (if cache_max_seconds is provided) before querying exchanges.
        Tries a direct rate, and if that fails and neither currency is USDT, attempts an indirect conversion via USDT.

        Args:
            req (ConvertRequest): The conversion request parameters.

        Returns:
            ConvertResponse: The conversion result including the rate, result, exchange used, and timestamp.
        """
        exchanges_to_try = []
        if req.exchange:
            preferred = req.exchange.lower()
            for ex in self.exchange_clients:
                if ex.name == preferred:
                    exchanges_to_try.append(ex)
            for ex in self.exchange_clients:
                if ex.name != preferred:
                    exchanges_to_try.append(ex)
        else:
            exchanges_to_try = self.exchange_clients

        error_messages = []
        conversion_result = None

        def build_cache_key(ex_name: str) -> str:
            return f"{ex_name}:{req.currency_from.upper()}:{req.currency_to.upper()}"

        for ex in exchanges_to_try:
            cache_key = build_cache_key(ex.name)
            if req.cache_max_seconds is not None and self.redis:
                cached_value = await self.redis.get(cache_key)
                if cached_value:
                    cached_obj = json.loads(cached_value)
                    if (time.time() - cached_obj["updated_at"]) < req.cache_max_seconds:
                        conversion_result = cached_obj
                        break

            rate, symbol, ts = await ex.get_rate(req.currency_from, req.currency_to)

            if (
                rate is None
                and req.currency_from.upper() != "USDT"
                and req.currency_to.upper() != "USDT"
            ):
                r1, s1, t1 = await ex.get_rate(req.currency_from, "USDT")
                r2, s2, t2 = await ex.get_rate("USDT", req.currency_to)
                if r1 is not None and r2 is not None:
                    rate = r1 * r2
                    ts = int(time.time())

            if rate is not None:
                try:
                    conversion_value = Decimal(req.amount) * rate
                except InvalidOperation:
                    conversion_value = Decimal(0)
                conversion_result = {
                    "currency_from": req.currency_from.upper(),
                    "currency_to": req.currency_to.upper(),
                    "exchange": ex.name,
                    "rate": str(rate.normalize()),
                    "result": str(conversion_value.normalize()),
                    "updated_at": ts,
                }
                if self.redis:
                    await self.redis.set(
                        cache_key, json.dumps(conversion_result), ex=CACHE_EXPIRATION
                    )
                break
            else:
                error_messages.append(
                    f"{ex.name} did not provide rate for {req.currency_from}->{req.currency_to}"
                )

        if conversion_result:
            return ConvertResponse(
                currency_from=conversion_result["currency_from"],
                currency_to=conversion_result["currency_to"],
                exchange=conversion_result["exchange"],
                rate=Decimal(conversion_result["rate"]),
                result=Decimal(conversion_result["result"]),
                updated_at=conversion_result["updated_at"],
            )
        else:
            raise Exception("; ".join(error_messages))
