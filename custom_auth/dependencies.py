from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_async_session
from fastapi import Depends

from custom_auth.dao import CustomUserDAO
from custom_auth.managers import UserManager


async def get_user_manager(
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    yield UserManager(session=session, dao=CustomUserDAO)
