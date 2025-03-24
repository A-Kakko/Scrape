"""
設定ファイル
"""
import os

# 基本的な検索設定
SEARCH_KEYWORD = "マダミス"  # 検索キーワード
START_PAGE = 1               # 開始ページ
END_PAGE = 3                 # 終了ページ

# 出力設定
OUTPUT_DIR = "data"          # データ保存ディレクトリ

# アクセス制御設定
WAIT_TIME_MIN = 1           # アクセス間の最小待機時間
WAIT_TIME_MAX = 2            # アクセス間の最大待機時間
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
    'Referer': 'https://booth.pm/ja',
    'DNT': '1',
}

# URL設定
BASE_URL = "https://booth.pm"
