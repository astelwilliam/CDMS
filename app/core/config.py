from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    APP_NAME: str = "CDMS"
    DEBUG: bool = True
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str
    LOG_LEVEL: str = "INFO"
    BACKEND_CORS_ORIGINS: List[str] = []

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def cors_origins(self) -> List[str]:
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            return json.loads(self.BACKEND_CORS_ORIGINS)
        return self.BACKEND_CORS_ORIGINS


settings = Settings()
