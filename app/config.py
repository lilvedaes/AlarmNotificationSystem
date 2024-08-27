# app/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    sns_topic_arn: str
    celery_broker_url: str
    celery_result_backend: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: str
    timezone: str

    class Config:
        env_file = ".env"

settings = Settings()
