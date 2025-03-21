from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from core.database import Base


class BaseDAO:
    model = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.model is None:
            raise NotImplementedError("Not implemented attribute: model")
        if not issubclass(cls.model, Base):
            raise TypeError("The attribute model must be a subclass of the Base")

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> model:
        instance = cls.model(**kwargs)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance

    @classmethod
    async def get(cls, session: AsyncSession, id_: int | UUID) -> Optional[model]:
        return await session.get(cls.model, id_)
