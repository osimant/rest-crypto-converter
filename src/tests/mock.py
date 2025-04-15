import time
from decimal import Decimal
from typing import Dict, Optional, Tuple

from src.adapters.exchange.base import IExchangeAdapter


class MockExchangeAdapter(IExchangeAdapter):
    @property
    def name(self) -> str:
        return "mock"

    async def get_rate(
        self, currency_from: str, currency_to: str
    ) -> Tuple[Optional[Decimal], Optional[str], Optional[int]]:
        if currency_from.upper() == currency_to.upper():
            return (
                Decimal("1.0"),
                f"{currency_from.upper()}{currency_to.upper()}",
                int(time.time()),
            )
        else:
            return (
                Decimal("2.0"),
                f"{currency_from.upper()}{currency_to.upper()}",
                int(time.time()),
            )


class MockRedisClient:
    """
    A simple in-memory mock redis client to simulate async get/set.
    """

    def __init__(self):
        self.store: Dict[str, str] = {}

    async def get(self, key: str) -> Optional[str]:
        return self.store.get(key)

    async def set(self, key: str, value: str, ex: int = None) -> None:
        self.store[key] = value

    async def close(self):
        pass
