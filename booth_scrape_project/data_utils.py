"""
データの保存と処理に関するユーティリティ関数
"""
import os
import json
from typing import Dict, List, Any, Optional, Union

def save_to_json(data: List[Dict[str, Any]], filename: str) -> None:
    """
    データをJSONファイルに保存する
    
    Args:
        data: 保存するデータ
        filename: 保存先ファイル名
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"{len(data)}件のデータを {filename} に保存しました")

def load_from_json(filename: str) -> List[Dict[str, Any]]:
    """
    JSONファイルからデータを読み込む
    
    Args:
        filename: 読み込むファイル名
        
    Returns:
        読み込んだデータ
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def format_item_data(item_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    アイテム情報を整形する
    
    Args:
        item_info: 整形前のアイテム情報
        
    Returns:
        整形後のアイテム情報
    """
    # 必須フィールドの定義
    required_fields: List[str] = ["title", "price", "url", "id"]
    
    # 数値型に変換すべきフィールドの定義
    integer_fields: List[str] = ["price", "likes"]
    
    # 文字列型に変換すべきフィールドの定義
    string_fields: List[str] = ["title", "author", "description", "id"]
    
    # 必要なフィールドがあるか確認し、なければNoneを設定
    for field in required_fields:
        if field not in item_info:
            item_info[field] = None
    
    # 数値フィールドの型変換
    for field in integer_fields:
        if field in item_info and item_info[field] is not None:
            try:
                item_info[field] = int(item_info[field])
            except (ValueError, TypeError):
                item_info[field] = None
    
    # 文字列フィールドの型変換
    for field in string_fields:
        if field in item_info and item_info[field] is not None:
            try:
                item_info[field] = str(item_info[field])
            except (ValueError, TypeError):
                item_info[field] = None
    
    # 一部の特殊なフィールドの処理（例：タイムスタンプなど）
    # このセクションには必要に応じて特殊なフィールド処理を追加できます
    
    return item_info