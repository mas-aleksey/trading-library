import asyncio

from common.woker import Strategy, WorkerManager

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


async def main() -> None:
    wm = WorkerManager()
    await wm.start([STRATEGY])
    await asyncio.sleep(15)
    await wm.stop()
    fig = wm._workers[0].strategy.chart.make_figure("Test Figure", "BTC-USD")
    fig.show()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
