import csv
from pathlib import Path
from typing import Generator

from core.settings import CSVConfig
from schemas.base import Candle, Order, OrderIN, OrderSide, Position
from trading.exchanges.base import BaseExchange


class CSVExchange(BaseExchange):

    def __init__(self, config: CSVConfig):
        self.path = config.PATH
        self.balance: float = 10000
        self.amount: float = 0

    def _files(self) -> list[Path]:
        path = Path(self.path)
        if path.is_file():
            return [path]
        return sorted(path.glob("*.csv"))

    async def stop(self) -> None:
        pass

    async def init(self, *_args, **_kwargs) -> Generator[Candle, None, None]:
        if False:
            yield

    async def get_candles(self, *_args, **_kwargs) -> Generator[Candle, None, None]:
        for file in self._files():
            with Path(file).open(newline="") as csvfile:
                for row in csv.reader(csvfile):
                    yield Candle.from_csv(row)

    async def place_order(self, order_in: OrderIN, *_args, **_kwargs) -> Order:
        cost = order_in.amount * order_in.price
        if order_in.side == OrderSide.BUY:
            self.balance -= cost
            self.amount += order_in.amount
        if order_in.side == OrderSide.SELL:
            self.balance += cost
            self.amount -= order_in.amount
        return Order(
            time=order_in.time,
            price=order_in.price,
            amount=order_in.amount,
            side=order_in.side,
            status="FILLED",
            cost=cost,
        )

    async def get_position_info(self, symbol: str) -> Position:
        pass

    async def get_orders_history(self, order_id: str) -> dict:
        pass

    async def get_balance(self, *_args, **_kwargs) -> tuple[float, float]:
        return self.amount, self.balance
