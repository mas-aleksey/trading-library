from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


class DatabaseConnector:

    def __init__(
        self,
        db_url: str,
        max_idle_conns: int = 2,
        max_open_conn: int = 16,
    ):
        self._engine = create_async_engine(
            db_url,
            pool_size=max_idle_conns,
            max_overflow=max_open_conn,
            pool_pre_ping=True,
            isolation_level="AUTOCOMMIT",
        )

    @property
    def session_maker(self) -> async_sessionmaker:
        return async_sessionmaker(bind=self._engine)

    async def disconnect(self) -> None:
        await self._engine.dispose()
