# JSON Formatter using Gemini API
# This script formats JSON data from a file or directory using Gemini API with few-shot learning
# The API key is loaded from a .env file
import os
import argparse
from pathlib import Path
from dotenv import load_dotenv
from google import genai
import json
import re
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load API key from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Check if API key is loaded correctly
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# Initialize the client
client = genai.Client(api_key=GEMINI_API_KEY)

# Model to use
MODEL_NAME = "gemini-2.0-flash-001"

# Define few-shot examples


def get_examples():
    """Returns example pairs of input and expected output for few-shot learning"""
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
                "thumbnail_url": "https://booth.pximg.net/c/48x48/users/819984/icon_image/155d25a9-c506-4de0-81cb-28d86cb0da02_base_resized.jpg"
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
                "thumbnail_url": "https://booth.pximg.net/c/48x48/users/819984/icon_image/155d25a9-c506-4de0-81cb-28d86cb0da02_base_resized.jpg"
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
                "thumbnail_url": "https://booth.pximg.net/c/48x48/users/10875563/icon_image/3e1d5c0b-f980-45fd-99b1-058037c52f6f_base_resized.jpg"
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
                "thumbnail_url": "https://booth.pximg.net/c/48x48/users/10875563/icon_image/3e1d5c0b-f980-45fd-99b1-058037c52f6f_base_resized.jpg"
            }
        },
        {
            "input": {
                "url": "https://booth.pm/ja/items/3000123",
                "id": "3000123",
                "title": "サンシャイン・オブ・ザ・デッド【TRPG初心者向けゾンビシナリオ】",
                "price": 800,
                "likes": 325,
                "author": "TRPGクリエイターズ",
                "description": "TRPG初心者にもおすすめなゾンビものシナリオ「サンシャイン・オブ・ザ・デッド」\n\nプレイヤー：3～5人\nGMが必要です\n推定プレイ時間：3～4時間\n\n内容：\n・シナリオ本編PDF\n・キャラクターシート\n・導入用マップ\n・GMガイド\n\nシステムはCoC 7版を使用します。",
                "thumbnail_url": "https://example.com/thumbnail3.jpg"
            },
            "output": {
                "url": "https://booth.pm/ja/items/3000123",
                "id": "3000123",
                "title": "サンシャイン・オブ・ザ・デッド",
                "price": 800,
                "likes": 325,
                "author": "TRPGクリエイターズ",
                "game_type": "TRPG",
                "gm_required": "必要",
                "min_players": 3,
                "max_players": 5,
                "play_time": {
                    "min": 180,
                    "avg": 210
                },
                "thumbnail_url": "https://example.com/thumbnail3.jpg"
            }
        }
    ]


def build_prompt(examples, input_json):
    """Build a prompt for the Gemini API with few-shot examples"""
    prompt = """
以下はゲームシナリオや関連コンテンツのJSONデータを特定の形式に整形する例です。
以下の情報を抽出・整形してください：

1. game_type: タイトルや説明文から「TRPG」「マーダーミステリー」「その他」のいずれかを判断
2. gm_required: 説明文からGM必要性（「必要」「不要」「どちらでも可」のいずれか）
3. min_players, max_players: 最小・最大プレイ人数
4. play_time: プレイ時間（最短と平均）を分単位で数値化
5. title: タイトルから【】、「」、『』などの記号を取り除いてシンプルに

元のデータと整形後のデータの例を示します：
"""

    for i, example in enumerate(examples, 1):
        prompt += f"\n例 {i}:\n"
        prompt += f"入力: {json.dumps(example['input'], ensure_ascii=False, indent=2)}\n"
        prompt += f"出力: {json.dumps(example['output'], ensure_ascii=False, indent=2)}\n"

    prompt += f"\n新しい入力:\n{json.dumps(input_json, ensure_ascii=False, indent=2)}\n\n"
    prompt += """
新しい出力（整形されたJSON）を作成してください。
説明文から以下の情報を正確に抽出してください：
- game_type: タイトルや説明文からゲームの種類を「TRPG」「マーダーミステリー」「その他」のいずれかで判定
- gm_required: GM必要性（「必要」「不要」「どちらでも可」のいずれか）
- min_players, max_players: 最小・最大プレイ人数(GM込みで必要な最少人数、GMレス可ならその場合の人数)
- play_time: プレイ時間を分単位で表現（最短minと平均avg）

タイトルは【】などの記号を取り除き、シンプルにしてください。
JSONフォーマットのみを返してください。説明や解説は不要です。
"""

    return prompt


def format_json_with_gemini(input_json, examples=None, retries=3):
    """Format a JSON object using Gemini API with few-shot learning"""
    if examples is None:
        examples = get_examples()

    prompt = build_prompt(examples, input_json)

    # Set parameters for more controlled generation
    from google.genai import types

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,  # Lower temperature for more deterministic outputs
                    top_k=40,
                    top_p=0.95,
                )
            )

            # Extract JSON from response
            json_str = response.text.strip()
            if '```' in json_str:
                json_match = re.search(
                    r'```(?:json)?\s*([\s\S]*?)\s*```', json_str)
                if json_match:
                    json_str = json_match.group(1)

            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                if attempt < retries - 1:
                    time.sleep(1)  # Wait a bit before retrying
                    continue
                else:
                    print(
                        f"Failed to parse JSON response after {retries} attempts: {e}")
                    print(f"Response text: {json_str}")
                    return None

        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1)  # Wait a bit before retrying
                continue
            else:
                print(f"API call failed after {retries} attempts: {e}")
                return None


def process_file(file_path, output_dir, examples=None):
    """Process a single JSON file"""
    try:
        # Read input file
        with open(file_path, 'r', encoding='utf-8') as f:
            input_data = json.load(f)

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Determine output file path
        output_file = os.path.join(output_dir, os.path.basename(file_path))

        # Process input data (single object or array)
        if isinstance(input_data, list):
            # Process array of objects
            results = []
            for item in tqdm(input_data, desc=f"Processing {file_path}", unit="item"):
                formatted_item = format_json_with_gemini(item, examples)
                if formatted_item:
                    results.append(formatted_item)

            # Save results
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            return len(results)
        else:
            # Process single object
            formatted_data = format_json_with_gemini(input_data, examples)
            if formatted_data:
                # Save result
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(formatted_data, f, ensure_ascii=False, indent=2)
                return 1
            return 0

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return 0


def process_directory(input_dir, output_dir, examples=None, max_workers=2, throttle_delay=4):
    """Process all JSON files in a directory with rate limiting"""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all JSON files in the input directory
    json_files = list(Path(input_dir).glob('**/*.json'))
    
    if not json_files:
        print(f"No JSON files found in {input_dir}")
        return 0
    
    print(f"Found {len(json_files)} JSON files to process")
    
    # レート制限を避けるために、並列ワーカー数を減らし、処理間に遅延を追加
    processed_count = 0
    
    # 単一ファイルごとに処理して、各ファイル間に遅延を追加
    for file in tqdm(json_files, desc="Processing files", unit="file"):
        try:
            result_count = process_file(str(file), output_dir, examples)
            processed_count += result_count
            print(f"Processed {file}: {result_count} items")
            
            # レート制限を避けるために各ファイル処理後に待機
            time.sleep(throttle_delay)
            
        except Exception as e:
            print(f"Error processing {file}: {e}")
    
    return processed_count


# 遅延機能を追加してレート制限に対応
def format_json_with_gemini(input_json, examples=None, model_name=MODEL_NAME, retries=3, backoff_factor=2):
    """Format a JSON object using Gemini API with few-shot learning"""
    if examples is None:
        examples = get_examples()
    
    prompt = build_prompt(examples, input_json)
    
    # Set parameters for more controlled generation
    from google.genai import types
    
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,  # Lower temperature for more deterministic outputs
                    top_k=40,
                    top_p=0.95,
                )
            )
            
            # Extract JSON from response
            json_str = response.text.strip()
            if '```' in json_str:
                json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', json_str)
                if json_match:
                    json_str = json_match.group(1)
            
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                if attempt < retries - 1:
                    time.sleep(1)  # Wait a bit before retrying
                    continue
                else:
                    print(f"Failed to parse JSON response after {retries} attempts: {e}")
                    print(f"Response text: {json_str}")
                    return None
                
        except Exception as e:
            error_str = str(e)
            if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
                # レート制限に達した場合、待機時間を増やす
                wait_time = (backoff_factor ** attempt) * 5  # 5秒、10秒、20秒...と指数関数的に増加
                print(f"Rate limit reached. Waiting for {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue
            elif attempt < retries - 1:
                time.sleep(1)  # Wait a bit before retrying
                continue
            else:
                print(f"API call failed after {retries} attempts: {e}")
                return None
            
def main():
    """Main function to parse arguments and run the formatter"""
    global MODEL_NAME
    
    parser = argparse.ArgumentParser(description='Format JSON data using Gemini API')
    parser.add_argument('input', help='Input JSON file or directory')
    parser.add_argument('--output', '-o', help='Output directory (default: formatted_output)', default='formatted_output')
    parser.add_argument('--workers', '-w', type=int, help='Number of parallel workers (default: 2)', default=2)
    parser.add_argument('--model', '-m', help=f'Gemini model to use (default: {MODEL_NAME})', default=MODEL_NAME)
    parser.add_argument('--delay', '-d', type=float, help='Delay between API calls in seconds (default: 4)', default=4)
    parser.add_argument('--batch-size', '-b', type=int, help='Process items in batches of this size (default: 10)', default=10)
    
    args = parser.parse_args()
    
    # Update model name if specified
    MODEL_NAME = args.model
    
    # Load examples
    examples = get_examples()
    
    start_time = time.time()
    
    # Check if input is a file or directory
    input_path = Path(args.input)
    if input_path.is_file():
        print(f"Processing single file: {input_path}")
        count = process_file(str(input_path), args.output, examples)
        print(f"Successfully processed {count} items")
    elif input_path.is_dir():
        print(f"Processing directory: {input_path}")
        count = process_directory(str(input_path), args.output, examples, args.workers, args.delay)
        print(f"Successfully processed {count} items from {input_path}")
    else:
        print(f"Input path {args.input} does not exist")
        return
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"Total processing time: {duration:.2f} seconds")
    if count > 0:
        print(f"Average time per item: {duration/count:.2f} seconds")
    print(f"Results saved to {args.output}")

if __name__ == '__main__':
    main()
