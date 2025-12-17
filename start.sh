#!/bin/bash

# カラー出力用
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 仮想環境が存在するかチェック
if [ ! -d "venv" ]; then
    echo -e "${RED}エラー: 仮想環境が見つかりません。${NC}"
    echo -e "先に以下のコマンドを実行してセットアップしてください:"
    echo -e "${YELLOW}./setup.sh${NC}"
    exit 1
fi

# 仮想環境をアクティベート
echo -e "${GREEN}仮想環境をアクティベートしています...${NC}"
source venv/bin/activate

# サーバーを起動
echo -e "${GREEN}=== SNS Fetcher API を起動しています ===${NC}\n"
echo -e "サーバー: ${YELLOW}http://localhost:8000${NC}"
echo -e "API ドキュメント: ${YELLOW}http://localhost:8000/docs${NC}\n"
echo -e "${GREEN}サーバーを停止するには Ctrl+C を押してください${NC}\n"

# uvicorn でサーバーを起動
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
