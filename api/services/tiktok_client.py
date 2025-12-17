import httpx
import json
import re
from bs4 import BeautifulSoup
from api.models import AccountInfo, SNSPlatform


class TikTokClient:
    """TikTok Webスクレイピングクライアント"""

    def __init__(self):
        pass

    async def get_account_info(self, account_id: str) -> AccountInfo:
        """
        TikTokユーザー情報を取得（Webスクレイピング）

        Args:
            account_id: ユーザー名 (例: @username の場合 "username")

        Returns:
            AccountInfo: アカウント情報
        """
        try:
            # @ を削除
            username = account_id.lstrip('@')
            url = f"https://www.tiktok.com/@{username}"

            async with httpx.AsyncClient(follow_redirects=True) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }

                response = await client.get(url, headers=headers, timeout=30.0)

                if response.status_code == 404:
                    raise ValueError(f"User not found: {username}")
                elif response.status_code != 200:
                    raise ValueError(f"TikTok error: {response.status_code}")

                html_content = response.text

                # HTMLから__UNIVERSAL_DATA_FOR_REHYDRATION__のJSONデータを抽出
                soup = BeautifulSoup(html_content, 'lxml')
                script_tag = soup.find('script', id='__UNIVERSAL_DATA_FOR_REHYDRATION__')

                if not script_tag:
                    raise ValueError("Could not find user data in page")

                json_data = json.loads(script_tag.string)

                # ユーザー情報を抽出
                # パスは: __DEFAULT_SCOPE__ -> webapp.user-detail -> userInfo
                user_info = json_data.get('__DEFAULT_SCOPE__', {}).get('webapp.user-detail', {}).get('userInfo', {})

                if not user_info:
                    raise ValueError(f"User not found: {username}")

                user = user_info.get('user', {})
                stats = user_info.get('stats', {})

                return AccountInfo(
                    account_id=user.get('uniqueId', username),
                    account_name=user.get('nickname', ''),
                    followers_count=stats.get('followerCount', 0),
                    following_count=stats.get('followingCount', 0),
                    post_count=stats.get('videoCount'),
                    sns=SNSPlatform.TIKTOK
                )

        except httpx.HTTPError as e:
            raise ValueError(f"HTTP error occurred: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse TikTok page data: {e}")
        except Exception as e:
            raise ValueError(f"Failed to fetch TikTok user info: {e}")
