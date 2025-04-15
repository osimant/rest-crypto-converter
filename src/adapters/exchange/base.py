import time
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional, Tuple

import aiohttp


class IExchangeAdapter(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Returns the name of the exchange (e.g., "binance", "kucoin").
        """
        pass

    @abstractmethod
    async def get_rate(
        self, currency_from: str, currency_to: str
    ) -> Tuple[Optional[Decimal], Optional[str], Optional[int]]:
        """
        Fetch the conversion rate for the given currency pair.

        Returns:
            Tuple of (rate as Decimal or None, symbol used, UNIX timestamp)
        """
        pass


class BaseExchangeAdapter(IExchangeAdapter):
    @abstractmethod
    def get_api_url(self, symbol: str) -> str:
        """
        Construct the full API URL for a given symbol.
        Must be implemented by subclasses.
        """
        pass

    def extract_price(self, data: dict) -> Optional[Decimal]:
        """
        Extract the price value from the API response.
        The default implementation searches for a 'price' key or a nested 'data.price'.
        Subclasses can override this if necessary.
        """
        price = data.get("price")
        if price is None and "data" in data:
            price = data["data"].get("price")
        return Decimal(price) if price is not None else None

    def format_symbol_direct(self, currency_from: str, currency_to: str) -> str:
        """
        Default symbol formatting for direct pairing.
        Can be overridden by subclasses if needed.
        """
        return f"{currency_from.upper()}{currency_to.upper()}"

    def format_symbol_inverse(self, currency_from: str, currency_to: str) -> str:
        """
        Default symbol formatting for inverse pairing.
        Can be overridden by subclasses if needed.
        """
        return f"{currency_to.upper()}{currency_from.upper()}"

    async def fetch_json(self, url: str) -> dict:
        """
        Convenience method to perform an HTTP GET request and return the JSON response.
        """
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=5)
        ) as session:
            async with session.get(url) as resp:
                return await resp.json()

    async def get_rate(
        self, currency_from: str, currency_to: str
    ) -> Tuple[Optional[Decimal], Optional[str], Optional[int]]:
        """
        Retrieve a conversion rate by first trying a direct pairing and, if necessary,
        an inverse pairing.
        """
        symbol_direct = self.format_symbol_direct(currency_from, currency_to)
        url_direct = self.get_api_url(symbol_direct)
        try:
            response = await self.fetch_json(url_direct)
            price = self.extract_price(response)
            if price is not None:
                return price, symbol_direct, int(time.time())
        except Exception:
            pass

        symbol_inverse = self.format_symbol_inverse(currency_from, currency_to)
        url_inverse = self.get_api_url(symbol_inverse)
        try:
            response = await self.fetch_json(url_inverse)
            price = self.extract_price(response)
            if price is not None:
                try:
                    rate = Decimal(1) / price
                except Exception:
                    rate = None
                return rate, symbol_inverse, int(time.time())
        except Exception:
            return None, None, None

        return None, None, None
