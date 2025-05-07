"""
Google Gemini APIを利用したフォーマット機能
"""
import os
import sys
from typing import Dict, Optional
from pathlib import Path
from dotenv import load_dotenv


def format_with_gemini(prompt: str, model_name: str) -> Optional[Dict]:
    """Gemini APIを使用してプロンプトを処理"""
    try:
        from google import genai
        from google.genai import types

        # .envファイルを明示的に読み込む
        # カレントディレクトリから見て上位の.envを探す
        env_paths = [
            Path(".env"),                     # カレントディレクトリ
            Path("../.env"),                  # 1つ上の階層
            Path("../../.env"),               # 2つ上の階層
            Path(__file__).parent.parent.parent / ".env"  # コードからの相対パス
        ]

        env_loaded = False
        for path in env_paths:
            if path.exists():
                load_dotenv(path)
                print(f"環境変数を読み込みました: {path}")
                env_loaded = True
                break

        if not env_loaded:
            print("警告: .envファイルが見つかりませんでした")
            

        # 環境変数を取得
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print(
                "GEMINI_API_KEY が環境変数に設定されていません。.envファイルを確認してください。")
            sys.exit(1)

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                top_k=40,
                top_p=0.95,
            )
        )

        return response.text

    except ImportError:
        print("google-generativeai package is not installed. Run: pip install google-generativeai")
        sys.exit(1)
    except Exception as e:
        print(f"Error in Gemini API call: {e}")
        sys.exit(1)
