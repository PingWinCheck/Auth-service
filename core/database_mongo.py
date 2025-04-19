from motor.motor_asyncio import AsyncIOMotorClient
from core.settings import settings
from beanie import init_beanie
from core.logger import get_logger

log = get_logger(__name__)

URL = f"mongodb://{settings.mongo.user}:{settings.mongo.password}@{settings.mongo.host}:{settings.mongo.port}"


async def connection_mongo(*models) -> None:
    client = AsyncIOMotorClient(URL)
    await init_beanie(database=client.mongo_base, document_models=models)
    log.info("Init beanie")
