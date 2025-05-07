"""
AI APIを使用してJSONデータを整形するモジュール
"""
import os
import json
import re
import time
import requests
import sys
from typing import Dict, List, Any, Optional
from tqdm import tqdm
from pathlib import Path
from utils.data_utils import append_to_json
# APIクライアントインポート
from formatting.api.gemini import format_with_gemini
from formatting.api.ollama import format_with_ollama

# APIのタイプを定義
API_TYPE_GEMINI = "gemini"
API_TYPE_OLLAMA = "ollama"

# モデル設定
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash-001"
DEFAULT_OLLAMA_MODEL = "gemma3:12b"

def build_prompt(examples: List[Dict], input_json: Dict) -> str:
    """プロンプトを構築する"""
    prompt = """
以下はゲームシナリオや関連コンテンツのJSONデータを特定の形式に整形する例です。
以下の情報を抽出・整形してください：

1. game_type: タイトルや説明文から「TRPG」「マーダーミステリー」「その他」のいずれかを判断
2. gm_required: 説明文からGM必要性（「必要」「不要」「どちらでも可」のいずれか）
3. min_players, max_players: 最小・最大プレイ人数
4. play_time: プレイ時間（最短と平均）を分単位で数値化
5. title: タイトルから【】などの記号を取り除いてシンプルに

元のデータと整形後のデータの例を示します：
"""
    
    for i, example in enumerate(examples, 1):
        prompt += f"\n例 {i}:\n"
        prompt += f"入力: {json.dumps(example['input'], ensure_ascii=False, indent=2)}\n"
        prompt += f"出力: {json.dumps(example['output'], ensure_ascii=False, indent=2)}\n"
    
    prompt += f"\n新しい入力:\n{json.dumps(input_json, ensure_ascii=False, indent=2)}\n\n"
    prompt += "新しい出力（整形されたJSON）を作成してください。JSONフォーマットのみを返してください。"
    
    return prompt

def get_examples() -> List[Dict]:
    """フォーマット例を取得する"""
    return [
        {
            "input": {
                "url": "https://booth.pm/ja/items/2867487",
                "id": "2867487",
                "title": "ヘンペルのカラス【2人協力型マーダーミステリー】",
                "price": 500,
                "likes": 1679,
                "author": "らしょちゃんshop",
                "description": "２人協力型マーダーミステリー 「ヘンペルのカラス」\nPL2＋GM\nタイムアタック：最短75分〜（読み込み時間含む。平均120分）\nオフライン＆オンライン　\n\n＜キャラクター＞\nHO1：青年\nHO2: 少女\n\n＜あらすじ＞\n２人は森の中で出会いました。\nそれぞれ、目的があるようです。",
                "thumbnail_url": "https://example.com/thumbnail1.jpg"
            },
            "output": {
                "url": "https://booth.pm/ja/items/2867487",
                "id": "2867487",
                "title": "ヘンペルのカラス",
                "price": 500,
                "likes": 1679,
                "author": "らしょちゃんshop",
                "game_type": "マーダーミステリー",
                "gm_required": "必要",
                "min_players": 2,
                "max_players": 3,
                "play_time": {
                    "min": 75,
                    "avg": 120
                },
                "thumbnail_url": "https://example.com/thumbnail1.jpg"
            }
        },
        {
            "input": {
                "url": "https://booth.pm/ja/items/4374013",
                "id": "4374013",
                "title": "【支援用SS】「ふわふわクリームさらにジューシー」ショートストーリー",
                "price": 1500,
                "likes": 851,
                "author": "ahashop",
                "description": "マーダーミステリー「ふわふわクリームさらにジューシー」支援用SS(ショートストーリー）です。\n\n※本作品は、ゲームではありません。\n※本編のネタバレを含みます。未プレイの方はご注意下さい。\n\n※本編URL：\nhttps://booth.pm/ja/items/4358468",
                "thumbnail_url": "https://example.com/thumbnail2.jpg"
            },
            "output": {
                "url": "https://booth.pm/ja/items/4374013",
                "id": "4374013",
                "title": "「ふわふわクリームさらにジューシー」ショートストーリー",
                "price": 1500,
                "likes": 851,
                "author": "ahashop",
                "game_type": "その他",
                "gm_required": "不要",
                "min_players": 0,
                "max_players": 0,
                "play_time": {
                    "min": 0,
                    "avg": 0
                },
                "thumbnail_url": "https://example.com/thumbnail2.jpg"
            }
        }
    ]

def extract_json_from_response(response_text: str) -> Optional[Dict]:
    """テキストレスポンスからJSONを抽出して解析"""
    json_str = response_text.strip()
    
    # コードブロック内のJSONを抽出
    if '```' in json_str:
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', json_str)
        if json_match:
            json_str = json_match.group(1)
    
    try:
        # JSONを解析
        return json.loads(json_str)
    except json.JSONDecodeError:
        # 余分なテキストを除去して再試行
        try:
            clean_text = re.sub(r'^[^{]*({.*})[^}]*$', r'\1', json_str, flags=re.DOTALL)
            return json.loads(clean_text)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON from response: {json_str}")
            return None

def format_json_with_api(input_json: Dict, api_type: str, model_name: str, examples: Optional[List[Dict]] = None, retries: int = 3, backoff_factor: int = 2) -> Optional[Dict]:
    """APIを使用してJSONを整形"""
    if examples is None:
        examples = get_examples()
    
    prompt = build_prompt(examples, input_json)
    
    for attempt in range(retries):
        try:
            if api_type == API_TYPE_GEMINI:
                return format_with_gemini(prompt, model_name)
            elif api_type == API_TYPE_OLLAMA:
                return format_with_ollama(prompt, model_name)
            else:
                print(f"Unsupported API type: {api_type}")
                sys.exit(1)
                
        except Exception as e:
            error_str = str(e)
            if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
                wait_time = (backoff_factor ** attempt) * 5
                print(f"Rate limit reached. Waiting for {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue
            elif attempt < retries - 1:
                wait_time = (backoff_factor ** attempt) * 1
                print(f"API call failed. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            else:
                print(f"API call failed after {retries} attempts: {e}")
                return None

def process_file(file_path: str, output_dir: str, api_type: str, model_name: str, examples: Optional[List[Dict]] = None, delay: float = 4) -> int:
    """ファイルを処理"""
    try:
        # 入力ファイルを読み込み
        with open(file_path, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
        
        # 出力ディレクトリが存在しない場合は作成
        os.makedirs(output_dir, exist_ok=True)
        
        # 出力ファイルパスを決定
        output_file = os.path.join(output_dir, os.path.basename(file_path))
        
        # データタイプに基づいて処理
        if isinstance(input_data, list):
            # 配列の場合は各アイテムを処理し、すぐ保存する
            os.makedirs(output_dir, exist_ok=True)
            results = []
            for item in tqdm(input_data, desc=f"Processing {file_path}", unit="item"):
                formatted_item = format_json_with_api(item, api_type, model_name, examples)
                if formatted_item:
                    title = formatted_item.get("title","タイトルなし")
                    print(f"成功： \"{title}\"の整形が完了")
                    results.append(formatted_item)
                    append_to_json(formatted_item, output_file)
                    print(f"アイテム処理完了： {formatted_item.get('title','不明なタイトル')}")
                time.sleep(delay)  # APIリクエスト間の遅延
            

            return len(results)
        else:
            # 単一オブジェクトの場合
            formatted_data = format_json_with_api(input_data, api_type, model_name, examples)
            if formatted_data:
                # 結果を保存
                title = formatted_data.get("title","タイトルなし")
                print(f"成功： \"{title}\"の整形が完了")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(formatted_data, f, ensure_ascii=False, indent=2)
                return 1
            return 0
            
    except Exception as e:
        print(f"ファイル処理エラー{file_path}: {e}")
        return 0

def process_directory(input_dir: str, output_dir: str, api_type: str, model_name: str, examples: Optional[List[Dict]] = None, max_workers: int = 1, delay: float = 4) -> int:
    """ディレクトリ内のすべてのJSONファイルを処理"""
    # 出力ディレクトリが存在しない場合は作成
    os.makedirs(output_dir, exist_ok=True)
    
    # 入力ディレクトリ内のすべてのJSONファイルを検索
    json_files = list(Path(input_dir).glob('**/*.json'))
    
    if not json_files:
        print(f"No JSON files found in {input_dir}")
        return 0
    
    print(f"Found {len(json_files)} JSON files to process")
    
    # 単一ワーカーの場合はシーケンシャルに処理
    if max_workers <= 1:
        processed_count = 0
        for file in tqdm(json_files, desc="Processing files", unit="file"):
            try:
                result_count = process_file(str(file), output_dir, api_type, model_name, examples, delay)
                processed_count += result_count
                print(f"Processed {file}: {result_count} items")
            except Exception as e:
                print(f"Error processing {file}: {e}")
        
        return processed_count
    
    # 複数ワーカーの場合は並列処理
    else:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        processed_count = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # すべての処理タスクを送信
            future_to_file = {
                executor.submit(process_file, str(file), output_dir, api_type, model_name, examples, delay): file
                for file in json_files
            }
            
            # 完了したタスクの結果を処理
            for future in tqdm(as_completed(future_to_file), total=len(json_files), desc="Processing files", unit="file"):
                file = future_to_file[future]
                try:
                    result_count = future.result()
                    processed_count += result_count
                    print(f"完了：{file}から{result_count}件の処理が終了しました。")
                except Exception as e:
                    print(f"Error processing {file}: {e}")
        
        return processed_count