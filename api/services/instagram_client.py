import httpx
import re
from bs4 import BeautifulSoup
from api.models import AccountInfo, SNSPlatform


class InstagramClient:
    """Instagram Webスクレイピングクライアント"""

    def __init__(self):
        pass

    def _parse_count(self, text: str) -> int:
        """
        フォロワー数などのテキストを数値に変換
        例: "831K" -> 831000, "1.5M" -> 1500000, "1,234" -> 1234
        """
        text = text.strip().replace(',', '')

        # K (千) の処理
        if 'K' in text:
            num_str = text.replace('K', '')
            try:
                return int(float(num_str) * 1000)
            except ValueError:
                return 0

        # M (百万) の処理
        if 'M' in text:
            num_str = text.replace('M', '')
            try:
                return int(float(num_str) * 1000000)
            except ValueError:
                return 0

        # 通常の数値
        try:
            return int(text)
        except ValueError:
            return 0

    async def get_account_info(self, account_id: str) -> AccountInfo:
        """
        Instagramユーザー情報を取得（Webスクレイピング）

        Args:
            account_id: ユーザー名 (例: harumi_gram)

        Returns:
            AccountInfo: アカウント情報
        """
        try:
            # @ を削除
            username = account_id.lstrip('@')
            url = f"https://www.instagram.com/{username}/"

            # httpxは自動的にgzip解凍するので、明示的なAccept-Encodingは不要
            async with httpx.AsyncClient(follow_redirects=True) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1",
                    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"macOS"'
                }

                response = await client.get(url, headers=headers, timeout=30.0)

                if response.status_code == 404:
                    raise ValueError(f"User not found: {username}")
                elif response.status_code != 200:
                    raise ValueError(f"Instagram error: {response.status_code}")

                html_content = response.text

                # BeautifulSoupでHTMLを解析
                soup = BeautifulSoup(html_content, 'html.parser')

                # og:descriptionメタタグから情報を抽出
                og_description = soup.find('meta', property='og:description')
                if not og_description:
                    raise ValueError("Could not find account data in page")

                description = og_description.get('content', '')

                # フォロワー数とフォロー数を抽出
                # 英語パターン: "XXX Followers, YYY Following"
                # 日本語パターン: "フォロワーXXX人、フォロー中YYY人"
                followers_match = re.search(r'([\d,.KM]+)\s+Followers?', description)
                following_match = re.search(r'([\d,.KM]+)\s+Following', description)

                # 日本語パターンも試す
                if not followers_match:
                    followers_match = re.search(r'フォロワー([\d,.KM]+)人', description)
                if not following_match:
                    following_match = re.search(r'フォロー中([\d,.KM]+)人', description)

                followers_count = 0
                following_count = 0

                if followers_match:
                    followers_count = self._parse_count(followers_match.group(1))

                if following_match:
                    following_count = self._parse_count(following_match.group(1))

                # アカウント名を抽出
                # og:titleから取得
                # 英語: "名前 (@username) • Instagram photos and videos"
                # 日本語: "名前(@username) • Instagram写真と動画"
                og_title = soup.find('meta', property='og:title')
                account_name = username

                if og_title:
                    title = og_title.get('content', '')
                    # "@" より前の部分を抽出（スペースあり・なし両対応）
                    name_match = re.search(r'^(.+?)\s*\(@', title)
                    if name_match:
                        account_name = name_match.group(1).strip()

                return AccountInfo(
                    account_id=username,
                    account_name=account_name,
                    followers_count=followers_count,
                    following_count=following_count,
                    sns=SNSPlatform.INSTAGRAM
                )

        except httpx.HTTPError as e:
            raise ValueError(f"HTTP error occurred: {e}")
        except Exception as e:
            raise ValueError(f"Failed to fetch Instagram user info: {e}")
