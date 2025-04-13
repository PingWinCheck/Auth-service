from uuid import UUID

import pytest

from custom_auth import CustomUser
from custom_auth.documents import UserDoc
from custom_auth.exceptions import TokenInvalidException, UserAlreadyExistsException


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


class TestRegister:
    user = {"email": "test@example.com", "password": "fake2password"}

    @staticmethod
    @pytest.fixture()
    def mock_kafka(monkeypatch):
        async def mock_producer_kafka(*args, **kwargs):
            pass

        monkeypatch.setattr("custom_auth.managers.kafka_producer", mock_producer_kafka)
        return mock_producer_kafka

    @staticmethod
    @pytest.fixture()
    def mock_user_doc(monkeypatch):
        class MockUserDoc:
            def __init__(self, *args, **kwargs):
                self.args = (args,)
                self.kwargs = kwargs

            async def insert(self, *args, **kwargs):
                return UserDoc(**self.kwargs)

        monkeypatch.setattr("custom_auth.managers.UserDoc", MockUserDoc)
        return MockUserDoc

    async def test_register(self, client, mock_kafka, mock_user_doc):
        response = await client.post("/v2/register", json=self.user)
        assert response.status_code == 201
        assert response.json() == {
            "content": "Для продолжения регистрации следуйте инструкциям из письма отправленого к вам на почту"
        }
