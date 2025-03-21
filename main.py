from uuid import UUID

from fastapi import FastAPI
import uvicorn

from auth.models import User
from fastapi_users import FastAPIUsers

from auth.schemas import UserRead, UserCreate, UserUpdate
from auth.utils import auth_backend
from core.dependencies import get_user_manager

fastapi_users = FastAPIUsers[User, UUID](get_user_manager, [auth_backend])

app = FastAPI()
# app.include_router(router_auth)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


def main():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
