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
    async def create_instance(cls, session: AsyncSession, **kwargs):
        instance = cls.model(**kwargs)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance

    @classmethod
    async def update_instance(cls, session: AsyncSession, **kwargs):
        instance = await session.get(cls.model, kwargs.get("id"))
        instance.username = kwargs.get("username")
        await session.commit()
