from decimal import Decimal
from typing import Optional

from .base import BaseExchangeAdapter

KUCOIN_API_URL = "https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={}"
KUCOIN_SUCCESS_CODE = "200000"


class KuCoinExchangeService(BaseExchangeAdapter):
    @property
    def name(self) -> str:
        return "kucoin"

    def get_api_url(self, symbol: str) -> str:
        return KUCOIN_API_URL.format(symbol)

    def extract_price(self, data: dict) -> Optional[Decimal]:
        """
        Override default extraction for KuCoin, which expects a specific success code
        and a nested structure for the price.
        """
        if data.get("code") != KUCOIN_SUCCESS_CODE:
            raise Exception("KuCoin API error")
        price = data.get("data", {}).get("price")
        return Decimal(price) if price is not None else None

    def format_symbol_direct(self, currency_from: str, currency_to: str) -> str:
        return f"{currency_from.upper()}-{currency_to.upper()}"

    def format_symbol_inverse(self, currency_from: str, currency_to: str) -> str:
        return f"{currency_to.upper()}-{currency_from.upper()}"
