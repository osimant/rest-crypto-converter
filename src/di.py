from fastapi import Depends, Request

from src.adapters.exchange.base import IExchangeAdapter
from src.adapters.exchange.binance import BinanceExchangeService
from src.adapters.exchange.kucoin import KuCoinExchangeService
from src.services.exchange import ConversionService


def get_redis_client(request: Request):
    return request.app.state.redis


def get_conversion_service(redis_client=Depends(get_redis_client)) -> IExchangeAdapter:
    exchange_clients = [BinanceExchangeService(), KuCoinExchangeService()]
    return ConversionService(redis_client, exchange_clients=exchange_clients)
