import abc
import logging
from typing import Generator

from schemas.base import Candle, Order, OrderIN, Position

logger = logging.getLogger()


class BaseExchange(abc.ABC):

    @abc.abstractmethod
    async def stop(self) -> None:
        raise NotImplementedError("Please implement 'stop' method")

    @abc.abstractmethod
    async def init(self, symbol: str) -> Generator[Candle, None, None]:
        yield NotImplementedError("Please implement 'get_candles' method")

    @abc.abstractmethod
    async def get_candles(
        self, symbol: str, timeframe: int = 1, size: int = 1000, start_time: int = None
    ) -> Generator[Candle, None, None]:
        yield NotImplementedError("Please implement 'get_candles' method")

    @abc.abstractmethod
    async def place_order(self, order_in: OrderIN, client_oid: str = None) -> Order:
        raise NotImplementedError("Please implement 'place_order' method")

    @abc.abstractmethod
    async def get_orders_history(self, symbol: str) -> dict:
        raise NotImplementedError("Please implement 'get_orders_history' method")

    @abc.abstractmethod
    async def get_position_info(self, symbol: str) -> Position:
        raise NotImplementedError("Please implement 'get_position_info' method")

    @abc.abstractmethod
    async def get_balance(self, symbol: str) -> tuple[float, float]:
        raise NotImplementedError("Please implement 'get_balances' method")
