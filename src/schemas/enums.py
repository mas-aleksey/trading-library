from enum import StrEnum


class StrategyType(StrEnum):
    KNIFE = "KnifeStrategy"


class ExchangeType(StrEnum):
    BINGX = "BingXExchange"
    CSV = "CSVExchange"


class IndicatorType(StrEnum):
    TRIPLE_EMA = "TripleEma"
    RSI = "RSI"
