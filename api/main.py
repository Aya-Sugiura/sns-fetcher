from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from api.models import HealthCheck, AccountInfo, SNSPlatform
from api.services.youtube_client import YouTubeClient
from api.services.x_client import XClient
from api.services.tiktok_client import TikTokClient
from api.services.instagram_client import InstagramClient

app = FastAPI(
    title="SNS Fetcher API",
    description="SNSデータ取得・管理API",
    version="0.1.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では特定のオリジンのみを許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """ルートエンドポイント"""
    return {
        "message": "SNS Fetcher API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """ヘルスチェックエンドポイント"""
    return HealthCheck(
        status="ok",
        timestamp=datetime.now()
    )


@app.get("/account/", response_model=AccountInfo, tags=["Account"])
async def get_account(
    sns: SNSPlatform = Query(..., description="SNSプラットフォーム (youtube, tiktok, x, instagram)"),
    account_id: str = Query(..., description="アカウントID")
):
    """
    SNSアカウント情報を取得

    - **sns**: SNSプラットフォーム (youtube, tiktok, x, instagram)
    - **account_id**: アカウントID
      - YouTube: チャンネルハンドル (例: @username)
      - X: ユーザー名 (例: elonmusk)
      - TikTok: ユーザー名 (例: username)
      - Instagram: ユーザー名 (例: username)

    Returns:
        AccountInfo: アカウント情報 (ID, 名前, フォロワー数, フォロー数)
    """
    try:
        if sns == SNSPlatform.YOUTUBE:
            client = YouTubeClient()
            return await client.get_account_info(account_id)

        elif sns == SNSPlatform.X:
            client = XClient()
            return await client.get_account_info(account_id)

        elif sns == SNSPlatform.TIKTOK:
            client = TikTokClient()
            return await client.get_account_info(account_id)

        elif sns == SNSPlatform.INSTAGRAM:
            client = InstagramClient()
            return await client.get_account_info(account_id)

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported SNS platform: {sns}"
            )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
