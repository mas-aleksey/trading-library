from pydantic import BaseModel, Field

# params = {
#     "exchange": {
#         "class": "BingXExchange",
#         "params": {
#             "symbol": "ETH",
#             "timeframe": 1,
#         },
#     },
#     "chart": {
#         "size": 100,
#         "indicators": [
#             {
#                 "class": "TripleEma",
#                 "params": {
#                     "fast_period": 39,
#                     "medium_period": 50,
#                     "slow_period": 91,
#                 },
#             },
#             {
#                 "class": "RSI",
#                 "params": {
#                     "period": 15,
#                     "ema_period": 5,
#                     "zone": 20,
#                     "use_for_sell": True,
#                 },
#             },
#         ],
#     },
#     "order_params": {"avg_rate": -0.38, "min_cost": 220, "increase": 1.15},
# }


class ClassParams(BaseModel):
    class_: str = Field(alias="class")
    params: dict


class ChartParams(BaseModel):
    size: int
    indicators: list[ClassParams]


class WorkerParams(BaseModel):
    exchange: ClassParams
    chart: ChartParams
    order_params: dict
