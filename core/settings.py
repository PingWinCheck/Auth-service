from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
from pathlib import Path


class DB(BaseModel):
    name: str
    user: str
    password: str
    host: str
    port: int


class Mongo(BaseModel):
    user: str
    password: str
    host: str
    port: int


class Kafka(BaseModel):
    host: str
    port: int


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        extra="allow",
        env_nested_delimiter=".",
    )

    db: DB
    db_test: DB
    mongo: Mongo
    kafka: Kafka

    jwt_secret: str


settings = Settings()
