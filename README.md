# SNS Fetcher API

FastAPIを使用したSNSデータ取得・管理APIです。

## 機能

- SNSアカウント情報の取得（YouTube, TikTok, X）
- アカウントID、名前、フォロワー数、フォロー数の取得
- RESTful API設計
- 自動生成されるAPI ドキュメント

## セットアップ

### 簡単な方法（推奨）

仮想環境で自動的にセットアップ・起動するスクリプトを用意しています。

```bash
# 初回セットアップ（仮想環境作成とパッケージインストール）
./setup.sh

# サーバー起動
./start.sh
```

サーバーは `http://localhost:8000` で起動します。

### 手動でセットアップする場合

#### 1. 仮想環境の作成

```bash
python3 -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
```

#### 2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

#### 3. 環境変数の設定

`.env` ファイルを作成し、使用するSNS APIのキーを設定します。

- **YouTube Data API v3**: [Google Cloud Console](https://console.cloud.google.com/apis/credentials) でAPIキーを取得
- **X (Twitter) API v2**: [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard) でBearer Tokenを取得
- **TikTok**: APIキー不要（Webスクレイピング）

`.env`ファイルの例：
```
YOUTUBE_API_KEY=your_youtube_api_key_here
X_BEARER_TOKEN=your_x_bearer_token_here
```

#### 4. サーバーの起動

```bash
uvicorn api.main:app --reload
```

## APIドキュメント

サーバー起動後、以下のURLでインタラクティブなAPIドキュメントにアクセスできます。

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## APIエンドポイント

### ヘルスチェック

- `GET /health` - サーバーの状態を確認

### アカウント情報取得

- `GET /account/` - SNSアカウント情報を取得
  - クエリパラメータ:
    - `sns`: SNSプラットフォーム (`youtube`, `tiktok`, `x`)
    - `account_id`: アカウントID

## 使用例

### YouTubeチャンネル情報を取得

```bash
# チャンネルIDを使用
curl "http://localhost:8000/account/?sns=youtube&account_id=UC_x5XG1OV2P6uZZ5FSM9Ttw"

# カスタムURLを使用
curl "http://localhost:8000/account/?sns=youtube&account_id=@GoogleDevelopers"
```

### Xアカウント情報を取得

```bash
curl "http://localhost:8000/account/?sns=x&account_id=elonmusk"
```

### TikTokアカウント情報を取得

```bash
curl "http://localhost:8000/account/?sns=tiktok&account_id=username"
```

### レスポンス例

```json
{
  "account_id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
  "account_name": "Google for Developers",
  "followers_count": 2340000,
  "following_count": 0,
  "sns": "youtube"
}
```

## プロジェクト構造

```
sns-fetcher/
├── api/
│   ├── __init__.py
│   ├── main.py              # メインアプリケーション
│   ├── models.py            # データモデル
│   ├── config.py            # 設定管理
│   ├── routers/             # 将来のルーター分割用
│   └── services/            # SNS APIクライアント
│       ├── __init__.py
│       ├── youtube_client.py
│       ├── x_client.py
│       └── tiktok_client.py
├── setup.sh                 # セットアップスクリプト
├── start.sh                 # 起動スクリプト
├── requirements.txt         # 依存パッケージ
├── .env.example             # 環境変数テンプレート
├── .gitignore
└── README.md
```

## 対応SNS

### YouTube
- YouTube Data API v3を使用
- チャンネルID またはカスタムURL（@username）で検索可能
- 取得情報: チャンネルID、チャンネル名、登録者数

### X (Twitter)
- X API v2を使用
- ユーザー名で検索
- 取得情報: ユーザー名、表示名、フォロワー数、フォロー数

### TikTok
- Webスクレイピングを使用（APIトークン不要）
- ユーザー名で検索
- 取得情報: ユーザー名、表示名、フォロワー数、フォロー数

## 開発について

### 現在の状態

- YouTube, X, TikTokの3つのSNSに対応
- YouTube, XはAPIを使用、TikTokはWebスクレイピングを使用
- YouTube, XのAPI認証には各プラットフォームのトークンが必要

### Google Cloudへのデプロイ

本番環境にデプロイする場合は、以下の対応が推奨されます。

1. **データベース**: Cloud SQL (PostgreSQL/MySQL) を使用
2. **環境**: Cloud Run または Compute Engine
3. **設定**: 環境変数で設定を管理

SQLiteはファイルベースのため、Cloud Runなどのステートレスな環境では永続化に問題があります。本番環境ではCloud SQLの使用を推奨します。

## 今後の拡張予定

- [x] 実際のSNS API連携（YouTube, X, TikTok）
- [ ] Instagram API連携
- [ ] データベース統合（取得データの保存）
- [ ] 認証・認可機能（APIキー認証）
- [ ] キャッシュ機能（レート制限対策）
- [ ] エラーハンドリングの改善
- [ ] テスト追加
- [ ] ロギング機能
