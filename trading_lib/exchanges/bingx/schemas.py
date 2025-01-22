from datetime import datetime
from typing import Generic, TypeVar

from common.schemas import OrderSide
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BingXResponse(BaseModel, Generic[T]):
    code: int
    data: T
    msg: str | None = None


class BingXBalance(BaseModel):
    asset: str
    free: float
    locked: float


class BingXBalances(BaseModel):
    balances: list[BingXBalance]

    def free_for_asset(self, asset: str) -> float:
        for balance in self.balances:
            if balance.asset == asset:
                return balance.free
        return 0


class BingXOrderOut(BaseModel):
    symbol: str
    orderId: int
    transactTime: datetime
    price: float
    origQty: float
    executedQty: float
    cummulativeQuoteQty: float
    status: str
    type: str
    side: OrderSide
    clientOrderID: str | None


class BingXOrderData(BaseModel):
    order: BingXOrderOut


class BingXCandleResponse(BingXResponse[list[list]]):
    pass


class BingXBalancesResponse(BingXResponse[BingXBalances]):
    pass


class BingXOrderResponse(BingXResponse[BingXOrderData]):
    pass
