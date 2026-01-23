from pydantic import BaseModel, EmailStr


class BadResponse(BaseModel):
    detail: str


class MailSchema(BaseModel):
    email: EmailStr
    msg: str
