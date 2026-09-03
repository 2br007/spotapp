import logging
import os
from typing import Optional

from pydantic import BaseModel, Field

from api.constants import DEFAULT_LOG_FORMAT


def database_dsn():
    return os.environ.get("DB_DSN") or os.environ["db_dsn"]


class Settings(BaseModel):
    """Settings which can be provided when server starts"""
    # db_dsn in format: 'postgresql+asyncpg://USERNAME:PASSWORD@$HOST/DB_NAME'
    db_dsn: str = Field(default_factory=database_dsn)
    log_format: Optional[str] = DEFAULT_LOG_FORMAT
    log_level: Optional[str] = "INFO"
    db_query_timeout: Optional[int] = 30


settings = Settings()


def configure_logger(logger_name: str,
                     log_format: Optional[str] = settings.log_format,
                     log_level: Optional[str] = settings.log_level):
    """Logger configuration"""
    try:
        logging.basicConfig(level=log_level, format=log_format)
        logger = logging.getLogger()
        logger.setLevel(log_level)
    except Exception as exc:
        logging.error(f"Can't init default logger: {exc}")
