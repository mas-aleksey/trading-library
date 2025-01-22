import abc
from typing import Generator

from common.schemas import Candle, Order, OrderIN


class BaseExchange(abc.ABC):

    @abc.abstractmethod
    async def stop(self) -> None:
        raise NotImplementedError("Please implement 'stop' method")

    @abc.abstractmethod
    async def get_candles(
        self, symbol: str, timeframe: int = 1, size: int = 1000, start_time: int = None
    ) -> Generator[Candle, None, None]:
        yield NotImplementedError("Please implement 'get_candles' method")

    @abc.abstractmethod
    async def place_order(self, order_in: OrderIN, client_oid: str = None) -> Order:
        raise NotImplementedError("Please implement 'place_order' method")

    @abc.abstractmethod
    async def get_balance(self, symbol: str) -> tuple[float, float]:
        raise NotImplementedError("Please implement 'get_balances' method")
