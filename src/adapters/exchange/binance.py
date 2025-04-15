from .base import BaseExchangeAdapter

BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price?symbol={}"


class BinanceExchangeService(BaseExchangeAdapter):
    @property
    def name(self) -> str:
        return "binance"

    def get_api_url(self, symbol: str) -> str:
        return BINANCE_API_URL.format(symbol)
