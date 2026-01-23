from uuid import UUID

import pytest

from custom_auth import CustomUser
from custom_auth.exceptions import TokenInvalidException, UserAlreadyExistsException
from pytest_mock import MockerFixture

user = CustomUser(
    email="qwe@asd.zxc",
    password_hash="nlo",
    id=UUID("a67b6d7c-2fa0-4a98-b7cd-501ba3f53d86"),
)


class TestVerify:
    @staticmethod
    @pytest.fixture
    def fixture_mock_verify_email_create_user(monkeypatch):
        async def mock_verify_email_create_user(self, token):
            if token == "1":
                raise TokenInvalidException
            if token == "2":
                raise UserAlreadyExistsException
            return user

        monkeypatch.setattr(
            "custom_auth.managers.UserManager.verify_email_create_user",
            mock_verify_email_create_user,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "token, status, js",
        [
            ("1", 400, {"detail": "Token invalid"}),
            ("2", 409, {"detail": "User already exists"}),
            ("3", 200, {"email": user.email}),
        ],
    )
    async def test_verify(
        client, fixture_mock_verify_email_create_user, token, status, js
    ):
        response = await client.get("/v2/verify", params={"token": token})
        assert response.status_code == status
        assert response.json() == js


# class TestRegister:
#     user = {"email": "test@example.com", "password": "fake2password"}
#
#     @staticmethod
#     @pytest.fixture()
#     def mock_kafka(monkeypatch):
#         async def mock_producer_kafka(*args, **kwargs):
#             pass
#
#         monkeypatch.setattr("custom_auth.managers.kafka_producer", mock_producer_kafka)
#         return mock_producer_kafka
#
#     @staticmethod
#     @pytest.fixture()
#     def mock_user_doc(monkeypatch):
#         class MockUserDoc:
#             def __init__(self, *args, **kwargs):
#                 self.args = (args,)
#                 self.kwargs = kwargs
#
#             async def insert(self, *args, **kwargs):
#                 return UserDoc(**self.kwargs)
#
#         monkeypatch.setattr("custom_auth.managers.UserDoc", MockUserDoc)
#         return MockUserDoc
#
#     async def test_register(self, client, mock_kafka, mock_user_doc):
#         response = await client.post("/v2/register", json=self.user)
#         assert response.status_code == 201
#         assert response.json() == {
#             "content": "Для продолжения регистрации следуйте инструкциям из письма отправленого к вам на почту"
#         }


class TestRegisterV2:
    user = {"email": "test@example.com", "password": "fake2password"}

    async def test_register(self, client, mocker: MockerFixture, mock_rabbit):
        # from faststream.rabbit import TestRabbitBroker
        # from core.faststream import rabbit_router
        # async with TestRabbitBroker(rabbit_router.broker):
        #     response = await client.post('/v2/register', json=self.user)
        #     assert response.status_code == 201

        # mock = mocker.patch.object(rabbit_router.broker, "publish")
        # mock.return_value = None
        # from custom_auth.managers import redis
        from unittest.mock import AsyncMock

        # mock_redis = mocker.patch.object(redis, 'set', new_callable=AsyncMock)
        mock_redis = AsyncMock()
        mocker.patch("custom_auth.managers.redis", mock_redis)

        response = await client.post("/v2/register", json=self.user)
        mock_redis.set.assert_awaited_once()
        args, kwargs = mock_redis.set.call_args
        assert response.status_code == 201
        assert response.json() == {
            "content": "Для продолжения регистрации следуйте инструкциям из письма отправленого к вам на почту"
        }
        assert "token:" in args[0]
        assert f'"email":"{self.user["email"]}"' in args[1]
        assert kwargs["ex"] == 600


class TestLogin:
    async def test_login(self, client, user):
        response = await client.post(
            "/v2/login", data={"username": user.email, "password": "fakeFake"}
        )

        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()
        assert "token_type" in response.json()

    @pytest.mark.parametrize(
        "email, password, response_status, response_json",
        [
            ("1qwe@asd.zxc", "1fakeFake", 403, {"detail": "Invalid login or password"}),
            ("1qwe@asd.zxc", "fakeFake", 403, {"detail": "Invalid login or password"}),
            ("qwe@asd.zxc", "fakeFake1", 403, {"detail": "Invalid login or password"}),
        ],
    )
    async def test_login_incorrect(
        self, client, user, email, password, response_status, response_json
    ):
        response = await client.post(
            "/v2/login", data={"username": email, "password": password}
        )
        assert response.status_code == response_status
        assert response.json() == response_json
