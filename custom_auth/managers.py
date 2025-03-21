from pwdlib import PasswordHash
from typing import TYPE_CHECKING, Type

from custom_auth.exceptions import UserAlreadyExists

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from custom_auth.dao import CustomUserDAO


class UserManager:
    def __init__(self, session: "AsyncSession", dao: "Type[CustomUserDAO]"):
        self._session = session
        self._dao = dao

    async def create(self, **kwargs):
        user = await self._dao.get_by_email(
            session=self._session, email=kwargs["email"]
        )
        if user:
            raise UserAlreadyExists()
        password = kwargs.pop("password")
        kwargs["password_hash"] = password_manager.hash(password)

        user = await self._dao.create(session=self._session, **kwargs)
        return user


password_manager = PasswordHash.recommended()
