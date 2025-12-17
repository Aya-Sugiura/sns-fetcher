from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """アプリケーション設定"""

    # X (Twitter) API
    x_bearer_token: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
