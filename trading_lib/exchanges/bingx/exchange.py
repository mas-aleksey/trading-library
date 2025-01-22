from typing import Generator

from common.exchange import BaseExchange
from common.schemas import Candle, Order, OrderIN
from exchanges.bingx.client import BingXClient, BingXConfig
from pydantic import BaseModel

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

    def __init__(self, config: BingXConfig) -> None:
        self.client = BingXClient(config)
        self.statistics: dict[str, BingXPairStat] = {}

    async def stop(self) -> None:
        await self.client.stop()

    def _statistic(self, symbol: str) -> BingXPairStat:
        if symbol not in self.statistics:
            self.statistics[symbol] = BingXPairStat(symbol=symbol)
        return self.statistics[symbol]

    async def get_candles(
        self, symbol: str, timeframe: int = 1, size: int = 1000, start_time: int = None
    ) -> Generator[Candle, None, None]:
        stat = self._statistic(symbol)
        list_data = await self.client.get_candles(
            symbol=f"{symbol}-USDT",
            interval=BINGX_INTERVALS[timeframe],
            limit=size,
            start_time=start_time or stat.start_time,
        )
        list_data.reverse()
        for data in list_data:
            stat.start_time = data[0]
            yield Candle(
                time=data[0],
                open=data[1],
                high=data[2],
                low=data[3],
                close=data[4],
                volume=data[7],
            )

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

    async def get_balance(self, symbol: str) -> tuple[float, float]:
        balances = await self.client.get_balances()
        return balances.free_for_asset(symbol), balances.free_for_asset("USDT")
