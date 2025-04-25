from typing import Annotated

from pydantic import BaseModel, Field, EmailStr


class UserBaseSchema(BaseModel):
    email: EmailStr


class UserCreateSchema(UserBaseSchema):
    password: Annotated[str, Field(min_length=8)]


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'Bearer'