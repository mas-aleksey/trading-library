import asyncio
import json
import logging
import uuid
from time import monotonic
from typing import Generic, TypeVar

import backoff
from aiohttp import (
    ClientConnectionError,
    ClientResponse,
    ClientSession,
    ClientTimeout,
    ContentTypeError,
)
from core.exceptions import BaseAppError, BaseClientError
from core.settings import BaseClientConfig, get_settings
from pydantic import BaseModel, ValidationError


settings = get_settings()

T_SCHEMA = TypeVar("T_SCHEMA", bound=BaseModel)
T_CONFIG = TypeVar("T_CONFIG", bound=BaseClientConfig)


class Response(BaseModel):
    headers: dict
    body: str | dict | None = None


class BaseClient(Generic[T_CONFIG]):

    def __init__(self, config: T_CONFIG):
        self._config = config
        self.logger = logging.getLogger(self.name)
        self.session = ClientSession(timeout=ClientTimeout(total=settings.CLIENT_TIMEOUT))

    @property
    def config(self) -> T_CONFIG:
        return self._config

    async def __aenter__(self) -> "BaseClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: ANN001
        await self.stop()

    async def stop(self) -> None:
        await self.session.close()

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def base_path(self) -> str:
        return self.config.HOST.strip("/")

    def get_path(self, url: str) -> str:
        url = url.lstrip("/")
        return f"{self.base_path}/{url}"

    @staticmethod
    def load_schema(data: dict, schema: type[T_SCHEMA]) -> T_SCHEMA:
        try:
            return schema.model_validate(data)
        except (TypeError, ValidationError) as exc:
            raise BaseAppError(
                f"ValidationError in schema '{schema.__name__}': {str(exc)}. Data: {data}"
            ) from exc

    @staticmethod
    async def _raise_for_status(resp: ClientResponse) -> None:
        # good statuses -> return
        if resp.status in (200, 201, 202, 204):
            return

        content = await resp.text()
        error_msg = str(resp).replace("\n", " ")

        # client exceptions -> raise up
        if 400 <= resp.status < 500:
            raise BaseAppError(error_msg, content)

        # other unhandled exceptions -> retry (backoff)
        raise BaseClientError(error_msg, content)

    async def _handle_response(self, resp: ClientResponse, request_info: dict) -> Response:
        await self._raise_for_status(resp)
        response = Response(headers=resp.headers)

        if resp.status == 204:
            return response

        try:
            body = await resp.json(content_type=resp.content_type)
            self.logger.debug(
                "Response: '%s' request_info: %s, data: %s",
                resp.content_type,
                request_info,
                body,
            )
            response.body = body
        except (json.decoder.JSONDecodeError, ContentTypeError) as exc:
            error_msg = "Response JSONDecodeError: %s content_type: %s, request_info: %s" % (
                exc,
                resp.content_type,
                request_info,
            )
            self.logger.error(error_msg)
            raise BaseClientError(f"{self.name} error", error_msg) from exc
        else:
            return response

    @backoff.on_exception(
        backoff.expo,
        (ClientConnectionError, BaseClientError),
        max_tries=settings.MAX_RETRY,
    )
    async def _perform_request(self, method: str, url: str, **kwargs) -> Response:
        kwargs.setdefault("ssl", False)
        start_time = monotonic()
        status_code = 500
        request_info = {
            "method": method.upper(),
            "request_id": str(uuid.uuid4()),
            "url": url,
        }
        try:
            self.logger.debug("Request: %s", request_info)
            async with self.session.request(method, url, **kwargs) as resp:
                status_code = resp.status
                return await self._handle_response(resp, request_info)
        except asyncio.TimeoutError as exc:
            self.logger.error("TimeoutError request_info: %s", request_info)
            raise BaseClientError("TimeoutError", request_info) from exc
        except Exception as exc:
            self.logger.exception(
                "Request error [%s]: %s request_info: %s",
                status_code,
                str(exc),
                request_info,
            )
            raise
        finally:
            elapsed = 1000.0 * (monotonic() - start_time)
            duration = "{:0.3f} ms".format(elapsed)
            self.logger.info("Response: [%s] Duration: %s: %s", status_code, duration, request_info)
