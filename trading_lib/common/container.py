import asyncio

from common.exchange import ExchangeFactory
from common.puller import Puller
from config import Settings
from db.db_connector import DatabaseConnector
from telegram.client import TelegramClient


class Container:
    def __init__(self, settings: Settings, loop: asyncio.AbstractEventLoop = None) -> None:
        self._settings = settings
        self._loop = loop or asyncio.get_event_loop()
        self._db = None
        self._tg_client: TelegramClient | None = None
        self._exchange_fabric: ExchangeFactory | None = None
        self._puller: Puller | None = None

    @property
    def db(self) -> DatabaseConnector:
        if self._db is None:
            self._db = DatabaseConnector(self._settings.DB.asyncpg_url)
        return self._db

    @property
    def tg_client(self) -> TelegramClient:
        if self._tg_client is None:
            self._tg_client = TelegramClient(self._settings.TELEGRAM)
        return self._tg_client

    @property
    def exchange_fabric(self) -> ExchangeFactory:
        if self._exchange_fabric is None:
            self._exchange_fabric = ExchangeFactory(self._settings)
        return self._exchange_fabric

    @property
    def puller(self) -> Puller:
        if self._puller is None:
            self._puller = Puller()
        return self._puller

    async def stop(self) -> None:
        if self._db is not None:
            await self._db.disconnect()
        self._db = None

        if self._tg_client is not None:
            await self._tg_client.stop()
        self._tg_client = None

        if self._exchange_fabric is not None:
            await self._exchange_fabric.stop()
        self._exchange_fabric = None

        if self._puller is not None:
            await self._puller.stop()
        self._puller = None
