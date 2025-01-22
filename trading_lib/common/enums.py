from enum import Enum, StrEnum


class Signal(Enum):
    NONE = 0
    BUY = 1
    SELL = 2


class OrderSide(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class ExchangeType(StrEnum):
    BINGX = "BingXExchange"
    CSV = "CSVExchange"


class IndicatorType(StrEnum):
    TRIPLE_EMA = "TripleEma"
    RSI = "RSI"
