from uuid import UUID
from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from auth.models import User
from fastapi_users import FastAPIUsers

from auth.schemas import UserRead, UserCreate, UserUpdate
from auth.utils import auth_backend
from core.database_mongo import connection_mongo
from core.dependencies import get_user_manager
from custom_auth.documents import UserDoc
from custom_auth.routers import router as router_custom_auth
from core.logger import get_logger
from core.faststream import rabbit_router

fastapi_users = FastAPIUsers[User, UUID](get_user_manager, [auth_backend])
log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Start lifespan FastAPI")
    await connection_mongo(UserDoc)
    yield
    log.info("Stop lifespan FastAPI")


app = FastAPI(
    title="FastAPI AUTH",
    summary="Service authenticated",
    description="Service authenticated and authorized. Used JWT Header.",
    root_path="/api/auth",
    # lifespan=lifespan,
)
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

app.include_router(router_custom_auth, prefix="/v2", tags=["auth"])
app.include_router(rabbit_router, prefix="/rabbit")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def main():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
