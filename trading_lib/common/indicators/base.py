from dataclasses import dataclass
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
from common.enums import Signal


@dataclass
class BaseIndicator:
    use_for_buy: bool = True
    use_for_sell: bool = True

    def __str__(self) -> str:
        return str(self.__dict__)

    def _calculate(self, last_data: dict, price: float) -> dict:
        raise NotImplementedError("Please implement '_calculate' method")

    @staticmethod
    def calc_ema(prev_ema: float, period: int, new_value: float) -> float:
        prev_ema = prev_ema or new_value
        k = 2 / (period + 1)
        return (new_value - prev_ema) * k + prev_ema

    def new_data(self, time_series: list[datetime], data: dict, price: float) -> dict:
        last_data = data[time_series[-1]] if data else {}
        return self._calculate(last_data, price)

    def update_last(self, time_series: list[datetime], data: dict, price: float) -> dict:
        last_data = data[time_series[-2]]
        return self._calculate(last_data, price)

    def signal(self, last_data: dict) -> Signal:
        raise NotImplementedError("Please implement 'signal' method")

    def add_trace(self, figure: go.Figure, chart_df: pd.DataFrame) -> None:
        raise NotImplementedError("Please implement 'add_trace' method")
