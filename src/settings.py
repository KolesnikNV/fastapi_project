import sys
from typing import Union, Optional

from pydantic_settings import BaseSettings
from pydantic import EmailStr, PostgresDsn
from loguru import logger

logger.add(sys.stderr, format="{time} {level} {message}", level="DEBUG")
logger.add("logs/file_{time}.log", retention="1 day")


class Settings(BaseSettings):
    """Application settings."""

    SECRET_KEY: str
    ALGORITHM: str

    HOST: str
    PORT: int

    EMAIL_HOST: str
    EMAIL: EmailStr
    EMAIL_PASSWORD: str
    EMAIL_PORT: int

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DATABASE_URL: Union[Optional[PostgresDsn], Optional[str]]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
