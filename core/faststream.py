from faststream.rabbit.fastapi import RabbitRouter
from core.settings import settings
from .schemas import MailSchema


rabbit_router = RabbitRouter(settings.rabbit.url)

email_publisher = rabbit_router.publisher(
    queue="send-email",
    title="Email",
    description="Очередь для отправки Email",
    schema=MailSchema,
)
