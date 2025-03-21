from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from core import BaseDAO
from custom_auth import CustomUser


class CustomUserDAO(BaseDAO):
    model = CustomUser

    @classmethod
    async def get_by_email(cls, session: AsyncSession, email: str) -> Optional[model]:
        return await session.scalar(select(cls.model).filter_by(email=email))
