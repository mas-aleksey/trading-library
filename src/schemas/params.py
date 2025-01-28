from enum import StrEnum
from typing import Generic, TypeVar

from pydantic import BaseModel, Field
from schemas.enums import ExchangeType, IndicatorType, StrategyType


T = TypeVar("T", bound=StrEnum)


class ClassParams(BaseModel, Generic[T]):
    class_: T = Field(alias="class")
    params: dict | None


class ChartParams(BaseModel):
    size: int = 100
    timeframe: int = 1
    indicators: list[ClassParams[IndicatorType]] = Field(default_factory=list)
    rows: int = 2
    cols: int = 1


class WorkerParams(BaseModel):
    symbol: str
    exchange: ExchangeType
    chart: ChartParams
    strategy: ClassParams[StrategyType]
    pull_interval: int = 5
