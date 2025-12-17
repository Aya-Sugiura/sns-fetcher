import httpx
from api.models import AccountInfo, SNSPlatform
from api.config import settings


class XClient:
    """X (Twitter) API v2 クライアント"""

    BASE_URL = "https://api.twitter.com/2"

    def __init__(self):
        if not settings.x_bearer_token:
            raise ValueError("X Bearer Token is not configured")
        self.bearer_token = settings.x_bearer_token

    async def get_account_info(self, account_id: str) -> AccountInfo:
        """
        Xユーザー情報を取得

        Args:
            account_id: ユーザー名 (例: @elonmusk の場合 "elonmusk")

        Returns:
            AccountInfo: アカウント情報
        """
        try:
            # @ を削除
            username = account_id.lstrip('@')

            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.bearer_token}",
                }

                # ユーザー情報を取得
                response = await client.get(
                    f"{self.BASE_URL}/users/by/username/{username}",
                    headers=headers,
                    params={
                        "user.fields": "public_metrics,username,name"
                    }
                )

                if response.status_code == 401:
                    raise ValueError("X API authentication failed. Please check your Bearer Token.")
                elif response.status_code == 404:
                    raise ValueError(f"User not found: {username}")
                elif response.status_code != 200:
                    raise ValueError(f"X API error: {response.status_code} - {response.text}")

                data = response.json()

                if 'data' not in data:
                    raise ValueError(f"User not found: {username}")

                user_data = data['data']
                public_metrics = user_data.get('public_metrics', {})

                return AccountInfo(
                    account_id=user_data['username'],
                    account_name=user_data['name'],
                    followers_count=public_metrics.get('followers_count', 0),
                    following_count=public_metrics.get('following_count', 0),
                    sns=SNSPlatform.X
                )

        except httpx.HTTPError as e:
            raise ValueError(f"HTTP error occurred: {e}")
        except Exception as e:
            raise ValueError(f"Failed to fetch X user info: {e}")
