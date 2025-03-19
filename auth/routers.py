from fastapi import APIRouter, Depends
from auth.schemas import UserCreateSchema, UserBaseSchema
from auth.dao import UserDAO
from core.dependencies import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=UserBaseSchema)
async def register(
    user_credentials: UserCreateSchema,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await UserDAO.create_instance(
        session=session, **user_credentials.model_dump()
    )


@router.post("/update")
async def update(
    credentials: dict[str, str], session: Annotated[AsyncSession, Depends(get_session)]
):
    await UserDAO.update_instance(session, **credentials)
