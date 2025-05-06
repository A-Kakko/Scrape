# API切り替え機能を追加した部分

import os
import argparse
from pathlib import Path
from dotenv import load_dotenv
import json
import re
import time
import requests
from tqdm import tqdm

# 環境変数の読み込み
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api")

# APIのタイプを定義
API_TYPE_GEMINI = "gemini"
API_TYPE_OLLAMA = "ollama"

# モデル設定
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash-001"
DEFAULT_OLLAMA_MODEL = "gemma3:12b"

# APIクライアントの初期化
def initialize_client(api_type):
    """APIタイプに基づいてクライアントを初期化"""
    if api_type == API_TYPE_GEMINI:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        
        try:
            from google import genai
            return genai.Client(api_key=GEMINI_API_KEY)
        except ImportError:
            raise ImportError("google-generativeai package is not installed. Run: pip install google-generativeai")
    
    elif api_type == API_TYPE_OLLAMA:
        # Ollamaはリクエストごとに直接APIを呼び出すため、クライアントオブジェクトは不要
        # OllamaのAPIが利用可能かテスト
        try:
            response = requests.get(f"{OLLAMA_API_URL}/tags")
            if response.status_code != 200:
                raise ConnectionError(f"Failed to connect to Ollama API at {OLLAMA_API_URL}")
            return True
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to connect to Ollama API: {e}")
    
    else:
        raise ValueError(f"Unsupported API type: {api_type}")

# APIを使用してJSONを整形
def format_json_with_api(input_json, api_type, model_name, examples=None, retries=3, backoff_factor=2):
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
                raise ValueError(f"Unsupported API type: {api_type}")
                
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

# Gemini APIを使用して整形
def format_with_gemini(prompt, model_name):
    """Gemini APIを使用してプロンプトを処理"""
    from google import genai
    from google.genai import types
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            top_k=40,
            top_p=0.95,
        )
    )
    
    # レスポンスからJSONを抽出
    return extract_json_from_response(response.text)

# Ollama APIを使用して整形
def format_with_ollama(prompt, model_name):
    """Ollama APIを使用してプロンプトを処理"""
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(
        f"{OLLAMA_API_URL}/generate",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        raise Exception(f"Ollama API returned status code {response.status_code}: {response.text}")
    
    response_json = response.json()
    response_text = response_json.get("response", "")
    
    # レスポンスからJSONを抽出
    return extract_json_from_response(response_text)

# レスポンスからJSONを抽出
def extract_json_from_response(response_text):
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

# メイン関数の修正
def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Format JSON data using AI APIs')
    parser.add_argument('input', help='Input JSON file or directory')
    parser.add_argument('--output', '-o', help='Output directory (default: formatted_output)', default='formatted_output')
    parser.add_argument('--workers', '-w', type=int, help='Number of parallel workers (default: 1)', default=1)
    parser.add_argument('--delay', '-d', type=float, help='Delay between API calls in seconds (default: 4)', default=4)
    parser.add_argument('--api', '-a', choices=[API_TYPE_GEMINI, API_TYPE_OLLAMA], default=API_TYPE_GEMINI,
                        help=f'API to use (default: {API_TYPE_GEMINI})')
    parser.add_argument('--model', '-m', help='Model name (defaults depend on API type)', default=None)
    
    args = parser.parse_args()
    
    # APIタイプに基づいてデフォルトモデルを設定
    if args.model is None:
        if args.api == API_TYPE_GEMINI:
            args.model = DEFAULT_GEMINI_MODEL
        elif args.api == API_TYPE_OLLAMA:
            args.model = DEFAULT_OLLAMA_MODEL
    
    # APIクライアントを初期化
    try:
        initialize_client(args.api)
        print(f"Successfully initialized {args.api.capitalize()} API")
        print(f"Using model: {args.model}")
    except Exception as e:
        print(f"Failed to initialize {args.api.capitalize()} API: {e}")
        return
    
    # 例を読み込み
    examples = get_examples()
    
    # 入力パスを処理
    start_time = time.time()
    input_path = Path(args.input)
    
    if input_path.is_file():
        print(f"Processing single file: {input_path}")
        count = process_file(str(input_path), args.output, args.api, args.model, examples, args.delay)
        print(f"Successfully processed {count} items")
    elif input_path.is_dir():
        print(f"Processing directory: {input_path}")
        count = process_directory(str(input_path), args.output, args.api, args.model, examples, 
                                  args.workers, args.delay)
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

# process_file関数の修正
def process_file(file_path, output_dir, api_type, model_name, examples=None, delay=4):
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
            # 配列の場合は各アイテムを処理
            results = []
            for item in tqdm(input_data, desc=f"Processing {file_path}", unit="item"):
                formatted_item = format_json_with_api(item, api_type, model_name, examples)
                if formatted_item:
                    results.append(formatted_item)
                time.sleep(delay)  # APIリクエスト間の遅延
            
            # 結果を保存
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            return len(results)
        else:
            # 単一オブジェクトの場合
            formatted_data = format_json_with_api(input_data, api_type, model_name, examples)
            if formatted_data:
                # 結果を保存
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(formatted_data, f, ensure_ascii=False, indent=2)
                return 1
            return 0
            
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return 0

# process_directory関数の修正
def process_directory(input_dir, output_dir, api_type, model_name, examples=None, max_workers=1, delay=4):
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
                    print(f"Processed {file}: {result_count} items")
                except Exception as e:
                    print(f"Error processing {file}: {e}")
        
        return processed_count