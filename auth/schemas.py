import uuid
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    username: Annotated[str, Field(min_length=3)]
    email: EmailStr
    id: UUID = uuid.uuid4()


class UserCreate(UserBase):
    password: Annotated[str, Field(min_length=8)]
