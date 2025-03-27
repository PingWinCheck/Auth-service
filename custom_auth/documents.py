from typing import Annotated

from beanie import Document, Indexed
from pydantic import EmailStr


class UserDoc(Document):
    email: EmailStr
    password_hash: str
    token: Annotated[str, Indexed(unique=True)]
