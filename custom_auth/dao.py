from typing import Optional

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from core import BaseDAO
from custom_auth import CustomUser


class CustomUserDAO(BaseDAO):
    model = CustomUser

    @classmethod
    async def get_by_email(
        cls, session: AsyncSession, email: str | EmailStr
    ) -> Optional[model]:
        return await session.scalar(select(cls.model).filter_by(email=email))
