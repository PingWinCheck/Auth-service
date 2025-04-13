import pytest

from httpx import ASGITransport, AsyncClient

from main import app, lifespan


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


# @pytest.fixture(autouse=True)
# def depends_override(session):
#     app.dependency_overrides[get_async_session] = session
