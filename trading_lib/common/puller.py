import asyncio
import logging
from dataclasses import dataclass

from common.exchange import BaseExchange


@dataclass
class Subscribe:
    exchange: BaseExchange
    symbol: str
    queues: list[asyncio.Queue]
    pull_interval: int

    @property
    def info(self) -> str:
        return f"exchange={type(self.exchange).__name__} {self.symbol=} {self.pull_interval=}"


class Puller:

    def __init__(self) -> None:
        self._logger = logging.getLogger("[Poller]")
        self._subscribes: dict[str, Subscribe] = {}
        self._tasks: list[asyncio.Task] = []
        self._running = True

    def subscribe(self, exchange: BaseExchange, symbol: str, pull_interval: int) -> asyncio.Queue:
        key = f"{type(exchange).__name__}-{symbol}-{pull_interval}"
        queue = asyncio.Queue()
        if key not in self._subscribes:
            self._subscribes[key] = Subscribe(
                exchange=exchange,
                symbol=symbol,
                queues=[queue],
                pull_interval=pull_interval,
            )
        else:
            self._subscribes[key].queues.append(queue)
        self._logger.info(f"Subscribed: {self._subscribes[key].info}")
        return queue

    async def _loop(self, stat: Subscribe) -> None:
        self._logger.info(f"Start pulling {stat.info}")
        while self._running:
            try:
                async for candle in stat.exchange.get_candles(stat.symbol):
                    await asyncio.gather(*[queue.put(candle) for queue in stat.queues])
            except Exception as e:
                self._logger.exception(e)
                self._logger.info(f"Error: {e}")
            finally:
                self._logger.info(f"Sleep {stat.pull_interval} seconds")
                await asyncio.sleep(stat.pull_interval)
        self._logger.info(f"Stopped pulling {stat.info}")

    async def start(self) -> None:
        self._running = True
        for stat in self._subscribes.values():
            self._tasks.append(asyncio.create_task(self._loop(stat)))

    async def stop(self) -> None:
        self._running = False
        self._logger.info("Stopping...")
        await asyncio.gather(*self._tasks)
        self._logger.info("Stopped")
