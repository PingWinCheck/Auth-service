from faststream.rabbit.fastapi import RabbitRouter
from core.settings import settings


rabbit_router = RabbitRouter(settings.rabbit.url)
