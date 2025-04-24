

import jwt
from dataclasses import dataclass
from core.settings import settings
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from typing import Literal
from datetime import datetime, timezone, timedelta

@dataclass
class JWT:
    algorithm: Literal['RS256', 'HS256']
    key: str
    public_key: str | None = None

    def encode(self, payload: dict, expire_seconds: int) -> str:
        payload_copy = payload.copy()
        now_time = datetime.now(timezone.utc)
        time_delta = now_time + timedelta(seconds=expire_seconds)
        payload_copy['exp'] = time_delta
        return jwt.encode(payload=payload_copy,
                          key=self.key,
                          algorithm=self.algorithm)

    def decode(self, token: str) -> dict:
        key = self.public_key if self.public_key else self.key
        return jwt.decode(jwt=token,
                          key=key,
                          algorithms=[self.algorithm])
