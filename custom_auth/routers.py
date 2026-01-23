from fastapi import HTTPException, status, Form
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends

from typing import Annotated


from core.schemas import BadResponse
from custom_auth.exceptions import (
    UserAlreadyExistsException,
    TokenInvalidException,
    InvalidLoginOrPasswordException,
    UserDoesNotExistsException,
)
from custom_auth.managers import UserManager
from custom_auth.dependencies import get_user_manager
from custom_auth.schemas import (
    UserCreateSchema,
    UserBaseSchema,
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
        await user_manager.create(user)
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
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
):
    try:
        token = await user_manager.login(credentials=credentials)
    except InvalidLoginOrPasswordException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid login or password"
        )
    return token


# TODO: Написать тесты на сброс пароля
# TODO: ответ убрать токен
# TODO: сделать отправку письма


@router.patch("/change_password")
async def change_password(
    email: UserBaseSchema,
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
):
    try:
        await user_manager.reset_password(email)
    except UserDoesNotExistsException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {
        "detail": "Письмо для сброса пароля отправлено на вашу почту",
    }


@router.get("/reset_password")
async def reset_password_token(
    token: str, user_manager: Annotated[UserManager, Depends(get_user_manager)]
):
    try:
        return await user_manager.reset_password_with_token(token)
    except TokenInvalidException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/reset_password", response_model=UserBaseSchema)
async def reset_password(
    token: str,
    password: Annotated[str, Form()],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
):
    try:
        user = await user_manager.reset_password_with_token_new_password(
            token, password
        )
    except TokenInvalidException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UserDoesNotExistsException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return user
