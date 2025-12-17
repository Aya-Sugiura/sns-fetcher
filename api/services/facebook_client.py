import httpx
import re
from bs4 import BeautifulSoup
from api.models import AccountInfo, SNSPlatform


class FacebookClient:
    """Facebook Webスクレイピングクライアント"""

    def __init__(self):
        pass

    def _parse_count(self, text: str) -> int:
        """
        フォロワー数などのテキストを数値に変換
        例: "111,402" -> 111402, "24萬" -> 240000, "1.5K" -> 1500
        """
        text = text.strip().replace(',', '')

        # 萬 (万) の処理
        if '萬' in text or '万' in text:
            num_str = text.replace('萬', '').replace('万', '')
            try:
                return int(float(num_str) * 10000)
            except ValueError:
                return 0

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
        Facebookページ情報を取得（Webスクレイピング）

        Args:
            account_id: ページID (例: HokkaidoJerry)

        Returns:
            AccountInfo: アカウント情報
        """
        try:
            # @ を削除
            page_id = account_id.lstrip('@')
            url = f"https://www.facebook.com/{page_id}"

            async with httpx.AsyncClient(follow_redirects=True) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1"
                }

                response = await client.get(url, headers=headers, timeout=30.0)

                if response.status_code == 404:
                    raise ValueError(f"Page not found: {page_id}")
                elif response.status_code != 200:
                    raise ValueError(f"Facebook error: {response.status_code}")

                html_content = response.text

                # BeautifulSoupでHTMLを解析
                soup = BeautifulSoup(html_content, 'html.parser')

                # og:titleからアカウント名を取得
                og_title = soup.find('meta', property='og:title')
                if not og_title:
                    raise ValueError("Could not find page data")

                account_name = og_title.get('content', page_id)

                # og:descriptionから情報を抽出
                og_description = soup.find('meta', property='og:description')
                description = og_description.get('content', '') if og_description else ''

                # 個人アカウントかどうかをチェック
                # 個人アカウントの場合は「Facebookを利用しています」「Join Facebook to connect」などのテキストが含まれる
                personal_account_patterns = [
                    'Facebookを利用しています',
                    'Facebookに登録して',
                    'Join Facebook to connect',
                    'Facebook에 가입하여',  # 韓国語
                    '加入 Facebook，与',  # 中国語
                ]

                for pattern in personal_account_patterns:
                    if pattern in description:
                        raise ValueError(f"Personal accounts are not supported. Only Facebook Pages can be accessed: {page_id}")

                followers_count = 0

                # 「いいね！」のパターンを抽出
                # 日本語: 「いいね！」111,402件
                # 英語: 111,402 likes
                # 中国語: 111,402 次贊
                likes_match = re.search(r'「いいね！」([\d,]+)件', description)
                if not likes_match:
                    likes_match = re.search(r'([\d,]+)\s*likes?', description, re.IGNORECASE)
                if not likes_match:
                    likes_match = re.search(r'([\d,]+)\s*次贊', description)

                if likes_match:
                    followers_count = self._parse_count(likes_match.group(1))

                return AccountInfo(
                    account_id=page_id,
                    account_name=account_name,
                    followers_count=followers_count,
                    following_count=0,  # Facebookページはフォロー数を取得しない
                    post_count=None,  # 投稿数は取得困難
                    sns=SNSPlatform.FACEBOOK
                )

        except httpx.HTTPError as e:
            raise ValueError(f"HTTP error occurred: {e}")
        except Exception as e:
            raise ValueError(f"Failed to fetch Facebook page info: {e}")
