from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_prefix="VIGIL_")

    SERVICE_NAME: str = "vigil-controller"
    VERSION: str = "0.1.0"
    PORT: int = 8080
    DRY_RUN: bool = True
    MAX_ACTIONS_PER_HOUR: int = 10
    ALLOWED_NAMESPACES: List[str] = ["default"]
    GITHUB_TOKEN: Optional[str] = None
    LLM_ENABLED: bool = True
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    RULES_PATH: str = "rules.yaml"


settings = Settings()

