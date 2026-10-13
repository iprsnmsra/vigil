from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SERVICE_NAME: str = "product-api"
    VERSION: str = "0.1.0"
    PORT: int = 8080
    FAILURE_MODE: str = ""
    LOG_LEVEL: str = "INFO"

settings = Settings()
