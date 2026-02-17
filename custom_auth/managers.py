import secrets
from datetime import timedelta


from pwdlib import PasswordHash
from typing import TYPE_CHECKING, Type

from core.schemas import MailSchema
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
from custom_auth.schemas import (
    TokenSchema,
    UserBaseSchema,
    UserCreateSchema,
    UserDBCreateSchema,
)
from custom_auth.utils import TokenGenerator
from core.faststream import rabbit_router

log = get_logger(__name__)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from custom_auth.dao import CustomUserDAO
    from fastapi.security.oauth2 import OAuth2PasswordRequestForm

password_manager = PasswordHash.recommended()


class UserManager:
    def __init__(self, session: "AsyncSession", dao: "Type[CustomUserDAO]"):
        self._session = session
        self._dao = dao

    async def create(self, data: UserCreateSchema) -> UserDoc | None:
        """
        Проверяет наличие пользователя в postgres, если уже существует, выбрасывает исключение UserAlreadyExistsException.
        Хэширует password, генерирует токен.
        Сохраняет результат в mongo.
        Отправляет в kafka для дальнейшей обработки.
        :return:
        """
        user = await self._dao.get_by_email(session=self._session, email=data.email)
        if user:
            raise UserAlreadyExistsException("Пользователь уже существует")

        password_hash = password_manager.hash(data.password)

        token = secrets.token_urlsafe(64)
        # TODO: zamena mongo na redis
        await redis.set(
            f"token:{token}",
            UserDBCreateSchema(
                email=data.email, password_hash=password_hash
            ).model_dump_json(),
            ex=600,
        )
        log.info("Временный пользователь %s создан в редис", data.email)
        msg = f"""Для подтверждения почты перейдите по ссылке http://localhost:8000/v2/verify?token={token}"""
        mail = MailSchema(
            recipient=data.email, msg=msg, subject="Подтверждение аккаунта"
        )
        await rabbit_router.broker.publish(
            mail,
            queue="send-email",
            persist=True,
            # headers={'x-dead-letter-exchange': 'DLQ-EX',
            #                                    'x-dead-letter-routing-key': 'dlq'}
        )
        # await email_publisher.publish(mail.model_dump_json())
        log.info("Сообщение ушло к брокеру для дальнейшей обработки")
        return user

    async def verify_email_create_user(self, token: str):
        """
        поиск в mongo пользователя по токену, если токен не найден выбрасывает исключение TokenInvalidException.
        если токен найден, проверяем существует ли такой пользователь в основной бд, если нет, то создаем нового пользователя
        иначе выбрасываем исключение UserAlreadyExistsException
        удаляем запись из mongo с текущим токеном
        :param token:
        :return:
        """
        # TODO zamena mongo na redis
        response_redis = await redis.get(f"token:{token}")
        if response_redis is None:
            raise TokenInvalidException("Token invalid")
        user_json = UserDBCreateSchema.model_validate_json(response_redis)
        log.info("Получили пользователя из редис по токену")
        user = await self._dao.get_by_email(
            session=self._session, email=user_json.email
        )
        log.info(
            "Проверяем существует ли уже пользователь с именем %s", user_json.email
        )
        if user:
            raise UserAlreadyExistsException
        user = await self._dao.create(session=self._session, **user_json.model_dump())
        log.info("Создали запись в бд с именем пользователя %s", user_json.email)
        await redis.delete(f"token:{token}")
        log.info("Очистили временного пользователя из редис")

        return user

    async def login(self, credentials: "OAuth2PasswordRequestForm") -> TokenSchema:
        user = await self._dao.get_by_email(self._session, credentials.username)
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
        await redis.set(
            f"token:reset-password:{token}", credentials.email, ex=timedelta(minutes=15)
        )

        # await kafka_producer(
        #     "send-mail",
        #     send_message_model=ConfirmMail(email=credentials.email, token=token),
        # )
        msg = f"""Для сброса пароля перейдите по ссылке http://localhost:8000/v2/reset_password?token={token}"""
        await rabbit_router.broker.publish(
            MailSchema(recipient=credentials.email, msg=msg, subject="Сброс пароля"),
            queue="send-email",
        )
        return token

    async def reset_password_with_token(self, token: str) -> str:
        email = await redis.get(f"token:reset-password:{token}")
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
        await redis.delete(f"token:reset-password:{token}")
        return user
