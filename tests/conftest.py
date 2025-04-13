import asyncio
from typing import AsyncGenerator

import pytest

from core.database import Base
from core.settings import settings
from alembic.config import Config
from alembic import command


from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

TEST_URL_DB = f"postgresql+asyncpg://{settings.db_test.user}:{settings.db_test.password}@{settings.db_test.host}:{settings.db_test.port}/{settings.db_test.name}"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def make_migrate():
    config = Config("alembic.ini")
    config.set_main_option("test", "True")
    command.upgrade(config, "head")
    yield
    command.downgrade(config, "base")


@pytest.fixture()
async def session() -> AsyncGenerator[AsyncSession, None]:
    async_engine = create_async_engine(TEST_URL_DB)
    async_session = async_sessionmaker(async_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture()
async def drop_table(session):
    yield
    for table in reversed(Base.metadata.sorted_tables):
        await session.execute(table.delete())
        await session.commit()
