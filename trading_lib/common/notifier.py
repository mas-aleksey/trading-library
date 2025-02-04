from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import plotly.graph_objects as go
from common.chart import Chart
from common.enums import OrderSide, Signal
from common.schemas import Candle, Position


class BaseNotifier:

    async def push_text(self, text: str) -> None:
        raise NotImplementedError

    async def push_figure(self, fig: go.Figure, name: str) -> None:
        raise NotImplementedError


class DummyNotifier(BaseNotifier):
    def __init__(self, path: str) -> None:
        self.path = path

    async def push_text(self, text: str) -> None:
        pass

    async def push_figure(self, fig: go.Figure, name: str) -> None:
        print("save chart", name)  # noqa: T201
        file_name = f"{self.path}/{name}.jpg"
        with Path(file_name).open("wb") as f:
            f.write(fig.to_image("jpeg", width=1050, height=750, scale=2))


@dataclass
class NotifyService:
    client: BaseNotifier
    need_send_position: bool = True
    need_send_signal: bool = True
    need_send_after_sell: bool = True
    last_signal_chart_dt: datetime | None = None
    sell_dt: datetime | None = None
    avg_price: float | None = None

    async def send_text(self, text: str) -> None:
        await self.client.push_text(text)

    async def send_chart(self, chart: Chart, _sig: Signal, _candle: Candle, symbol: str) -> None:
        # await self.send_signal(chart, sig, candle, symbol)
        await self.send_after_sell(chart, symbol)

    async def send_position(self, chart: Chart, position: Position, symbol: str) -> None:
        if self.need_send_position is False:
            return
        start_price = round(position.orders[0].price, 2)
        avg_price = round(position.avg_price, 2)
        loss = round((avg_price - start_price) / start_price * 100, 2)
        min_val, min_dt = chart.find_min(position.orders[0].time, position.orders[-1].time)
        min_loss = round((min_val - start_price) / start_price * 100, 2)
        fig = chart.make_figure(
            f"start={start_price} avg={avg_price} min={min_val} loss={loss} min_loss={min_loss} "
            f"duration={position.duration} profit={round(position.profit, 2)}",
            symbol,
            position.orders[0].time - timedelta(days=1),
        )
        params = {"row": 1, "col": 1, "line_dash": "dash", "line_width": 1}
        for order in position.orders:
            color = "red" if order.side == OrderSide.BUY else "green"
            fig.add_hline(y=order.price, line_color=color, **params)
        fig.add_hline(y=position.avg_price, line_color="blue", **params)
        fig.add_vline(x=position.orders[0].time, line_color="green", **params)

        fig.add_hline(y=min_val, line_color="blue", **params)
        await self.client.push_figure(fig, f"{position.orders[0].time.isoformat()}-deal")
        self.sell_dt = position.orders[-1].time + timedelta(minutes=30)
        self.avg_price = position.avg_price

    async def send_signal(self, chart: Chart, sig: Signal, candle: Candle, symbol: str) -> None:
        if self.need_send_signal is False:
            return
        if sig in (Signal.SELL, Signal.NONE):
            return
        if (
            self.last_signal_chart_dt is not None
            and self.last_signal_chart_dt + timedelta(minutes=10) > datetime.now().astimezone()
        ):
            return
        fig = chart.make_figure(f"{sig} {candle.close}", symbol, candle.time - timedelta(days=1))
        await self.client.push_figure(fig, f"{candle.time.isoformat()}-{sig}")
        self.last_signal_chart_dt = candle.time

    async def send_after_sell(self, chart: Chart, symbol: str) -> None:
        if self.need_send_after_sell is False:
            return
        if self.sell_dt is not None and self.sell_dt + timedelta(minutes=30) < datetime.now(
            tz=timezone.utc
        ):
            params = {"row": 1, "col": 1, "line_dash": "dash", "line_width": 1}
            max_value, max_value_time = chart.find_max(self.sell_dt)
            gain_rate = round((max_value - self.avg_price) / self.avg_price * 100, 2)
            fig = chart.make_figure(f"{gain_rate=}", symbol, self.sell_dt - timedelta(days=1))
            fig.add_hline(y=self.avg_price, line_color="blue", **params)
            fig.add_hline(y=max_value, line_color="green", **params)
            await self.client.push_figure(fig, f"{self.sell_dt.isoformat()}+60")
            self.sell_dt = None
