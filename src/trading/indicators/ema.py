from dataclasses import dataclass

import pandas as pd
import plotly.graph_objects as go
from trading.indicators.base import BaseIndicator, Signal


@dataclass
class TripleEma(BaseIndicator):
    fast_period: int = 20
    medium_period: int = 100
    slow_period: int = 300

    def __str__(self) -> str:
        return f"EMA({self.fast_period}, {self.medium_period}, {self.slow_period})"

    @property
    def fast_key(self) -> str:
        return f"Ema_{self.fast_period}"

    @property
    def medium_key(self) -> str:
        return f"Ema_{self.medium_period}"

    @property
    def slow_key(self) -> str:
        return f"Ema_{self.slow_period}"

    def _calculate(self, last_data: dict, price: float) -> dict:
        return {
            self.fast_key: self.calc_ema(
                last_data.get(self.fast_key, price), self.fast_period, price
            ),
            self.medium_key: self.calc_ema(
                last_data.get(self.medium_key, price), self.medium_period, price
            ),
            self.slow_key: self.calc_ema(
                last_data.get(self.slow_key, price), self.slow_period, price
            ),
        }

    def signal(self, last_data: dict) -> Signal:
        if last_data[self.slow_key] > last_data[self.medium_key] > last_data[self.fast_key]:
            return Signal.BUY
        if last_data[self.slow_key] < last_data[self.medium_key] < last_data[self.fast_key]:
            return Signal.SELL
        return Signal.NONE

    def add_trace(self, figure: go.Figure, chart_df: pd.DataFrame) -> None:
        figure.add_trace(
            go.Scatter(
                x=chart_df["time"],
                y=chart_df[self.fast_key],
                mode="lines",
                name=self.fast_key,
                line={"color": "green", "width": 2},
            ),
            row=1,
            col=1,
        )
        figure.add_trace(
            go.Scatter(
                x=chart_df["time"],
                y=chart_df[self.medium_key],
                mode="lines",
                name=self.medium_key,
                line={"color": "orange", "width": 2},
            ),
            row=1,
            col=1,
        )
        figure.add_trace(
            go.Scatter(
                x=chart_df["time"],
                y=chart_df[self.slow_key],
                mode="lines",
                name=self.slow_key,
                line={"color": "red", "width": 2},
            ),
            row=1,
            col=1,
        )
