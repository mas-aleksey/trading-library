from dataclasses import dataclass, field

from common.enums import Signal
from common.schemas import Candle, OrderIN, Position
from strategies.base import BaseStrategy


@dataclass
class ExampleStrategy(BaseStrategy):
    take_profit: float
    orders_map: list[tuple[float, float]]
    orders: list = field(default_factory=list)

    async def _handle(self, candle: Candle, sig: Signal) -> Position | None:
        if sig == Signal.BUY and self.position is None:
            await self.open_position(candle)

        if self.position is None:
            return

        delta = round((candle.close - self.position.avg_price) / self.position.avg_price * 100, 3)
        if delta > self.take_profit:
            return await self.close_position(candle)

        if delta < 0:
            await self.averaging(abs(delta), candle)

    async def open_position(self, candle: Candle) -> None:
        _, balance = await self.exchange.get_balance(self.symbol)
        self.orders = [(d, balance * r) for d, r in self.orders_map]
        _, cost = self.orders.pop(0)
        amount = cost / candle.close
        order = await self.exchange.place_order(OrderIN.buy(self.symbol, amount, candle))
        self.position = Position.new(order)

    async def close_position(self, candle: Candle) -> Position:
        amount, balance = await self.exchange.get_balance(self.symbol)
        order = await self.exchange.place_order(OrderIN.sell(self.symbol, amount, candle))
        self.position.add_sell(order)
        position = self.position
        self.position = None
        return position

    async def averaging(self, delta: float, candle: Candle) -> None:
        _, balance = await self.exchange.get_balance(self.symbol)
        if balance < 1:
            return
        if not self.orders:
            return
        cost = 0
        if delta > self.orders[0][0]:
            _, cost = self.orders.pop(0)
        if cost > balance:
            cost = balance
        if cost == 0:
            return
        amount = cost / candle.close
        order = await self.exchange.place_order(OrderIN.buy(self.symbol, amount, candle))
        self.position.add_buy(order)
