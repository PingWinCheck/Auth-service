from pydantic import BaseModel


class BadResponse(BaseModel):
    detail: str
