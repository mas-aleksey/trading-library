from db.config import DatabaseConfig
from exchanges.bingx.config import BingXConfig
from exchanges.local.config import CSVConfig
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MAX_RETRY: int = 5
    CLIENT_TIMEOUT: int = 30
    BINGX: BingXConfig | None = None
    CSV: CSVConfig | None = None
    DB: DatabaseConfig

    class Config:
        case_sensitive = True


def get_settings() -> Settings:
    return Settings()
