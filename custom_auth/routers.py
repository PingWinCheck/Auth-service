from fastapi import HTTPException, status

from fastapi import APIRouter, Depends

from typing import Annotated


from core.schemas import BadResponse
from custom_auth.exceptions import (
    UserAlreadyExistsException,
    TokenInvalidException,
    InvalidLoginOrPassword,
)
from custom_auth.managers import UserManager
from custom_auth.dependencies import get_user_manager
from custom_auth.schemas import (
    UserCreateSchema,
    UserBaseSchema,
    UserLoginSchema,
    TokenSchema,
)

router = APIRouter()


@router.post(
    "/register",
    status_code=201,
    responses={
        201: {
            "content": {
                "application/json": {
                    "example": {
                        "detail": "При успешной регистрации будет отправлено письмо \
с подтверждением на указанную почту"
                    }
                }
            },
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
        await user_manager.create(**user.model_dump())
    except UserAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )

    return {
        "content": "Для продолжения регистрации следуйте инструкциям из письма отправленого к вам на почту"
    }


@router.get(
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


@router.post(
    "/login",
    response_model=TokenSchema,
    responses={
        403: {
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid login or password"},
                    "schema": BadResponse.model_json_schema(),
                }
            }
        },
    },
)
async def login(
    credentials: UserLoginSchema,
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
):
    try:
        token = await user_manager.login(credentials=credentials)
    except InvalidLoginOrPassword:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid login or password"
        )
    return token
