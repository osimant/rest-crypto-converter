from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = False
    HOST: str
    PORT: int
    HTTP_SCHEMA: str
    BASE_URL: str = ""
    API_V1_STR: str = "v1"
    BACKEND_CORS_ORIGINS: str
    OPENAPI_ENABLED: bool

    REDIS_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: int

    @staticmethod
    def get_backend_cors_origins(v: str) -> List[str]:
        return [i.strip() for i in v.split(" ")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
