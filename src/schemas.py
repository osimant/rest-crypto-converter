from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class ConvertRequest(BaseModel):
    currency_from: str
    currency_to: str
    exchange: Optional[str] = None
    amount: Decimal
    cache_max_seconds: Optional[int] = None


class ConvertResponse(BaseModel):
    currency_from: str
    currency_to: str
    exchange: str
    rate: Decimal
    result: Decimal
    updated_at: int
