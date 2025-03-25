"""
BOOTHウェブサイトからデータをスクレイピングするクラス
"""
import requests
from bs4 import BeautifulSoup as bs4
import time
import random
import urllib.parse
from typing import Dict, List, Optional, Any, Union
from booth_likes import get_booth_likes
import config


class BoothScraper:
    """BOOTHからデータをスクレイピングするクラス"""

    def __init__(self) -> None:
        """初期化"""
        self.headers: Dict[str, str] = config.HEADERS

    def get_search_url(self, keyword: str, page: int = 1) -> str:
        """
        検索ページのURLを構築する

        Args:
            keyword: 検索キーワード
            page: ページ番号

        Returns:
            検索ページのURL
        """
        encoded_keyword = urllib.parse.quote(keyword)
        if page == 1:
            return f"{config.BASE_URL}/ja/search/{encoded_keyword}"
        else:
            return f"{config.BASE_URL}/ja/search/{encoded_keyword}?page={page}"

    def get_item_links_from_search(self, search_url: str) -> List[Dict[str, Any]]:
        """
        検索結果ページから商品リンクを取得する

        Args:
            search_url: 検索結果ページのURL

        Returns:
            商品情報のリスト（URL、ID、タイトル、価格を含む）
        """
        print(f"検索ページにアクセス中: {search_url}")
        try:
            response = requests.get(search_url, headers=self.headers)
            response.raise_for_status()

            soup = bs4(response.text, "html.parser")

            # ページタイトルを表示
            page_title = soup.title.text if soup.title else "タイトルなし"
            print(f"ページタイトル: {page_title}")

            # 商品カードを探す
            item_cards = soup.select("li.item-card")
            print(f"検索結果から {len(item_cards)} 件のアイテムカードを発見")

            item_links: List[Dict[str, Any]] = []
            for card in item_cards:
                # タイトルリンクを取得
                title_link = card.select_one(
                    "a.item-card__title-anchor--multiline")
                if title_link and title_link.get("href"):
                    item_url = title_link.get("href")
                    if not item_url.startswith("http"):
                        item_url = f"{config.BASE_URL}{item_url}"

                    # 基本情報を取得
                    product_id = card.get("data-product-id", "")
                    product_name = card.get("data-product-name", "")
                    product_price = card.get("data-product-price", "")

                    print(f"アイテム発見: {product_name} (ID: {product_id})")

                    item_links.append({
                        "url": item_url,
                        "id": product_id,
                        "title": product_name,
                        "price": product_price
                    })

            return item_links

        except Exception as e:
            print(f"検索ページのアクセスエラー: {str(e)}")
            return []

    def scrape_item_page(self, item_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        商品ページから詳細情報をスクレイピングする

        Args:
            item_info: 基本的な商品情報（URL、ID、タイトル、価格を含む）

        Returns:
            詳細な商品情報（上記に加えてスキ数、作者、説明、サムネイルURLを含む）
        """
        url = item_info["url"]
        print(f"商品ページにアクセス中: {url}")

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            soup = bs4(response.text, "html.parser")

            # スキの数取得
            likes: Optional[int] = get_booth_likes(url)

            # 作者情報取得
            author: str = item_info.get("author", "Unknown")
            author_elem = soup.select_one(
                ".u-text-ellipsis") or soup.select_one(".item-card__shop-name")
            if author_elem:
                author = author_elem.text.strip()

            # 説明文取得
            description: str = ""
            desc_elem = soup.select_one(
                ".description") or soup.select_one(".item-description")
            if desc_elem:
                description = desc_elem.text.strip()
                
            # サムネイル画像URL取得
            thumbnail_url: Optional[str] = None
            main_image = soup.select_one(".item-view__image-link img")

            # main_image が None でない場合に処理を進める
            if main_image and isinstance(main_image, bs4.element.Tag):
                # get メソッドで取得した値が str 型か確認
                src = main_image.get("src")
                data_original = main_image.get("data-original")
                if isinstance(src, str):
                    thumbnail_url = src
                elif isinstance(data_original, str):
                    thumbnail_url = data_original

            # サムネイル画像が見つからない場合のフォールバック処理
            if not thumbnail_url:
                for img in soup.find_all("img"):
                    if isinstance(img, bs4.element.Tag):
                        src = img.get("src", "")
                        if isinstance(src, str) and ("market" in src or "pximg" in src):
                            thumbnail_url = src
                            break

            # 詳細データを更新
            item_info.update({
                "likes": likes,
                "author": author,
                "description": description,
                "thumbnail_url": thumbnail_url
            })

            print(f"収集完了: {item_info['title']} (スキ数: {likes})")
            return item_info

        except Exception as e:
            print(f"商品ページのアクセスエラー: {url} - {str(e)}")
            return item_info

    def wait_random_time(self, min_time: Optional[float] = None, max_time: Optional[float] = None) -> None:
        """
        ランダムな時間待機する

        Args:
            min_time: 最小待機時間
            max_time: 最大待機時間
        """
        min_time = min_time or config.WAIT_TIME_MIN
        max_time = max_time or config.WAIT_TIME_MAX
        wait_time = random.uniform(min_time, max_time)
        print(f"{wait_time:.1f}秒待機中...")
        time.sleep(wait_time)
