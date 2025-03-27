import secrets

from pwdlib import PasswordHash
from typing import TYPE_CHECKING, Type

from custom_auth.documents import UserDoc
from custom_auth.exceptions import UserAlreadyExistsException, TokenInvalidException

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from custom_auth.dao import CustomUserDAO

password_manager = PasswordHash.recommended()


class UserManager:
    def __init__(self, session: "AsyncSession", dao: "Type[CustomUserDAO]"):
        self._session = session
        self._dao = dao

    async def create(self, **kwargs) -> UserDoc | None:
        user = await self._dao.get_by_email(
            session=self._session, email=kwargs["email"]
        )
        if user:
            raise UserAlreadyExistsException("Пользователь уже существует")
        password = kwargs.pop("password")
        kwargs["password_hash"] = password_manager.hash(password)

        kwargs["token"] = secrets.token_urlsafe(64)
        user_doc = await UserDoc(**kwargs).insert()

        # user = await self._dao.create(session=self._session, **kwargs)
        return user_doc

    async def verify_email_create_user(self, token: str):
        user_doc = await UserDoc.find_one({"token": token})
        if user_doc is None:
            raise TokenInvalidException
        dump = user_doc.model_dump()
        dump.pop("token", None)
        dump.pop("id", None)
        user = await self._dao.get_by_email(session=self._session, email=dump["email"])
        if user:
            raise UserAlreadyExistsException
        user = await self._dao.create(session=self._session, **dump)
        await user_doc.delete()
        return user
