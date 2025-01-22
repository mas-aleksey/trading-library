import asyncio
import uuid
from pathlib import Path

from common.chart import Chart
from common.params import WorkerParams
from common.woker import Strategy
from exchanges.local.config import CSVConfig
from exchanges.local.exchange import CSVExchange
from strategies.example import ExampleStrategy

STRATEGY = Strategy(
    name="KnifeStrategy",
    params={
        "symbol": "ETH",
        "pull_interval": 5,
        "exchange": "CSVExchange",
        "chart": {
            "size": 900,
            "timeframe": 1,
            "indicators": [
                {
                    "class": "TripleEma",
                    "params": {},
                },
                {
                    "class": "RSI",
                    "params": {},
                },
            ],
        },
        "strategy": {
            "class": "KnifeStrategy",
            "params": {
                "take_profit": 0.5,
                "orders_map": [(0, 0.1), (2, 0.2), (5, 0.3), (8, 0.4)],
            },
        },
    },
)

DATA_DIR = Path(__file__).parent.parent / "data"
FILE_PATH = DATA_DIR / "test.csv"


async def main(task: Strategy) -> None:
    params = WorkerParams.model_validate(task.params)
    params.pull_interval = 0
    exchange = CSVExchange(CSVConfig(PATH=FILE_PATH.as_posix()))
    strategy = ExampleStrategy(
        strategy_id=uuid.uuid4(),
        symbol=params.symbol,
        chart=Chart.new(params.chart),
        exchange=exchange,
        online_check=False,
        **params.strategy.params,
    )
    async for candle in exchange.get_candles(params.symbol):
        candle.time = candle.time.astimezone()
        await strategy.handle(candle)
    if strategy.position:
        pos = await strategy.close_position(candle)
        strategy.save_chart(pos)
    print(await strategy.exchange.get_balance(""))  # noqa: T201


if __name__ == "__main__":
    asyncio.run(main(STRATEGY))
