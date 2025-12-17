from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SNSPost(BaseModel):
    """SNS投稿データモデル"""
    id: Optional[int] = None
    platform: str = Field(..., description="SNSプラットフォーム (twitter, instagram, etc.)")
    content: str = Field(..., description="投稿内容")
    author: str = Field(..., description="投稿者")
    created_at: Optional[datetime] = None
    url: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "platform": "twitter",
                "content": "Hello World!",
                "author": "user123",
                "url": "https://twitter.com/user123/status/123456"
            }
        }


class SNSPostCreate(BaseModel):
    """SNS投稿作成用モデル"""
    platform: str
    content: str
    author: str
    url: Optional[str] = None


class HealthCheck(BaseModel):
    """ヘルスチェック応答モデル"""
    status: str
    timestamp: datetime
