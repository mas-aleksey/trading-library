import logging
from dataclasses import dataclass, field
from uuid import UUID

from db.db_connector import DatabaseConnector
from schemas.base import Candle, Position
from trading.chart import Chart
from trading.exchanges.base import BaseExchange
from trading.indicators import Signal
from trading.notifier import NotifyService


@dataclass
class BaseStrategy:
    strategy_id: UUID
    symbol: str
    chart: Chart
    exchange: BaseExchange
    db: DatabaseConnector
    notifier: NotifyService
    online_check: bool
    position: Position | None = field(init=False)
    logger: logging.Logger = field(init=False)

    def __post_init__(self):
        self.position = None
        self.logger = logging.getLogger(self.__class__.__name__)

    async def init(self) -> None:
        raise NotImplementedError("Please implement init method")

    async def handle(self, candle: Candle) -> Position | None:
        sig = self.chart.add(candle)
        if self.chart.is_ready:
            if self.online_check is True and self.chart.is_online is False:
                return
            self.logger.info(f"get online candle {candle.time.isoformat()}")
            position = await self._handle(candle, sig)
            if position is not None:
                await self.notifier.send_position(self.chart, position, self.symbol)
            await self.notifier.send_chart(self.chart, sig, candle, self.symbol)
            return position

    async def _handle(self, candle: Candle, sig: Signal) -> Position | None:
        raise NotImplementedError("Please implement _handle method")
