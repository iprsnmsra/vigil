from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="VIGIL_",
        env_file=(".env", "../.env", "../../.env"),
        extra="ignore",
    )

    SERVICE_NAME: str = "vigil-controller"
    VERSION: str = "0.1.0"
    PORT: int = 8080
    DRY_RUN: bool = True
    MAX_ACTIONS_PER_HOUR: int = 10
    ALLOWED_NAMESPACES: List[str] = ["default"]
    GITHUB_TOKEN: Optional[str] = None
    LLM_ENABLED: bool = True
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-flash-lite-latest"
    RULES_PATH: str = "rules.yaml"


settings = Settings()

