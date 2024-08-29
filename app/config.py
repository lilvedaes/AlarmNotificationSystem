from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_default_region: str
    end_user_messaging_sender_id_arn: str
    pinpoint_verified_email: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: str
    timezone: str

    class Config:
        env_file = ".env"

settings = Settings()
