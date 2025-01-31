import logging
from contextlib import asynccontextmanager

from common.container import Container
from common.woker import WorkerManager
from config import get_settings
from fastapi import FastAPI

logger = logging.getLogger("[APP]")


@asynccontextmanager
async def lifespan(_app: FastAPI):  # noqa: ANN201
    logger.info("Starting up")

    container = Container(get_settings())
    wm = WorkerManager(container)
    await wm.start()
    yield

    logger.info("Shutting down")
    await wm.stop()
    await container.stop()


app = FastAPI(
    lifespan=lifespan,
)


@app.get("/")
async def root() -> dict:
    return {"message": "Hello World"}


@app.get("/healthz")
async def health_check() -> dict:
    return {"status": "healthy"}
