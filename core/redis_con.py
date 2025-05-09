from redis.asyncio import Redis
from core.settings import settings

redis = Redis(host=settings.redis.host, port=settings.redis.port, decode_responses=True)
