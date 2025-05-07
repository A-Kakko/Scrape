"""
Ollamaを使ったフォーマットのテスト
"""
import json
import os
import sys
from typing import Dict, List, Optional

# フォーマット機能をインポート
from formatting.api.ollama import format_with_ollama
from formatting.json_formatter import extract_json_from_response

def get_simple_examples() -> List[Dict]:
    """単純化されたテスト用の例を提供"""
    return [
        {
            "input": {
                "title": "殺人鬼の晩餐会【6人用マーダーミステリー】",
                "price": 1000,
                "description": "GM1名+PL6名で遊ぶマーダーミステリーです。プレイ時間は約3時間です。"
            },
            "output": {
                "title": "殺人鬼の晩餐会",
                "price": 1000,
                "game_type": "マーダーミステリー",
                "gm_required": "必要",
                "min_players": 7,
                "max_players": 7,
                "play_time": {
                    "avg": 180
                }
            }
        }
    ]

def build_simple_prompt(examples: List[Dict], input_json: Dict) -> str:
    """シンプルなプロンプトを構築"""
    prompt = """
以下はゲームシナリオのJSONデータを特定の形式に整形する例です。
次の情報を抽出・整形してください：

1. game_type: タイトルや説明文から「マーダーミステリー」「その他」を判断
2. gm_required: GMが必要かどうか
3. min_players, max_players: 最小・最大プレイ人数
4. play_time: プレイ時間（分単位）
5. title: タイトルから【】などの記号を取り除いたもの

例:
"""
    
    # 例を追加
    for example in examples:
        prompt += f"\n入力: {json.dumps(example['input'], ensure_ascii=False)}\n"
        prompt += f"出力: {json.dumps(example['output'], ensure_ascii=False)}\n"
    
    # 新しい入力を追加
    prompt += f"\n新しい入力:\n{json.dumps(input_json, ensure_ascii=False)}\n"
    prompt += "\n新しい出力（整形されたJSON）を作成してください。JSONフォーマットのみを返してください。"
    
    return prompt

def test_ollama():
    """Ollamaを使った簡単なテスト"""
    # テスト用の入力データ
    test_input = {
        "title": "星の砂時計【4人用協力型マーダーミステリー】",
        "price": 800,
        "description": "GMなしの全員参加型マーダーミステリーです。プレイ時間は約2時間です。必要人数は4名です。"
    }
    
    # テスト用の例を取得
    examples = get_simple_examples()
    
    # プロンプトを構築
    prompt = build_simple_prompt(examples, test_input)
    
    # モデル名を指定（使用可能なモデルに置き換えてください）
    model_name = "gemma3:12b"  # または "llama3:8b" など
    
    print(f"Ollamaを使用してテストを実行中（モデル: {model_name}）...")
    
    # APIを呼び出し
    response = format_with_ollama(prompt, model_name)
    
    if response:
        print("\n--- API レスポンス ---")
        print(response)
        
        # レスポンスからJSONを抽出
        formatted_json = extract_json_from_response(response)
        if formatted_json:
            print("\n--- 整形されたJSON ---")
            print(json.dumps(formatted_json, ensure_ascii=False, indent=2))
            return formatted_json
        else:
            print("JSONの抽出に失敗しました。")
    else:
        print("APIからの応答がありませんでした。")
    
    return None

if __name__ == "__main__":
    test_ollama()