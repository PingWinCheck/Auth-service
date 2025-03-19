from typing import Annotated

from pydantic import BaseModel, Field, EmailStr


class UserBaseSchema(BaseModel):
    username: Annotated[str, Field(min_length=3)]
    email: EmailStr


class UserCreateSchema(UserBaseSchema):
    password: Annotated[str, Field(min_length=8)]
