from aiokafka import AIOKafkaProducer
from pydantic import BaseModel, EmailStr
from core.settings import settings
from core.logger import get_logger

log = get_logger(__name__)
URL = f"{settings.kafka.host}:{settings.kafka.port}"


class ConfirmMail(BaseModel):
    email: EmailStr
    token: str


async def kafka_producer(
    topic: str,
    send_message_model: BaseModel,
):
    prod = AIOKafkaProducer(bootstrap_servers=URL, acks="all", enable_idempotence=True)
    await prod.start()
    log.info("Kafka producer start")
    try:
        await prod.send_and_wait(
            topic=topic, value=send_message_model.model_dump_json().encode()
        )
        log.info("Kafka sended message in topic: %r", topic)
    finally:
        await prod.stop()
