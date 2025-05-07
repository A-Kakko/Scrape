"""
Ollamaを使用した簡易フォーマットテストランナー
"""
import os
import sys
import json
from typing import Dict, List, Any, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from formatting.json_formatter import (
    format_json_with_api,
    API_TYPE_OLLAMA,
    extract_json_from_response,
    process_file
)

def run_simple_test():
    """単一アイテムのシンプルなテスト"""
    # テスト入力
    test_input = {
        "title": "星の砂時計【4人用協力型マーダーミステリー】",
        "price": 800,
        "description": "GMなしの全員参加型マーダーミステリーです。プレイ時間は約2時間です。必要人数は4名です。"
    }
    
    # モデル名 - 環境変数から取得または指定
    model_name = os.environ.get("OLLAMA_MODEL", "gemma3:12b")
    
    print(f"Ollamaを使用して単一アイテムをテスト中（モデル: {model_name}）...")
    
    # APIを呼び出し
    result = format_json_with_api(
        input_json=test_input,
        api_type=API_TYPE_OLLAMA,
        model_name=model_name
    )
    
    if result:
        print("\n--- 処理結果 ---")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("処理に失敗しました。")

def run_file_test(input_file: str = "test_data.json", output_dir: str = "test_output"):
    """ファイル処理のテスト"""
    # 出力ディレクトリを作成
    os.makedirs(output_dir, exist_ok=True)
    
    # モデル名 - 環境変数から取得または指定
    model_name = os.environ.get("OLLAMA_MODEL", "gemma3:12b")
    
    print(f"Ollamaを使用してファイルを処理中（モデル: {model_name}）...")
    print(f"入力ファイル: {input_file}")
    print(f"出力ディレクトリ: {output_dir}")
    
    # ファイル処理
    processed_count = process_file(
        file_path=input_file,
        output_dir=output_dir,
        api_type=API_TYPE_OLLAMA,
        model_name=model_name,
        delay=2.0  # APIリクエスト間の遅延を短く設定
    )
    
    print(f"\n処理完了: {processed_count}件のアイテムを処理しました。")
    
    # 出力ファイルの確認
    output_file = os.path.join(output_dir, os.path.basename(input_file))
    if os.path.exists(output_file):
        print(f"出力ファイル: {output_file}")
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"出力データ件数: {len(data) if isinstance(data, list) else 1}")
    else:
        print(f"警告: 出力ファイル {output_file} が見つかりません。")

if __name__ == "__main__":
    # コマンドライン引数の処理
    if len(sys.argv) > 1:
        # ファイル指定がある場合はファイル処理テスト
        input_file = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "test_output"
        run_file_test(input_file, output_dir)
    else:
        # 引数がない場合は単一アイテムテスト
        run_simple_test()