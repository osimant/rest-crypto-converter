from decimal import Decimal

import pytest

from src.schemas import ConvertRequest
from src.services.exchange import ConversionService

from .mock import MockExchangeAdapter, MockRedisClient


@pytest.fixture
def mock_redis_client():
    return MockRedisClient()


@pytest.fixture
def mock_exchange_adapter():
    return MockExchangeAdapter()


@pytest.fixture
def conversion_service(mock_redis_client, mock_exchange_adapter):
    return ConversionService(
        mock_redis_client, exchange_clients=[mock_exchange_adapter]
    )


@pytest.mark.asyncio
async def test_conversion(conversion_service: ConversionService):
    req = ConvertRequest(
        currency_from="WCT",
        currency_to="USDT",
        exchange=None,
        amount=1,
        cache_max_seconds=30,
    )
    resp = await conversion_service.convert(req)

    assert resp.currency_from == "WCT"
    assert resp.currency_to == "USDT"
    assert resp.exchange == "mock"
    assert resp.rate == Decimal("2.0")
    assert resp.result == Decimal("2.0")


@pytest.mark.asyncio
async def test_cached_conversion(
    conversion_service: ConversionService, mock_redis_client: MockRedisClient
):
    req = ConvertRequest(
        currency_from="WCT",
        currency_to="USDT",
        exchange=None,
        amount=1,
        cache_max_seconds=30,
    )
    first_resp = await conversion_service.convert(req)
    second_resp = await conversion_service.convert(req)

    assert first_resp.model_dump() == second_resp.model_dump()
