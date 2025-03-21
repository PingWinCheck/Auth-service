from uuid import UUID

from fastapi_users.authentication import (
    BearerTransport,
    JWTStrategy,
    AuthenticationBackend,
)
from fastapi_users import BaseUserManager, UUIDIDMixin

from auth.models import User
from core.settings import settings

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy():
    return JWTStrategy(secret=settings.jwt_secret, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt", transport=bearer_transport, get_strategy=get_jwt_strategy
)


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    verification_token_secret = "secret"
    reset_password_token_secret = "secret"
