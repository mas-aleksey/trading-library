from typing import Any


class BaseAppError(Exception):
    """Base class for all exceptions in application"""

    default_msg = "Unknown error"

    def __init__(self, message: str | None = None, extra: Any = None) -> None:
        self.message = message or self.default_msg
        if extra:
            self.message = f"{self.message}, info: {extra}"

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return self.message


class BaseClientError(BaseAppError):
    default_msg = "Client error"
