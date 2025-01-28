from pydantic_settings import BaseSettings


class CSVConfig(BaseSettings):
    PATH: str
    INITIAL_BALANCE: float = 10000

    class Config:
        env_prefix = "CSV_"
