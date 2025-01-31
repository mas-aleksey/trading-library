import logging
from typing import BinaryIO

from async_client import BaseClient
from common.exceptions import BaseClientError
from telegram.config import TelegramConfig
from telegram.schemas import TelegramSendResponse

logger = logging.getLogger("TelegramClient")


class TelegramClient(BaseClient[TelegramConfig]):

    def get_path(self, url: str) -> str:
        return f"{self.base_path}/bot{self.config.TOKEN}/{url}"

    async def _send(self, path: str, **kwargs) -> None:
        if self.config.ENABLED is False:
            logger.info("Skip sending to Telegram")
            return
        resp = await self._perform_request("POST", self.get_path(path), **kwargs)
        data = self.load_schema(resp.body, TelegramSendResponse)
        if not data.ok:
            self.logger.error(f"Telegram error: {resp.body}")
            raise BaseClientError(extra=f"Telegram error: {resp.body}")

    async def send_info(self, message: str) -> None:
        payload = {"chat_id": self.config.INFO_CHAT_ID, "text": message}
        await self._send("sendMessage", json=payload)

    async def send_debug(self, message: str) -> None:
        payload = {"chat_id": self.config.DEBUG_CHAT_ID, "text": message}
        await self._send("sendMessage", json=payload)

    async def send_photo(self, photo: BinaryIO | bytes) -> None:
        """
        :param photo: BinaryIO object
        :return: None
        """
        params = {"chat_id": self.config.DEBUG_CHAT_ID}
        data = {"photo": photo}
        await self._send("sendPhoto", params=params, data=data)
