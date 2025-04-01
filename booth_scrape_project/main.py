
#TODO:実行時間がかかるのがsleep要因か環境要因か？ playwriteは時間食いそう・・・
#TODO:タイトル表記ゆれすぎ問題
#TODO:こっから詳細情報を変換する
#TODO:AIのAPIサーバを動かせるようにする必要がある
"""
BOOTHスクレイピングのエントリポイント
"""
import os
import time
import random
from typing import List, Dict, Any, Optional
from booth_scraper import BoothScraper
from data_utils import save_to_json, format_item_data
import config

def main() -> None:
    """メイン処理"""
    # 保存先ディレクトリを作成
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    
    # スクレイパーを初期化
    scraper = BoothScraper()
    
    # 収集データを保持するリスト
    all_items: List[Dict[str, Any]] = []
    
    print(f"検索キーワード: {config.SEARCH_KEYWORD}")
    print(f"ページ範囲: {config.START_PAGE}〜{config.END_PAGE}")
    
    try:
        for page in range(config.START_PAGE, config.END_PAGE + 1):
            # 検索ページからアイテムリンクのみを取得
            search_url = scraper.get_search_url(config.SEARCH_KEYWORD, page)
            item_links = scraper.get_item_links_from_search(search_url)
            
            print(f"ページ {page} から {len(item_links)} 件のアイテムリンクを取得しました")
            
            # 各アイテムページをスクレイピング
            for item_link in item_links:
                # ランダムな待機時間
                scraper.wait_random_time()
                
                # アイテムページのスクレイピング（全ての詳細情報を取得）
                item_data = scraper.scrape_item_page(item_link)
                if item_data:
                    # データを整形して追加
                    all_items.append(format_item_data(item_data))
            
            # ページ間の待機時間
            if page < config.END_PAGE:
                scraper.wait_random_time(
                    config.WAIT_TIME_MIN + 2, 
                    config.WAIT_TIME_MAX + 3
                )
            
            # 途中経過を保存
            save_to_json(
                all_items, 
                f"{config.OUTPUT_DIR}/booth_data_page_{config.START_PAGE}-{page}.json"
            )
        
        # 最終データを保存
        save_to_json(
            all_items, 
            f"{config.OUTPUT_DIR}/booth_data_{config.SEARCH_KEYWORD}.json"
        )
        
    except KeyboardInterrupt:
        print("\nユーザーによる中断が検出されました。ここまでのデータを保存します。")
        save_to_json(all_items, f"{config.OUTPUT_DIR}/booth_data_interrupted.json")
    
    except Exception as e:
        print(f"\n予期せぬエラーが発生しました: {str(e)}")
        if all_items:
            save_to_json(all_items, f"{config.OUTPUT_DIR}/booth_data_error.json")
    
    print("\nスクレイピング完了")

if __name__ == "__main__":
    main()