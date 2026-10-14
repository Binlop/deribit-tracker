from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

CONFIG_DIR = Path(__file__).resolve().parent
ENV_FILE = CONFIG_DIR / ".env.example"


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    APP_ENV: str
    DEBUG: bool = False
    PROJECT_NAME: str = "Deribit API"
    ALGORITHM: str = "HS256"

    REDIS_URL_CACHE: str = "redis://redis:6379/2"
    REDIS_URL_CELERY: str = "redis://redis:6379"
    CELERY_BROKER_DB: int = 0
    CELERY_RESULT_DB: int = 1

    DERIBIT_BASE_URL: str = "https://www.deribit.com/api/v2/public"
    FETCH_INTERVAL_SECONDS: int = 15
    TICKERS: list[str] = ["btc_usd", "eth_usd"]

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @computed_field
    @property
    def CELERY_BROKER_URL(self) -> str:
        return f"{self.REDIS_URL_CELERY}/{self.CELERY_BROKER_DB}"

    @computed_field
    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return f"{self.REDIS_URL_CELERY}/{self.CELERY_RESULT_DB}"


settings = Settings()