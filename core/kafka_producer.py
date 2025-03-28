from aiokafka import AIOKafkaProducer
from pydantic import BaseModel, EmailStr
from core.settings import settings

URL = f"{settings.kafka_host}:{settings.kafka_port}"


class ConfirmMail(BaseModel):
    email: EmailStr
    token: str


async def kafka_producer(
    topic: str,
    send_message_model: BaseModel,
):
    prod = AIOKafkaProducer(bootstrap_servers=URL, acks="all", enable_idempotence=True)
    await prod.start()
    try:
        await prod.send_and_wait(
            topic=topic, value=send_message_model.model_dump_json().encode()
        )
    finally:
        await prod.stop()
