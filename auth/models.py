from core.database import Base
from fastapi_users.db import SQLAlchemyBaseUserTableUUID


class User(Base, SQLAlchemyBaseUserTableUUID):
    pass
