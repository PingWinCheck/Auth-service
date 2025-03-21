import uuid
from typing import Annotated

from pydantic import BaseModel, Field, EmailStr
from fastapi_users import schemas


class UserBaseSchema(BaseModel):
    username: Annotated[str, Field(min_length=3)]
    email: EmailStr


class UserCreateSchema(UserBaseSchema):
    password: Annotated[str, Field(min_length=8)]


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass
