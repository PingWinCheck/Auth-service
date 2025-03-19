from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column

from core.settings import settings


URL = f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

async_engine = create_async_engine(url=URL)

async_session = async_sessionmaker(async_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # def __init_subclass__(cls, **kwargs):
    #     cls.__tablename__ = cls.__name__.lower() + 's'
    #     super().__init_subclass__(**kwargs)
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + "'s"
