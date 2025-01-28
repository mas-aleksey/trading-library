from datetime import datetime, timedelta, timezone
from typing import Generator

from clients.bingx import BingXClient
from core.settings import BingXConfig
from pydantic import BaseModel
from schemas.base import Candle, Order, OrderIN, OrderSide, Position
from trading.exchanges.base import BaseExchange

BINGX_INTERVALS = {
    1: "1m",
    3: "3m",
    5: "5m",
    15: "15m",
    30: "30m",
    60: "1h",
    2 * 60: "2h",
    4 * 60: "4h",
    6 * 60: "6h",
    8 * 60: "8h",
    12 * 60: "12h",
    24 * 60: "1d",
    3 * 24 * 60: "3d",
    7 * 24 * 60: "1w",
    30 * 24 * 60: "1M",
}


class BingXPairStat(BaseModel):
    symbol: str
    start_time: int | None = None


class BingXExchange(BaseExchange):

    def __init__(self, config: BingXConfig):
        self.client = BingXClient(config)
        self.statistics: dict[str, BingXPairStat] = {}

    async def stop(self) -> None:
        await self.client.stop()

    def statistic(self, symbol: str) -> BingXPairStat:
        if symbol not in self.statistics:
            self.statistics[symbol] = BingXPairStat(symbol=symbol)
        return self.statistics[symbol]

    async def init(self, symbol: str) -> Generator[Candle, None, None]:
        start_date = datetime.now(tz=timezone.utc) - timedelta(
            days=6, hours=23, minutes=59, seconds=59
        )
        end_date = datetime.now(tz=timezone.utc)
        size = 1000
        count = int((end_date - start_date).total_seconds() / 60 / size) + 1
        for offset in range(count):
            start_time = start_date + timedelta(minutes=offset * size)
            async for candle in self.get_candles(
                symbol=symbol,
                size=size,
                start_time=int(start_time.timestamp()) * 1000,
            ):
                yield candle

    async def get_candles(
        self, symbol: str, timeframe: int = 1, size: int = 1000, start_time: int = None
    ) -> Generator[Candle, None, None]:
        stat = self.statistic(symbol)
        list_data = await self.client.get_candles(
            symbol=f"{symbol}-USDT",
            interval=BINGX_INTERVALS[timeframe],
            limit=size,
            start_time=start_time or stat.start_time,
        )
        list_data.reverse()
        for data in list_data:
            stat.start_time = data[0]
            c = Candle(
                time=data[0],
                open=data[1],
                high=data[2],
                low=data[3],
                close=data[4],
                volume=data[7],
            )
            c.time = c.time.astimezone()
            yield c

    async def place_order(self, order_in: OrderIN, client_oid: str = None) -> Order:
        order = await self.client.place_order(
            f"{order_in.symbol}-USDT", order_in.side, order_in.amount, client_oid
        )
        return Order(
            time=order.transactTime,
            price=order.price,
            amount=order.executedQty,
            side=order.side,
            status=order.status,
            cost=order.cummulativeQuoteQty,
        )

    async def get_orders_history(self, symbol: str) -> list[Order]:
        order_hist = await self.client.get_order_history(f"{symbol}-USDT")
        return [
            Order(
                time=order.transactTime,
                price=order.price,
                amount=order.executedQty,
                side=order.side,
                status=order.status,
                cost=order.cummulativeQuoteQty,
            )
            for order in order_hist
            if order.symbol == f"{symbol}-USDT"
        ]

    async def get_balance(self, symbol: str) -> tuple[float, float]:
        balances = await self.client.get_balances()
        return balances.free_for_asset(symbol), balances.free_for_asset("USDT")

    async def get_position_info(self, symbol: str) -> Position:
        orders = await self.client.get_order_history(f"{symbol}-USDT")
        orders.reverse()
        total_cost, total_amount, avg_price = 0, 0, 0

        for order in orders:
            if order.status != "FILLED":
                continue

            if order.side == OrderSide.BUY:
                total_cost += order.price * order.executedQty
                total_amount += order.executedQty
                avg_price = total_cost / total_amount
            else:
                total_amount -= order.executedQty
                total_cost = avg_price * total_amount

        return Position(amount=total_amount, avg_cost=avg_price)
