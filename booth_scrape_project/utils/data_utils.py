"""
データの保存と処理に関するユーティリティ関数
"""
import os
import json
from typing import List, Dict, Any, Union, Optional


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
    # 必要なフィールドがあるか確認
    for field in ["title", "price", "url", "id"]:
        if field not in item_info:
            item_info[field] = None

    # 数値フィールドの型変換
    for field in ["price", "likes"]:
        if field in item_info and item_info[field] is not None:
            try:
                item_info[field] = int(item_info[field])
            except (ValueError, TypeError):
                item_info[field] = None

    return item_info


def append_to_json(item: Dict[str, Any], filename: str) -> None:
    """_summary_
    単一のアイテムをJson二追加する
    ファイルが存在しない場合新規作成、存在する場合は追加
    Args:
        item (Dict[str,Any]): _description_
        filename (str): _description_
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    existing_data = []
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            existing_data = json.load(f)

    # append data and save it
    existing_data.append(item)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
