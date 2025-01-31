from pydantic_settings import BaseSettings


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
