from fastapi import APIRouter, Depends
from typing import Annotated

from custom_auth.managers import UserManager
from custom_auth.dependencies import get_user_manager
from custom_auth.schemas import UserCreateSchema, UserBaseSchema

router = APIRouter()


@router.post("/register", response_model=UserBaseSchema)
async def register(
    user: UserCreateSchema,
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
):
    new_user = await user_manager.create(**user.model_dump())
    return new_user
