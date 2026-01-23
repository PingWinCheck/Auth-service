import pytest

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from core.dependencies import get_async_session
from custom_auth import CustomUser
from custom_auth.managers import password_manager
from main import app
from tests.conftest import TEST_URL_DB


# TODO: Костыль. При AsyncClient не отрабатывает fastapi lifespan
# @pytest.fixture(scope='session')


# @pytest.fixture(scope="session")
# async def lifespan_():
#     async with lifespan(app):
#         pass


@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as async_client:
        yield async_client


async def override_session():
    async_engine = create_async_engine(TEST_URL_DB)
    async_session = async_sessionmaker(async_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


app.dependency_overrides[get_async_session] = override_session


@pytest.fixture
async def user(session):
    user = CustomUser(
        email="qwe@asd.zxc", password_hash=password_manager.hash("fakeFake")
    )
    session.add(user)
    await session.commit()
    yield user
    await session.delete(user)
    await session.commit()


@pytest.fixture()
async def mock_rabbit():
    from faststream.rabbit import TestRabbitBroker
    from core.faststream import rabbit_router

    async with TestRabbitBroker(rabbit_router.broker) as br:
        yield br
