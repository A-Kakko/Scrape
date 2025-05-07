"""
汎用的なWebスクレイピングの基底クラス
"""
import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict, Any, Optional

class BaseScraper:
    """汎用Webスクレイパーの基底クラス"""
    
    def __init__(self, headers: Optional[Dict[str, str]] = None) -> None:
        """初期化"""
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
        }
    
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        指定されたURLからページのHTMLを取得し、BeautifulSoupオブジェクトとして返す
        
        Args:
            url: 取得するページのURL
            
        Returns:
            BeautifulSoupオブジェクト、エラー時はNone
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            print(f"ページの取得エラー: {url} - {str(e)}")
            return None

    def wait_random_time(self, min_time: float = 1.0, max_time: float = 2.0) -> None:
        """
        ランダムな時間待機する
        
        Args:
            min_time: 最小待機時間
            max_time: 最大待機時間
        """
        wait_time = random.uniform(min_time, max_time)
        print(f"{wait_time:.1f}秒待機中...")
        time.sleep(wait_time)