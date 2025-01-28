from async_client import ClientConfig


class BingXConfig(ClientConfig):
    API_KEY: str
    SECRET_KEY: str

    class Config:
        env_prefix = "BINGX_"
