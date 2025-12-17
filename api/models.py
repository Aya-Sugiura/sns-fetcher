from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class SNSPlatform(str, Enum):
    """対応SNSプラットフォーム"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"


class AccountInfo(BaseModel):
    """アカウント情報モデル"""
    account_id: str = Field(..., description="アカウントID")
    account_name: str = Field(..., description="アカウント名")
    followers_count: int = Field(..., description="フォロワー数")
    following_count: int = Field(..., description="フォロー数")
    post_count: Optional[int] = Field(None, description="投稿数（取得可能な場合のみ）")
    sns: SNSPlatform = Field(..., description="SNSプラットフォーム")

    class Config:
        json_schema_extra = {
            "example": {
                "account_id": "UC1234567890",
                "account_name": "Example Channel",
                "followers_count": 10000,
                "following_count": 500,
                "post_count": 1500,
                "sns": "youtube"
            }
        }


class HealthCheck(BaseModel):
    """ヘルスチェック応答モデル"""
    status: str
    timestamp: datetime
