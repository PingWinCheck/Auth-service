import pytest
from faker import Faker
from sqlalchemy.exc import IntegrityError

from custom_auth import CustomUser
from custom_auth.dao import CustomUserDAO

fake = Faker()


class TestCustomUserDAO:
    @staticmethod
    @pytest.mark.parametrize(
        "email, password", [(fake.email(safe=False), fake.password(length=8))]
    )
    async def test_create_get(email, password, session, drop_table):
        new_user: CustomUser = await CustomUserDAO.create(
            session, email=email, password_hash=password
        )
        user_db = await CustomUserDAO.get(session=session, id_=new_user.id)
        assert email == user_db.email
        assert password == user_db.password_hash

        assert new_user.id == user_db.id
        assert new_user.created_at == user_db.created_at
        assert new_user.updated_at == user_db.updated_at
        assert new_user.email == user_db.email
        assert new_user.password_hash == user_db.password_hash

    @staticmethod
    @pytest.mark.parametrize(
        "email, password_hash, expected_exception",
        [
            (None, None, IntegrityError),
            ("qwe@qwe.qw", None, IntegrityError),
            (None, "nab782342askdqw", IntegrityError),
        ],
    )
    async def test_create_error(
        email, password_hash, expected_exception, session, drop_table
    ):
        with pytest.raises(expected_exception, match="null value in"):
            try:
                await CustomUserDAO.create(
                    session=session, email=email, password_hash=password_hash
                )
            finally:
                await session.rollback()

    @staticmethod
    async def test_create_duplicate(session):
        session.add(CustomUser(email="qwe@qwe.qwe", password_hash="xcjneravm32423"))
        session.add(CustomUser(email="qwe@qwe.qwe", password_hash="ytneyne"))
        with pytest.raises(IntegrityError, match="duplicate key value"):
            await session.flush()

    @staticmethod
    async def test_get_by_email(session):
        email = "qwe@qwe.qwe"
        password_hash = "xcjneravm32423"
        session.add(CustomUser(email=email, password_hash=password_hash))
        await session.flush()
        user = await CustomUserDAO.get_by_email(session=session, email=email)
        assert user
        assert user.email == email
        assert user.password_hash == password_hash

        fake_user = await CustomUserDAO.get_by_email(session=session, email=email + "1")
        assert fake_user is None
        await session.rollback()
