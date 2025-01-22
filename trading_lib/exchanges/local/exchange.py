import csv
from pathlib import Path
from typing import Generator

from common.enums import OrderSide
from common.exchange import BaseExchange
from common.schemas import Candle, Order, OrderIN
from exchanges.local.config import CSVConfig


class CSVExchange(BaseExchange):

    def __init__(self, config: CSVConfig) -> None:
        self.path = config.PATH
        self.balance = config.INITIAL_BALANCE
        self.amount: float = 0

    def _files(self) -> list[Path]:
        path = Path(self.path)
        if path.is_file():
            return [path]
        return sorted(path.glob("*.csv"))

    async def stop(self) -> None:
        pass

    async def get_candles(
        self, _symbol: str, _timeframe: int = 1, _size: int = 1000, _start_time: int = None
    ) -> Generator[Candle, None, None]:
        for file in self._files():
            with Path(file).open(newline="") as csvfile:
                for data in csv.reader(csvfile):
                    yield Candle(
                        time=float(data[0]),
                        open=float(data[1]),
                        high=float(data[2]),
                        low=float(data[3]),
                        close=float(data[4]),
                        volume=float(data[5]),
                    )

    async def place_order(self, order_in: OrderIN, _client_oid: str = None) -> Order:
        cost = order_in.amount * order_in.candle.close
        if order_in.side == OrderSide.BUY:
            self.balance -= cost
            self.amount += order_in.amount
        if order_in.side == OrderSide.SELL:
            self.balance += cost
            self.amount -= order_in.amount
        return Order(
            time=order_in.candle.time,
            price=order_in.candle.close,
            amount=order_in.amount,
            side=order_in.side,
            status="FILLED",
            cost=cost,
        )

    async def get_balance(self, _symbol: str) -> tuple[float, float]:
        return self.amount, self.balance
