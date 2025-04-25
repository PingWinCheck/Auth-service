from uuid import uuid4

import jwt
from dataclasses import dataclass
from core.settings import settings
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from typing import Literal
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

from custom_auth.schemas import Token


@dataclass
class JWT:
    algorithm: Literal['RS256', 'HS256']
    key: str
    public_key: str | None = None

    def encode(self, payload: dict, expire_seconds: int) -> str:
        """
        Кодирует payload в json web token добавляя дополнительные поля:
        exp(Время жизни токена. Равен expire_seconds),
        iat(Время выпуска токена)
        return: str(jwt)
        """
        payload_copy = payload.copy()
        now_time = datetime.now(timezone.utc)
        time_delta = now_time + timedelta(seconds=expire_seconds)
        payload_copy['exp'] = time_delta
        payload_copy['iat'] = datetime.now(timezone.utc)
        return jwt.encode(payload=payload_copy,
                          key=self.key,
                          algorithm=self.algorithm)

    def decode(self, token: str) -> dict:
        """
        Декодирует jwt -> dict
        """
        key = self.public_key if self.public_key else self.key
        return jwt.decode(jwt=token,
                          key=key,
                          algorithms=[self.algorithm])

# @dataclass
class TokenGenerator:
    jwt_manager: JWT = JWT(algorithm='RS256',
                           key=settings.jwt.private_key,
                           public_key=settings.jwt.public_key)

# TODO: dodelat'
    def create_access_token(self, payload: dict) -> str:
        payload_copy = payload.copy()
        payload_copy['token_type'] = 'access'
        token = self.jwt_manager.encode(payload=payload_copy,
                                        expire_seconds=settings.jwt.expire_access_token_seconds)
        return token

    def create_refresh_token(self, payload: dict) -> str:
        payload_copy = payload.copy()
        payload_copy['jti'] = str(uuid4())
        payload_copy['token_type'] = 'refresh'
        token = self.jwt_manager.encode(payload=payload_copy,
                                        expire_seconds=settings.jwt.expire_refresh_token_seconds)
        return token

    def create_access_refresh_tokens_pair(self,
                                          payload_access: dict,
                                          payload_refresh: dict | None = None) -> Token:
        """
        Если payload access and refresh совпадают, то второй параметр указывать не обязательно
        """
        payload_refresh = payload_refresh if payload_refresh else payload_access
        access = self.create_access_token(payload_access)
        refresh = self.create_refresh_token(payload_refresh)
        return Token(access_token=access, refresh_token=refresh)