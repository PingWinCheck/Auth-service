import secrets
from datetime import timedelta

from pwdlib import PasswordHash
from typing import TYPE_CHECKING, Type

from core.kafka_producer import kafka_producer, ConfirmMail
from core.redis_con import redis
from custom_auth import CustomUser
from custom_auth.documents import UserDoc
from custom_auth.exceptions import (
    UserAlreadyExistsException,
    TokenInvalidException,
    InvalidLoginOrPasswordException,
    UserDoesNotExistsException,
)
from core.logger import get_logger
from custom_auth.schemas import TokenSchema, UserLoginSchema, UserBaseSchema
from custom_auth.utils import TokenGenerator

log = get_logger(__name__)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from custom_auth.dao import CustomUserDAO

password_manager = PasswordHash.recommended()


class UserManager:
    def __init__(self, session: "AsyncSession", dao: "Type[CustomUserDAO]"):
        self._session = session
        self._dao = dao

    async def create(self, **kwargs) -> UserDoc | None:
        """
        Проверяет наличие пользователя в postgres, если уже существует, выбрасывает исключение UserAlreadyExistsException.
        Хэширует password, генерирует токен.
        Сохраняет результат в mongo.
        Отправляет в kafka для дальнейшей обработки.
        :param kwargs:
        :return:
        """
        user = await self._dao.get_by_email(
            session=self._session, email=kwargs["email"]
        )
        if user:
            raise UserAlreadyExistsException("Пользователь уже существует")
        password = kwargs.pop("password")
        kwargs["password_hash"] = password_manager.hash(password)

        kwargs["token"] = secrets.token_urlsafe(64)
        user_doc = await UserDoc(**kwargs).insert()
        confirm_mail = ConfirmMail.model_validate(user_doc.model_dump())
        await kafka_producer(topic="send-mail", send_message_model=confirm_mail)

        # user = await self._dao.create(session=self._session, **kwargs)
        return user_doc

    async def verify_email_create_user(self, token: str):
        """
        поиск в mongo пользователя по токену, если токен не найден выбрасывает исключение TokenInvalidException.
        если токен найден, проверяем существует ли такой пользователь в основной бд, если нет, то создаем нового пользователя
        иначе выбрасываем исключение UserAlreadyExistsException
        удаляем запись из mongo с текущим токеном
        :param token:
        :return:
        """
        user_doc = await UserDoc.find_one({"token": token})
        if user_doc is None:
            raise TokenInvalidException("Token invalid")
        dump = user_doc.model_dump()
        dump.pop("token", None)
        dump.pop("id", None)
        user = await self._dao.get_by_email(session=self._session, email=dump["email"])
        if user:
            raise UserAlreadyExistsException
        user = await self._dao.create(session=self._session, **dump)
        await user_doc.delete()
        log.info("User verified email: %r and created db", dump["email"])
        return user

    async def login(self, credentials: UserLoginSchema) -> TokenSchema:
        user = await self._dao.get_by_email(self._session, credentials.email)
        if user is None:
            raise InvalidLoginOrPasswordException
        if not password_manager.verify(credentials.password, user.password_hash):
            raise InvalidLoginOrPasswordException
        payload = {"sub": str(user.id), "email": user.email}
        return TokenGenerator().create_access_refresh_tokens_pair(payload)

    async def reset_password(self, credentials: UserBaseSchema):
        user = await self._dao.get_by_email(self._session, credentials.email)
        if user is None:
            raise UserDoesNotExistsException(
                f"Пользователя с почтой: {credentials.email} не существует"
            )
        token = secrets.token_urlsafe(64)
        await redis.set(token, credentials.email, ex=timedelta(minutes=15))
        return token

    async def reset_password_with_token(self, token: str) -> str:
        email = await redis.get(token)
        if email is None:
            raise TokenInvalidException("Указанный токен не существует, либо истёк")
        return email

    async def reset_password_with_token_new_password(
        self, token: str, password: str
    ) -> CustomUser:
        email = await self.reset_password_with_token(token=token)
        user = await self._dao.get_by_email(session=self._session, email=email)
        if user is None:
            raise UserDoesNotExistsException("Пользователя не существует")
        user.password_hash = password_manager.hash(password)
        await self._session.commit()
        await self._session.refresh(user)
        await redis.delete(token)
        return user
