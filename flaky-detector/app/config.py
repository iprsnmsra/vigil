from typing import Optional

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SERVICE_NAME: str = "vigil-flaky-detector"
    VERSION: str = "0.1.0"
    PORT: int = 8081
    DATABASE_URL: str = "sqlite:///./test.db"
    QUARANTINE_THRESHOLD: float = 0.7
    GITHUB_TOKEN: Optional[str] = None

    class Config:
        env_prefix = "VIGIL_FLAKY_"

settings = Settings()
