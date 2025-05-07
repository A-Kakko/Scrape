"""
BOOTHスクレイピングのエントリポイント
"""
import os
import argparse
from typing import List, Dict, Any, Optional

# スクレイピング機能
from scraping.booth_scraper import BoothScraper
# 整形機能 
from formatting.json_formatter import process_file
# ユーティリティ
from utils.data_utils import save_to_json, format_item_data
# 設定
import config

def scrape_booth(keyword: str, start_page: int = 1, end_page: int = 1, output_dir: str = "data") -> List[Dict[str, Any]]:
    """
    BOOTHからデータをスクレイピングする
    
    Args:
        keyword: 検索キーワード
        start_page: 開始ページ
        end_page: 終了ページ
        output_dir: 出力ディレクトリ
        
    Returns:
        収集したデータのリスト
    """
    # 保存先ディレクトリを作成
    os.makedirs(output_dir, exist_ok=True)
    
    # スクレイパーを初期化
    scraper = BoothScraper()
    
    # 収集データを保持するリスト
    all_items: List[Dict[str, Any]] = []
    
    print(f"検索キーワード: {keyword}")
    print(f"ページ範囲: {start_page}〜{end_page}")
    
    try:
        for page in range(start_page, end_page + 1):
            # 検索ページからアイテムリンクのみを取得
            search_url = scraper.get_search_url(keyword, page)
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
            if page < end_page:
                scraper.wait_random_time(
                    config.WAIT_TIME_MIN + 2, 
                    config.WAIT_TIME_MAX + 3
                )
            
            # 途中経過を保存
            save_to_json(
                all_items, 
                f"{output_dir}/booth_data_page_{start_page}-{page}.json"
            )
        
        # 最終データを保存
        save_to_json(
            all_items, 
            f"{output_dir}/booth_data_{keyword}.json"
        )
        
        return all_items
        
    except KeyboardInterrupt:
        print("\nユーザーによる中断が検出されました。ここまでのデータを保存します。")
        save_to_json(all_items, f"{output_dir}/booth_data_interrupted.json")
        return all_items
    
    except Exception as e:
        print(f"\n予期せぬエラーが発生しました: {str(e)}")
        if all_items:
            save_to_json(all_items, f"{output_dir}/booth_data_error.json")
        return all_items

def format_booth_data(input_file: str, output_dir: str = "formatted", api_type: str = "gemini") -> None:
    """
    収集したBOOTHデータをAI APIを使用して整形する
    
    Args:
        input_file: 入力ファイル
        output_dir: 出力ディレクトリ
        api_type: 使用するAPIタイプ ("gemini" or "ollama")
    """
    # デフォルトモデル設定
    model_name = "gemini-2.0-flash-001" if api_type == "gemini" else "gemma3:12b"
    
    # ファイル処理
    processed_count = process_file(input_file, output_dir, api_type, model_name)
    print(f"{processed_count}件のデータを整形しました")

def main() -> None:
    """メイン処理"""
    parser = argparse.ArgumentParser(description='BOOTHスクレイピングとデータ整形')
    
    # サブコマンドの設定
    subparsers = parser.add_subparsers(dest='command', help='実行するコマンド')
    
    # スクレイピングコマンド
    scrape_parser = subparsers.add_parser('scrape', help='BOOTHからデータをスクレイピング')
    scrape_parser.add_argument('--keyword', '-k', required=True, help='検索キーワード')
    scrape_parser.add_argument('--start', '-s', type=int, default=1, help='開始ページ')
    scrape_parser.add_argument('--end', '-e', type=int, default=1, help='終了ページ')
    scrape_parser.add_argument('--output', '-o', default='data', help='出力ディレクトリ')
    
    # フォーマットコマンド
    format_parser = subparsers.add_parser('format', help='スクレイピングしたデータをフォーマット')
    format_parser.add_argument('--input', '-i', required=True, help='入力ファイル')
    format_parser.add_argument('--output', '-o', default='formatted', help='出力ディレクトリ')
    format_parser.add_argument('--api', '-a', choices=['gemini', 'ollama'], default='gemini', help='使用するAPI')
    
    args = parser.parse_args()
    
    if args.command == 'scrape':
        scrape_booth(args.keyword, args.start, args.end, args.output)
        print("\nスクレイピング完了")
        
    elif args.command == 'format':
        format_booth_data(args.input, args.output, args.api)
        print("\nフォーマット完了")
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()