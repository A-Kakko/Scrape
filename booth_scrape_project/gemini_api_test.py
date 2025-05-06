# Gemini API Few-Shot Test
# This script demonstrates how to use the Gemini API with few-shot learning
# The API key is loaded from a .env file
import os
from dotenv import load_dotenv
from google import genai
import json
import re
import time

# Load API key from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Check if API key is loaded correctly
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# Initialize the client
client = genai.Client(api_key=GEMINI_API_KEY)

def test_few_shot_simple():
    """Test few-shot learning with a simple color-object example"""
    try:
        # Few-shot examples
        examples = [
            {"input": "赤いリンゴ", "output": {"item": "リンゴ", "color": "赤"}},
            {"input": "青い空", "output": {"item": "空", "color": "青"}}
        ]
        
        # Construct prompt with examples
        prompt = "以下は入力と出力の例です。同じパターンで新しい入力を処理してください。\n\n"
        
        for example in examples:
            prompt += f"入力: {example['input']}\n"
            prompt += f"出力: {json.dumps(example['output'], ensure_ascii=False)}\n\n"
        
        prompt += "新しい入力: 緑の芝生\n"
        prompt += "新しい出力:"
        
        start_time = time.time()
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=prompt
        )
        end_time = time.time()
        
        print("=== Few-Shot Simple Test ===")
        print(f"Prompt: {prompt}")
        print(f"Response time: {end_time - start_time:.2f} seconds")
        print(f"Response: {response.text}")
        
        # Try to parse the response as JSON
        try:
            # Remove any code block markers
            json_str = response.text.strip()
            if '```' in json_str:
                json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', json_str)
                if json_match:
                    json_str = json_match.group(1)
            
            parsed_json = json.loads(json_str)
            print(f"Parsed JSON: {json.dumps(parsed_json, ensure_ascii=False, indent=2)}")
            print("✓ Successfully parsed response as JSON")
        except json.JSONDecodeError as e:
            print(f"× Failed to parse response as JSON: {e}")
        
        print("\n")
        return True
    except Exception as e:
        print(f"Error in few-shot simple test: {e}")
        return False

def test_few_shot_json_format():
    """Test few-shot learning for JSON formatting with game data"""
    try:
        # Few-shot examples
        examples = [
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
        
        # New input to process
        new_input = {
            "url": "https://booth.pm/ja/items/3000123",
            "id": "3000123",
            "title": "サンシャイン・オブ・ザ・デッド【TRPG初心者向けゾンビシナリオ】",
            "price": 800,
            "likes": 325,
            "author": "TRPGクリエイターズ",
            "description": "TRPG初心者にもおすすめなゾンビものシナリオ「サンシャイン・オブ・ザ・デッド」\n\nプレイヤー：3～5人\nGMが必要です\n推定プレイ時間：3～4時間\n\n内容：\n・シナリオ本編PDF\n・キャラクターシート\n・導入用マップ\n・GMガイド\n\nシステムはCoC 7版を使用します。",
            "thumbnail_url": "https://example.com/thumbnail3.jpg"
        }
        
        # Construct prompt with examples
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
        
        prompt += f"\n新しい入力:\n{json.dumps(new_input, ensure_ascii=False, indent=2)}\n\n"
        prompt += "新しい出力（整形されたJSON）を作成してください。JSONフォーマットのみを返してください。"
        
        # Set parameters for more controlled generation
        from google.genai import types
        
        start_time = time.time()
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,  # Lower temperature for more deterministic outputs
                top_k=40,
                top_p=0.95,
            )
        )
        end_time = time.time()
        
        print("=== Few-Shot JSON Format Test ===")
        print(f"Processing time: {end_time - start_time:.2f} seconds")
        print(f"Response: {response.text}")
        
        # Try to parse the response as JSON
        try:
            # Remove any code block markers
            json_str = response.text.strip()
            if '```' in json_str:
                json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', json_str)
                if json_match:
                    json_str = json_match.group(1)
            
            parsed_json = json.loads(json_str)
            print(f"Parsed JSON: {json.dumps(parsed_json, ensure_ascii=False, indent=2)}")
            print("✓ Successfully parsed response as JSON")
            
            # Additional validation
            required_fields = ["game_type", "gm_required", "min_players", "max_players", "play_time"]
            for field in required_fields:
                if field not in parsed_json:
                    print(f"× Field '{field}' is missing from the output JSON")
                    
            if "play_time" in parsed_json and isinstance(parsed_json["play_time"], dict):
                if "min" not in parsed_json["play_time"] or "avg" not in parsed_json["play_time"]:
                    print("× 'min' or 'avg' is missing from the 'play_time' object")
            
        except json.JSONDecodeError as e:
            print(f"× Failed to parse response as JSON: {e}")
        
        print("\n")
        return True
    except Exception as e:
        print(f"Error in few-shot JSON format test: {e}")
        return False

def test_few_shot_batch_processing():
    """Test few-shot learning with batch processing capability"""
    try:
        # Few-shot examples (same as test_few_shot_json_format)
        examples = [
            # Same examples as before
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
            }
        ]
        
        # Create a batch of inputs to process
        batch_inputs = [
            {
                "url": "https://booth.pm/ja/items/3000123",
                "id": "3000123",
                "title": "サンシャイン・オブ・ザ・デッド【TRPG初心者向けゾンビシナリオ】",
                "price": 800,
                "likes": 325,
                "author": "TRPGクリエイターズ",
                "description": "TRPG初心者にもおすすめなゾンビものシナリオ「サンシャイン・オブ・ザ・デッド」\n\nプレイヤー：3～5人\nGMが必要です\n推定プレイ時間：3～4時間\n\n内容：\n・シナリオ本編PDF\n・キャラクターシート\n・導入用マップ\n・GMガイド\n\nシステムはCoC 7版を使用します。",
                "thumbnail_url": "https://example.com/thumbnail3.jpg"
            },
            {
                "url": "https://booth.pm/ja/items/4000456",
                "id": "4000456",
                "title": "【無料配布】星空のセレナーデ",
                "price": 0,
                "likes": 125,
                "author": "星空工房",
                "description": "星空をテーマにした短編小説です。\n\n※本作品はゲームではありません。\nPDF形式でお楽しみください。\n約15分で読み終わる短編です。",
                "thumbnail_url": "https://example.com/thumbnail4.jpg"
            }
        ]
        
        # Function to format a single JSON using few-shot learning
        def format_json_with_few_shot(input_json, examples):
            prompt = """
以下はゲームシナリオや関連コンテンツのJSONデータを特定の形式に整形する例です。
説明文からゲーム種類、GM必要性、プレイ人数、プレイ時間を抽出し、タイトルから装飾を取り除いてください。

元のデータと整形後のデータの例を示します：
"""
            
            for i, example in enumerate(examples, 1):
                prompt += f"\n例 {i}:\n"
                prompt += f"入力: {json.dumps(example['input'], ensure_ascii=False, indent=2)}\n"
                prompt += f"出力: {json.dumps(example['output'], ensure_ascii=False, indent=2)}\n"
            
            prompt += f"\n新しい入力:\n{json.dumps(input_json, ensure_ascii=False, indent=2)}\n\n"
            prompt += "新しい出力（整形されたJSON）を作成してください。JSONフォーマットのみを返してください。"
            
            from google.genai import types
            
            response = client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
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
            except json.JSONDecodeError:
                return None
            
        print("=== Few-Shot Batch Processing Test ===")
        print(f"Processing {len(batch_inputs)} items...")
        
        results = []
        start_time = time.time()
        
        for i, input_json in enumerate(batch_inputs, 1):
            print(f"Processing item {i}/{len(batch_inputs)}...")
            item_start = time.time()
            formatted_json = format_json_with_few_shot(input_json, examples)
            item_end = time.time()
            
            if formatted_json:
                results.append(formatted_json)
                print(f"✓ Successfully processed item {i} in {item_end - item_start:.2f} seconds")
            else:
                print(f"× Failed to process item {i}")
        
        end_time = time.time()
        
        print(f"\nBatch processing completed in {end_time - start_time:.2f} seconds")
        print(f"Successfully processed {len(results)}/{len(batch_inputs)} items")
        
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        print("\n")
        return True
    except Exception as e:
        print(f"Error in few-shot batch processing test: {e}")
        return False

def run_all_tests():
    """Run all test functions and report results"""
    tests = [
        ("Few-Shot Simple Test", test_few_shot_simple),
        ("Few-Shot JSON Format Test", test_few_shot_json_format),
        ("Few-Shot Batch Processing Test", test_few_shot_batch_processing)
    ]
    
    results = {}
    for name, test_func in tests:
        print(f"Running {name}...")
        result = test_func()
        results[name] = "Success" if result else "Failed"
    
    print("\n=== Test Results Summary ===")
    for name, result in results.items():
        print(f"{name}: {result}")

if __name__ == "__main__":
    print("Starting Gemini API Few-Shot Learning tests...")
    run_all_tests()