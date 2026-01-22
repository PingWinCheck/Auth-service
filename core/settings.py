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


class Jwt(BaseModel):
    private_key: str
    public_key: str
    expire_access_token_seconds: int
    expire_refresh_token_seconds: int


class Redis(BaseModel):
    host: str
    port: int


class Rabbit(BaseModel):
    user: str
    password: str
    port: int
    host: str

    @property
    def url(self):
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        extra="allow",
        env_nested_delimiter="__",
    )

    db: DB
    db_test: DB
    mongo: Mongo
    kafka: Kafka
    jwt: Jwt
    redis: Redis
    rabbit: Rabbit

    jwt_secret: str


settings = Settings()
