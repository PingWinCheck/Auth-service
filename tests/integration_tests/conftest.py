import pytest

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from core.dependencies import get_async_session
from main import app, lifespan
from tests.conftest import TEST_URL_DB


# TODO: Костыль. При AsyncClient не отрабатывает fastapi lifespan
# @pytest.fixture(scope='session')


@pytest.fixture(scope="session")
async def lifespan_():
    async with lifespan(app):
        pass


@pytest.fixture(scope="session")
async def client(lifespan_):
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
