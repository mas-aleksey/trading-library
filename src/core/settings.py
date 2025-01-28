from pydantic_settings import BaseSettings


class BaseClientConfig(BaseSettings):
    HOST: str


class BingXConfig(BaseClientConfig):
    API_KEY: str
    SECRET_KEY: str


class CSVConfig(BaseSettings):
    PATH: str


class TelegramConfig(BaseClientConfig):
    TOKEN: str
    DEBUG_CHAT_ID: int
    INFO_CHAT_ID: int
    ENABLED: bool = True


class DatabaseConfig(BaseSettings):
    HOST: str
    PORT: int
    USERNAME: str
    PASSWORD: str
    NAME: str

    def make_url(self, driver: str) -> str:
        return f"{driver}://{self.USERNAME}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"

    @property
    def asyncpg_url(self) -> str:
        return self.make_url(driver="postgresql+asyncpg")

    @property
    def postgresql_url(self) -> str:
        return self.make_url(driver="postgresql")


class Settings(BaseSettings):
    MAX_RETRY: int = 5
    CLIENT_TIMEOUT: int = 30
    BINGX: BingXConfig | None = None
    CSV: CSVConfig | None = None
    TELEGRAM: TelegramConfig
    DB: DatabaseConfig

    class Config:
        case_sensitive = True
        env_nested_delimiter = "__"


def get_settings() -> Settings:
    return Settings()
