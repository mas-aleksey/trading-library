from dataclasses import dataclass

import pandas as pd
import plotly.graph_objects as go
from common.enums import Signal
from common.indicators import BaseIndicator


@dataclass
class RSI(BaseIndicator):
    period: int = 14
    ema_period: int = 7
    zone: int = 30

    def __str__(self) -> str:
        return f"RSI({self.period}, ema: {self.ema_period}, zone: {self.zone}, {self.use_for_sell})"

    def _calculate(self, last_data: dict, price: float) -> dict:
        diff = price - last_data.get("close", price)
        gain = diff if diff > 0 else 0
        loss = -diff if diff < 0 else 0

        avg_gain = (last_data.get("avg_gain", gain) * (self.period - 1) + gain) / self.period
        avg_loss = (last_data.get("avg_loss", loss) * (self.period - 1) + loss) / self.period

        rs = avg_gain / (avg_loss + 0.0001)
        rsi = 100 - (100 / (1 + rs))
        last_ema_rsi = last_data.get(f"RSI_ema_{self.period}", rsi)
        return {
            "avg_gain": avg_gain,
            "avg_loss": avg_loss,
            f"RSI_{self.period}": rsi,
            f"RSI_ema_{self.period}": self.calc_ema(last_ema_rsi, self.ema_period, rsi),
        }

    def signal(self, last_data: dict) -> Signal:
        key = f"RSI_ema_{self.period}"
        if key not in last_data:
            return Signal.NONE
        if last_data[key] < self.zone:
            return Signal.BUY
        if last_data[key] > 100 - self.zone:
            return Signal.SELL
        return Signal.NONE

    def add_trace(
        self, figure: go.Figure, chart_df: pd.DataFrame, row: int = 2, col: int = 1
    ) -> None:
        for key in [f"RSI_{self.period}", f"RSI_ema_{self.period}"]:
            figure.add_trace(
                go.Scatter(
                    x=chart_df["time"],
                    y=chart_df[key],
                    mode="lines",
                    name=key,
                ),
                row=row,
                col=col,
            )
        params = {
            "line_width": 1,
            "line_dash": "dash",
            "line_color": "black",
            "row": row,
            "col": col,
        }
        figure.add_hline(y=self.zone, **params)
        figure.add_hline(y=50, **params)
        figure.add_hline(y=100 - self.zone, **params)
