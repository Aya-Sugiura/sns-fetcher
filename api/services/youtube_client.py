import httpx
import json
import re
from api.models import AccountInfo, SNSPlatform


class YouTubeClient:
    """YouTube Webスクレイピングクライアント"""

    def __init__(self):
        pass

    def _parse_subscriber_count(self, text: str) -> int:
        """
        登録者数のテキストを数値に変換
        例: "11万人" -> 110000, "1.5万人" -> 15000, "1200人" -> 1200
        """
        # "チャンネル登録者数 " などのプレフィックスを削除
        text = re.sub(r'チャンネル登録者数\s*', '', text)
        text = re.sub(r'人.*', '', text)  # "人" 以降を削除
        text = text.strip()

        # "万" がある場合
        if '万' in text:
            num_str = text.replace('万', '')
            try:
                return int(float(num_str) * 10000)
            except ValueError:
                return 0

        # 通常の数値
        try:
            return int(text.replace(',', ''))
        except ValueError:
            return 0

    async def get_account_info(self, account_id: str) -> AccountInfo:
        """
        YouTubeチャンネル情報を取得（Webスクレイピング）

        Args:
            account_id: チャンネルハンドル (例: @username) またはチャンネルID

        Returns:
            AccountInfo: アカウント情報
        """
        try:
            # @ を追加（なければ）
            if not account_id.startswith('@') and not account_id.startswith('UC'):
                account_id = f'@{account_id}'

            url = f"https://www.youtube.com/{account_id}"

            async with httpx.AsyncClient(follow_redirects=True) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7"
                }

                response = await client.get(url, headers=headers, timeout=30.0)

                if response.status_code == 404:
                    raise ValueError(f"Channel not found: {account_id}")
                elif response.status_code != 200:
                    raise ValueError(f"YouTube error: {response.status_code}")

                html_content = response.text

                # ytInitialDataを抽出
                pattern = r'var ytInitialData = ({.*?});'
                match = re.search(pattern, html_content, re.DOTALL)

                if not match:
                    raise ValueError("Could not find channel data in page")

                json_data = json.loads(match.group(1))

                # チャンネル情報を抽出
                header = json_data.get('header', {}).get('pageHeaderRenderer', {})
                content = header.get('content', {}).get('pageHeaderViewModel', {})

                # チャンネル名
                title_obj = content.get('title', {}).get('dynamicTextViewModel', {}).get('text', {})
                channel_name = title_obj.get('content', '')

                if not channel_name:
                    raise ValueError(f"Channel not found: {account_id}")

                # メタデータから登録者数とハンドル名を取得
                metadata = content.get('metadata', {}).get('contentMetadataViewModel', {})
                metadata_rows = metadata.get('metadataRows', [])

                channel_handle = account_id
                subscriber_count = 0

                # metadata_rows[0]: ハンドル名
                if len(metadata_rows) > 0:
                    parts = metadata_rows[0].get('metadataParts', [])
                    if parts:
                        handle_text = parts[0].get('text', {}).get('content', '')
                        if handle_text.startswith('@'):
                            channel_handle = handle_text

                # metadata_rows[1]: 登録者数と動画数
                if len(metadata_rows) > 1:
                    parts = metadata_rows[1].get('metadataParts', [])
                    if parts:
                        subscriber_text = parts[0].get('text', {}).get('content', '')
                        subscriber_count = self._parse_subscriber_count(subscriber_text)

                return AccountInfo(
                    account_id=channel_handle,
                    account_name=channel_name,
                    followers_count=subscriber_count,
                    following_count=0,  # YouTubeにはフォロー数の概念がない
                    sns=SNSPlatform.YOUTUBE
                )

        except httpx.HTTPError as e:
            raise ValueError(f"HTTP error occurred: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse YouTube page data: {e}")
        except Exception as e:
            raise ValueError(f"Failed to fetch YouTube channel info: {e}")
