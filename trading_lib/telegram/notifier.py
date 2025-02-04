import plotly.graph_objects as go
from common.notifier import BaseNotifier
from telegram.client import TelegramClient


class TelegramNotifier(BaseNotifier):
    def __init__(self, tg_client: TelegramClient) -> None:
        self.tg_client = tg_client

    async def push_text(self, text: str) -> None:
        await self.tg_client.send_debug(text)

    async def push_figure(self, fig: go.Figure, _name: str) -> None:
        await self.tg_client.send_photo(fig.to_image("jpeg", width=1050, height=750, scale=2))
