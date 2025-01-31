import asyncio
import logging
import uuid
from typing import Any, Dict, List

from common.chart import Chart
from common.params import WorkerParams
from common.puller import Puller
from common.schemas import Candle
from exchanges.bingx.config import BingXConfig
from exchanges.bingx.exchange import BingXExchange
from pydantic import BaseModel
from strategies.base import BaseStrategy
from strategies.example import ExampleStrategy


class Strategy(BaseModel):
    name: str
    params: Dict[str, Any]


class Worker:

    def __init__(self, name: str, strategy: BaseStrategy) -> None:
        self.name = name
        self.strategy = strategy
        self.logger = logging.getLogger(name)
        self.running = True

    async def stop(self) -> None:
        self.running = False
        await self.log("stop")

    async def loop(self, queue: asyncio.Queue) -> None:
        await self.log("Run streaming")
        while self.running:
            try:
                candle: Candle = await queue.get()
                candle.time = candle.time.astimezone()
                await self.strategy.handle(candle)
            except Exception as e:
                await self.log(f"{type(e).__name__}: {e}", level="exception")
        await self.log("Stop streaming")

    async def log(self, msg: str, level: str = "info") -> None:
        getattr(self.logger, level)(msg)


class WorkerManager:
    def __init__(self) -> None:
        self._workers: list[Worker] = []
        self._tasks = []
        self.puller = Puller()
        self.logger = logging.getLogger(self.__class__.__name__)

    async def start(self, worker_tasks: List[Strategy]) -> None:
        self.logger.info("Prepare workers...")

        for worker_task in worker_tasks:
            params = WorkerParams.parse_obj(worker_task.params)
            exchange = BingXExchange(config=BingXConfig())
            strategy = ExampleStrategy(
                strategy_id=uuid.uuid4(),
                symbol=params.symbol,
                chart=Chart.new(params.chart),
                exchange=exchange,
                online_check=True,
                **params.strategy.params,
            )
            queue = self.puller.subscribe(exchange, params.symbol, params.pull_interval)
            worker = Worker(worker_task.name, strategy)
            self._tasks.append(asyncio.create_task(worker.loop(queue)))
            self._workers.append(worker)

        await self.puller.start()
        self.logger.info(f"Running {len(self._workers)} workers")

    async def stop(self) -> None:
        self.logger.info(f"Stopping {len(self._workers)} workers")
        await asyncio.gather(*[worker.stop() for worker in self._workers])

        self.logger.info(f"Stopping {len(self._tasks)} tasks")
        await asyncio.gather(*self._tasks)

        self.logger.info("Worker Manager is stopped")
