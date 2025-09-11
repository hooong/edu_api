from pydantic_settings import BaseSettings

from edu_register_api.enums import AppEnv


class Settings(BaseSettings):
    APP_ENV: AppEnv = "local"

    # DB
    DATABASE_URL: str = "postgresql://admin:admin@db:5432/edu_register"

    # JWT
    SECRET_KEY: str = "k8CIQfzEVVwEaXbffUI9mZSnFgL3wTlDSisr-j5R194"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
