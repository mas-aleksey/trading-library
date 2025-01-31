from async_client import ClientConfig


class TelegramConfig(ClientConfig):
    TOKEN: str
    DEBUG_CHAT_ID: int
    INFO_CHAT_ID: int
    ENABLED: bool = True

    class Config:
        env_prefix = "TELEGRAM_"
