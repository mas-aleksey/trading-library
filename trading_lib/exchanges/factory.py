from common.enums import ExchangeType
from common.exchange import BaseExchange
from config import Settings
from exchanges.bingx.exchange import BingXExchange
from exchanges.local.exchange import CSVExchange


class ExchangeFactory:
    EXCHANGES = {
        ExchangeType.BINGX: "_bingx_exchange",
        ExchangeType.CSV: "_csv_exchange",
    }

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self.__bingx_exchange: BingXExchange | None = None
        self.__csv_exchange: CSVExchange | None = None

    @property
    def _bingx_exchange(self) -> BingXExchange:
        if self.__bingx_exchange is None:
            self.__bingx_exchange = BingXExchange(self._settings.BINGX)
        return self.__bingx_exchange

    @property
    def _csv_exchange(self) -> CSVExchange:
        if self.__csv_exchange is None:
            self.__csv_exchange = CSVExchange(self._settings.CSV)
        return self.__csv_exchange

    def get(self, exchange_type: ExchangeType) -> BaseExchange:
        return getattr(self, self.EXCHANGES[exchange_type])

    async def stop(self) -> None:
        if self.__bingx_exchange is not None:
            await self.__bingx_exchange.stop()
        if self.__csv_exchange is not None:
            await self.__csv_exchange.stop()
