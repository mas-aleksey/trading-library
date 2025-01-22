from dataclasses import dataclass, field
from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
from common.enums import Signal
from common.indicators import RSI, BaseIndicator, TripleEma
from common.params import ChartParams
from common.schemas import Candle
from plotly.subplots import make_subplots

INDICATORS = {
    "TripleEma": TripleEma,
    "RSI": RSI,
}


@dataclass
class Chart:
    timeframe: int
    size: int
    indicators: list[BaseIndicator]
    rows: int
    cols: int
    data: dict[datetime, dict] = field(default_factory=dict)
    time_series: list[datetime] = field(default_factory=list)

    @property
    def is_online(self) -> bool:
        if not self.time_series:
            return False
        local_dt = datetime.now().astimezone()
        return local_dt - self.time_series[-1] < timedelta(minutes=self.timeframe)

    def get_delta(self) -> float:
        price_first = self.data[self.time_series[0]].get("close")
        price_last = self.data[self.time_series[-1]].get("close")
        return round((price_last - price_first) / price_first * 100, 2)

    @property
    def is_ready(self) -> bool:
        return len(self.time_series) == self.size

    @classmethod
    def new(cls, params: ChartParams) -> "Chart":
        return cls(
            timeframe=params.timeframe,
            size=params.size,
            indicators=[INDICATORS[i.class_](**i.params) for i in params.indicators],
            rows=params.rows,
            cols=params.cols,
        )

    def add(self, candle: Candle) -> Signal:
        new_data = candle.dict()
        if candle.time not in self.data:
            for indicator in self.indicators:
                upd = indicator.new_data(self.time_series, self.data, candle.close)
                new_data.update(upd)
            self.time_series.append(candle.time)
            if len(self.time_series) > self.size:
                old_time = self.time_series.pop(0)
                self.data.pop(old_time)
            self.data[candle.time] = new_data
        else:
            for indicator in self.indicators:
                upd = indicator.update_last(self.time_series, self.data, candle.close)
                new_data.update(upd)
            self.data[candle.time] = new_data

        return self.get_signal(new_data)

    def get_signal(self, data: dict) -> Signal:
        signals = [(i.signal(data), i) for i in self.indicators]
        buy = all(signal == Signal.BUY for signal, i in signals)  # if i.use_for_buy is True
        sell = all(signal == Signal.SELL for signal, i in signals if i.use_for_sell is True)
        if buy:
            return Signal.BUY
        if sell:
            return Signal.SELL
        return Signal.NONE

    def make_figure(self, caption: str, label: str, from_dt: datetime = None) -> go.Figure:
        from_dt = from_dt or self.time_series[0]
        chart_df = pd.DataFrame.from_records(
            [self.data[t] for t in self.time_series if t >= from_dt]
        )
        figure = make_subplots(
            rows=self.rows,
            cols=self.cols,
            shared_xaxes=True,
            vertical_spacing=0.02,
            row_heights=[0.7, 0.3],
            subplot_titles=(caption,),
        )
        candle_stick = go.Candlestick(
            x=chart_df["time"],
            open=chart_df["open"],
            high=chart_df["high"],
            low=chart_df["low"],
            close=chart_df["close"],
            name=f"{label} ({self.size} bars)",
        )
        figure.add_trace(candle_stick, row=1, col=1)
        figure.update_layout(xaxis_rangeslider_visible=False)
        for indicator in self.indicators:
            indicator.add_trace(figure, chart_df)
        return figure

    def find_min(self, from_time: datetime, to_time: datetime) -> tuple[float, datetime]:
        min_value, min_value_time = None, None
        for t in self.time_series:
            if to_time >= t >= from_time:
                if min_value is None:
                    min_value = self.data[t]["low"]
                    min_value_time = t
                if self.data[t]["low"] < min_value:
                    min_value = self.data[t]["low"]
                    min_value_time = t
        return min_value, min_value_time

    def find_max(self, from_time: datetime) -> tuple[float, datetime]:
        max_value, max_value_time = None, None
        for t in self.time_series:
            if t >= from_time:
                if max_value is None:
                    max_value = self.data[t]["high"]
                    max_value_time = t
                if self.data[t]["high"] > max_value:
                    max_value = self.data[t]["high"]
                    max_value_time = t
        return max_value, max_value_time
