from fastapi import HTTPException, status

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import Annotated

from core.schemas import BadResponse
from custom_auth.exceptions import UserAlreadyExistsException, TokenInvalidException
from custom_auth.managers import UserManager
from custom_auth.dependencies import get_user_manager
from custom_auth.schemas import UserCreateSchema, UserBaseSchema

router = APIRouter()


@router.post(
    "/register",
    response_model=UserBaseSchema,
    status_code=201,
    responses={
        201: {
            "model": UserBaseSchema,
            "description": "При успешной регистрации будет отправлено письмо с подтверждением на указанную почту",
        },
        409: {
            "description": "Bad Request",
            "content": {
                "application/json": {"example": {"detail": "User already exists"}}
            },
        },
    },
)
async def register(
    user: UserCreateSchema,
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
):
    try:
        new_user = await user_manager.create(**user.model_dump())
    except UserAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )

    # return new_user
    response = UserBaseSchema.model_validate(new_user.model_dump()).model_dump()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=response)


@router.post(
    "/verify",
    response_model=UserBaseSchema,
    responses={
        400: {
            "content": {
                "application/json": {
                    "example": {"detail": "Token invalid"},
                    "schema": BadResponse.model_json_schema(),
                }
            }
        },
        409: {
            "content": {
                "application/json": {
                    "example": {"detail": "User already exists"},
                    "schema": BadResponse.model_json_schema(),
                }
            }
        },
    },
)
async def verify(
    token: str, user_manager: Annotated[UserManager, Depends(get_user_manager)]
):
    try:
        user = await user_manager.verify_email_create_user(token=token)
    except TokenInvalidException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token invalid"
        )

    except UserAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )
    return user
