import logging
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path
from uuid import UUID

from common.chart import Chart
from common.enums import OrderSide, Signal
from common.exchange import BaseExchange
from common.notifier import NotifyService
from common.schemas import Candle, Position
from db.db_connector import DatabaseConnector


@dataclass
class BaseStrategy:
    strategy_id: UUID
    symbol: str
    chart: Chart
    exchange: BaseExchange
    online_check: bool
    position: Position | None = field(init=False)
    logger: logging.Logger = field(init=False)
    db: DatabaseConnector | None = field(init=False)
    notifier: NotifyService | None = field(init=False)

    def __post_init__(self) -> None:
        self.position = None
        self.logger = logging.getLogger(self.__class__.__name__)

    async def init(self) -> None:
        raise NotImplementedError("Please implement init method")

    async def handle(self, candle: Candle) -> None:
        sig = self.chart.add(candle)
        if self.chart.is_ready:
            if self.online_check is True and self.chart.is_online is False:
                return
            position = await self._handle(candle, sig)
            if position is not None:
                self.save_chart(position)

    def save_chart(self, position: Position) -> None:
        start_price = round(position.orders[0].price, 2)
        avg_price = round(position.avg_price, 2)
        loss = round((avg_price - start_price) / start_price * 100, 2)
        fig = self.chart.make_figure(
            f"start={start_price} avg={avg_price} loss={loss} "
            f"duration={position.duration} profit={round(position.profit, 2)}",
            self.symbol,
            position.orders[0].time - timedelta(days=1),
        )
        params = {"row": 1, "col": 1, "line_dash": "dash", "line_width": 1}
        for order in position.orders:
            color = "red" if order.side == OrderSide.BUY else "green"
            fig.add_hline(y=order.price, line_color=color, **params)
        fig.add_hline(y=position.avg_price, line_color="blue", **params)
        fig.add_vline(x=position.orders[0].time, line_color="green", **params)

        pattern = '%Y.%m.%d-%H.%M.%S'
        file_name = f"{position.orders[0].time.strftime(pattern)}-deal.jpg"
        with Path(file_name).open("wb") as f:
            f.write(fig.to_image("jpeg", width=1050, height=750, scale=2))

    async def _handle(self, candle: Candle, sig: Signal) -> Position | None:
        raise NotImplementedError("Please implement _handle method")
