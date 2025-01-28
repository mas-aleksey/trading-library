from pydantic import BaseModel


class TelegramSendResponse(BaseModel):
    ok: bool
    result: dict | None
