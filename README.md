# SNS Fetcher API

FastAPIを使用したSNSデータ取得・管理APIです。

## 機能

- SNS投稿データのCRUD操作
- プラットフォームごとのフィルタリング
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

#### 3. サーバーの起動

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

### 投稿管理

- `GET /posts` - 投稿一覧を取得（クエリパラメータ `platform` でフィルタリング可能）
- `GET /posts/{post_id}` - 特定の投稿を取得
- `POST /posts` - 新しい投稿を作成
- `PUT /posts/{post_id}` - 投稿を更新
- `DELETE /posts/{post_id}` - 投稿を削除

## 使用例

### 投稿を作成

```bash
curl -X POST "http://localhost:8000/posts" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "twitter",
    "content": "Hello World!",
    "author": "user123",
    "url": "https://twitter.com/user123/status/123456"
  }'
```

### 投稿一覧を取得

```bash
curl "http://localhost:8000/posts"
```

### プラットフォームでフィルタリング

```bash
curl "http://localhost:8000/posts?platform=twitter"
```

## プロジェクト構造

```
sns-fetcher/
├── api/
│   ├── __init__.py
│   ├── main.py          # メインアプリケーション
│   ├── models.py        # データモデル
│   └── routers/         # 将来のルーター分割用
├── setup.sh             # セットアップスクリプト
├── start.sh             # 起動スクリプト
├── requirements.txt     # 依存パッケージ
├── .gitignore
└── README.md
```

## 開発について

### 現在の状態

- データはメモリ上で管理（サーバー再起動でリセット）
- 将来的にはデータベース連携を追加予定

### Google Cloudへのデプロイ

本番環境にデプロイする場合は、以下の対応が推奨されます。

1. **データベース**: Cloud SQL (PostgreSQL/MySQL) を使用
2. **環境**: Cloud Run または Compute Engine
3. **設定**: 環境変数で設定を管理

SQLiteはファイルベースのため、Cloud Runなどのステートレスな環境では永続化に問題があります。本番環境ではCloud SQLの使用を推奨します。

## 今後の拡張予定

- [ ] データベース統合 (Cloud SQL)
- [ ] 認証・認可機能
- [ ] 実際のSNS API連携（Twitter, Instagram等）
- [ ] キャッシュ機能
- [ ] ページネーション
- [ ] テスト追加
