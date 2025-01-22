from datetime import datetime, timedelta

from common.enums import OrderSide
from pydantic import BaseModel


class Candle(BaseModel):
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    def merge(self, candle: "Candle") -> "Candle":
        return Candle(
            time=candle.time,
            open=self.open,
            high=max(self.high, candle.high),
            low=min(self.low, candle.low),
            close=candle.close,
            volume=self.volume + candle.volume,
        )

    @property
    def is_red(self) -> bool:
        return self.open > self.close

    @property
    def is_green(self) -> bool:
        return self.open < self.close


class OrderIN(BaseModel):
    symbol: str
    side: OrderSide
    amount: float
    candle: Candle

    @classmethod
    def buy(cls, symbol: str, amount: float, candle: Candle) -> "OrderIN":
        return cls(symbol=symbol, side=OrderSide.BUY, amount=amount, candle=candle)

    @classmethod
    def sell(cls, symbol: str, amount: float, candle: Candle) -> "OrderIN":
        return cls(symbol=symbol, side=OrderSide.SELL, amount=amount, candle=candle)


class Order(BaseModel):
    time: datetime
    price: float
    amount: float
    side: OrderSide
    status: str
    cost: float


class Position(BaseModel):
    orders: list[Order]
    total_amount: float
    total_cost: float
    avg_price: float
    profit: float = 0

    @property
    def duration(self) -> timedelta:
        return self.orders[-1].time - self.orders[0].time

    @classmethod
    def new(cls, order: Order) -> "Position":
        position = cls(orders=[], total_amount=0, total_cost=0, avg_price=0)
        position.add_buy(order)
        return position

    def add_buy(self, order: Order) -> None:
        self.orders.append(order)
        self.total_cost += order.cost
        self.total_amount += order.amount
        self.avg_price = self.total_cost / self.total_amount

    def add_sell(self, order: Order) -> None:
        self.orders.append(order)
        self.total_amount -= order.amount
        self.profit += order.cost - self.total_cost
        self.total_cost = self.avg_price * self.total_amount
