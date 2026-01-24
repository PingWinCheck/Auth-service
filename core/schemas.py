from pydantic import BaseModel, EmailStr


class BadResponse(BaseModel):
    detail: str


class MailSchema(BaseModel):
    recipient: EmailStr
    msg: str
    subject: str
