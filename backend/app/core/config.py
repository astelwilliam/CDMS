from pydantic_settings import BaseSettings
from typing import List, Literal
import json


class Settings(BaseSettings):
    APP_NAME: str = "CDMS"
    DEBUG: bool = True
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    SESSION_EXPIRE_MINUTES: int = 60
    SESSION_COOKIE_NAME: str = "cdms_session"
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_SAMESITE: Literal["lax", "strict"] = "lax"
    CSRF_HEADER_NAME: str = "X-CSRF-Token"
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
