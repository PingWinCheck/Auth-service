import uuid
from uuid import UUID

from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column


class User(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4())
    username: Mapped[str]
    password: Mapped[str]
    email: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
