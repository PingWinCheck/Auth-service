from uuid import UUID

from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column


class CustomUser(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(index=True, unique=True)
    password_hash: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
