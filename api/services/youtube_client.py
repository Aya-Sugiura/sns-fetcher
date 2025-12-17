from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from api.models import AccountInfo, SNSPlatform
from api.config import settings


class YouTubeClient:
    """YouTube Data API v3 クライアント"""

    def __init__(self):
        if not settings.youtube_api_key:
            raise ValueError("YouTube API key is not configured")
        self.youtube = build('youtube', 'v3', developerKey=settings.youtube_api_key)

    async def get_account_info(self, account_id: str) -> AccountInfo:
        """
        YouTubeチャンネル情報を取得

        Args:
            account_id: チャンネルID (例: UC...)またはカスタムURL

        Returns:
            AccountInfo: アカウント情報
        """
        try:
            # チャンネル情報を取得
            # account_idがカスタムURLの場合とチャンネルIDの場合の両方に対応
            if account_id.startswith('UC') or account_id.startswith('UU'):
                # チャンネルIDの場合
                request = self.youtube.channels().list(
                    part='snippet,statistics',
                    id=account_id
                )
            else:
                # カスタムURLまたはユーザー名の場合
                request = self.youtube.channels().list(
                    part='snippet,statistics',
                    forHandle=account_id
                )

            response = request.execute()

            if not response.get('items'):
                raise ValueError(f"Channel not found: {account_id}")

            channel = response['items'][0]
            snippet = channel['snippet']
            statistics = channel['statistics']

            return AccountInfo(
                account_id=channel['id'],
                account_name=snippet['title'],
                followers_count=int(statistics.get('subscriberCount', 0)),
                following_count=0,  # YouTubeにはフォロー数の概念がない
                sns=SNSPlatform.YOUTUBE
            )

        except HttpError as e:
            raise ValueError(f"YouTube API error: {e}")
        except Exception as e:
            raise ValueError(f"Failed to fetch YouTube channel info: {e}")
