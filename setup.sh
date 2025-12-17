#!/bin/bash

# カラー出力用
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== SNS Fetcher API セットアップ ===${NC}\n"

# 仮想環境が既に存在するかチェック
if [ -d "venv" ]; then
    echo -e "${YELLOW}仮想環境は既に存在します。${NC}"
    read -p "削除して再作成しますか? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "仮想環境を削除しています..."
        rm -rf venv
    else
        echo "セットアップをスキップします。"
        exit 0
    fi
fi

# Python 3 が存在するか確認
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}エラー: Python 3 がインストールされていません。${NC}"
    exit 1
fi

# 仮想環境を作成
echo -e "${GREEN}仮想環境を作成しています...${NC}"
python3 -m venv venv

# 仮想環境をアクティベート
echo -e "${GREEN}仮想環境をアクティベートしています...${NC}"
source venv/bin/activate

# pip をアップグレード
echo -e "${GREEN}pip をアップグレードしています...${NC}"
pip install --upgrade pip

# 依存パッケージをインストール
echo -e "${GREEN}依存パッケージをインストールしています...${NC}"
pip install -r requirements.txt

echo -e "\n${GREEN}=== セットアップ完了 ===${NC}"
echo -e "\nサーバーを起動するには以下のコマンドを実行してください:"
echo -e "${YELLOW}./start.sh${NC}"
