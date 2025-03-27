from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env", extra="forbid"
    )

    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int

    jwt_secret: str

    mongo_user: str
    mongo_password: str
    mongo_host: str
    mongo_port: int

    kafka_host: str
    kafka_port: int


settings = Settings()
