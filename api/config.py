from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """アプリケーション設定"""

    # YouTube API
    youtube_api_key: Optional[str] = None

    # X (Twitter) API
    x_bearer_token: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
