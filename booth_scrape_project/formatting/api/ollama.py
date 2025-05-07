"""
Ollama APIを利用したフォーマット機能
"""
import os
import requests
from typing import Dict, Optional

def format_with_ollama(prompt: str, model_name: str) -> Optional[Dict]:
    """Ollama APIを使用してプロンプトを処理"""
    api_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api")
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(
            f"{api_url}/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        response.raise_for_status()
        
        response_json = response.json()
        return response_json.get("response", "")
        
    except requests.RequestException as e:
        raise Exception(f"Error in Ollama API call: {e}")