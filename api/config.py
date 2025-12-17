from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """アプリケーション設定"""

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
