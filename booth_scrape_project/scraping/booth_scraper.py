"""
BOOTHウェブサイトからデータをスクレイピングするクラス
"""
import urllib.parse
from typing import List, Dict, Optional, Any, Union
from bs4 import BeautifulSoup
import re
from scraping.base_scraper import BaseScraper
from scraping.interaction.likes import get_booth_likes
import config

class BoothScraper(BaseScraper):
    """BOOTHからデータをスクレイピングするクラス"""
    
    def __init__(self) -> None:
        """初期化"""
        super().__init__(headers=config.HEADERS)
        self.base_url = config.BASE_URL
        
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
            return f"{self.base_url}/ja/search/{encoded_keyword}"
        else:
            return f"{self.base_url}/ja/search/{encoded_keyword}?page={page}"
    
    def get_item_links_from_search(self, search_url: str) -> List[Dict[str, str]]:
        """
        検索結果ページから商品リンクのみを取得する
        
        Args:
            search_url: 検索結果ページのURL
            
        Returns:
            商品リンクのリスト（URLのみを含む）
        """
        print(f"検索ページにアクセス中: {search_url}")
        soup = self.get_page(search_url)
        if not soup:
            return []
            
        # ページタイトルを表示
        page_title = soup.title.text if soup.title else "タイトルなし"
        print(f"ページタイトル: {page_title}")
        
        # 商品カードを探す
        item_cards = soup.select("li.item-card")
        print(f"検索結果から {len(item_cards)} 件のアイテムカードを発見")
        
        item_links = []
        for card in item_cards:
            # タイトルリンクを取得
            title_link = card.select_one("a.item-card__title-anchor--multiline")
            if title_link and title_link.get("href"):
                item_url = title_link.get("href")
                if not item_url.startswith("http"):
                    item_url = f"{self.base_url}{item_url}"
                
                # 商品IDを取得（あれば）
                product_id = card.get("data-product-id", "")
                
                # 検索ページでのタイトルを取得（表示用のみ）
                display_title = title_link.text.strip() if title_link.text else "タイトルなし"
                
                print(f"アイテムリンク発見: {item_url} (ID: {product_id}, タイトル: {display_title})")
                
                item_links.append({
                    "url": item_url,
                    "id": product_id
                })
        
        return item_links
    
    def scrape_item_page(self, item_info: Dict[str, str]) -> Dict[str, Any]:
        """
        商品ページから詳細情報をスクレイピングする
        
        Args:
            item_info: 基本的な商品情報（URL、IDを含む）
            
        Returns:
            詳細な商品情報（タイトル、価格、スキ数、作者、説明、サムネイルURLを含む）
        """
        url = item_info["url"]
        print(f"商品ページにアクセス中: {url}")
        
        soup = self.get_page(url)
        if not soup:
            # エラー時も最低限の情報は返す
            item_info.update({
                "title": "取得エラー",
                "price": None,
                "likes": None,
                "author": "不明",
                "description": "取得エラー",
                "thumbnail_url": None
            })
            return item_info
        
        # タイトル取得
        title = "不明"
        # まずはページのtitleタグから取得を試みる
        if soup.title:
            title_text = soup.title.text.strip()
            # 「商品名 - 販売者名 - BOOTH」の形式から商品名を抽出
            if " - " in title_text:
                # 最後の「- BOOTH」を削除
                if title_text.endswith(" - BOOTH"):
                    title_text = title_text[:-9]
                
                # 最後の「- 販売者名」を削除
                if " - " in title_text:
                    title_text = title_text.rsplit(" - ", 1)[0]
                
                title = title_text.strip()
        
        # titleタグからの取得に失敗した場合はh1要素から取得
        if title == "不明":
            title_elem = soup.select_one("h1.item-header__title")
            if title_elem:
                title = title_elem.text.strip()
        
        # 価格取得
        price: Optional[Union[int, str]] = None
        price_elem = soup.select_one(".price")
        if price_elem:
            price_text = price_elem.text.strip()
            # 価格から数字のみを抽出
            price_digits = ''.join(filter(str.isdigit, price_text))
            if price_digits:
                price = int(price_digits)
        
        # スキの数取得
        likes = get_booth_likes(url)
        
        # 作者情報取得
        author = "不明"
        author_elem = soup.select_one(".shop-name") or soup.select_one(".u-text-ellipsis")
        if author_elem:
            author = author_elem.text.strip()
        
        # 説明文取得の改善
        description = ""
        
        # 1. まず短い説明文を取得（メイン説明文）
        short_desc_elem = soup.select_one(".js-market-item-detail-description .description") or \
                        soup.select_one(".js-market-item-detail-description .autolink")
        if short_desc_elem:
            description += short_desc_elem.text.strip() + "\n\n"
        
        # 2. 詳細説明文を取得（セクション構造）
        detailed_sections = soup.select("section.shop__text")
        if detailed_sections:
            for section in detailed_sections:
                # セクションの見出し取得
                heading = section.select_one("h2")
                if heading:
                    description += f"**{heading.text.strip()}**\n"
                
                # セクションの本文取得
                content = section.select_one("p")
                if content:
                    description += f"{content.text.strip()}\n\n"
        
        # 3. 別の構造の説明文も探してみる（バックアップ）
        if not description:
            alt_desc_elem = soup.select_one(".item-description") or \
                            soup.select_one(".with-indent") or \
                            soup.select_one(".detail-description")
            if alt_desc_elem:
                description = alt_desc_elem.text.strip()
        
        # 説明文が空の場合、最終手段として商品詳細セクション全体から取得
        if not description:
            full_details = soup.select_one(".market-item-detail") or \
                            soup.select_one(".item-description-container")
            if full_details:
                # ナビゲーションなど不要部分を除外
                for nav in full_details.find_all(["nav", "header", "footer"]):
                    nav.decompose()
                description = full_details.text.strip()

            
        # サムネイル画像URL取得
        thumbnail_url = None
        main_image = soup.select_one(".item-view__image-link img")
        if main_image:
            thumbnail_url = main_image.get("src") or main_image.get("data-original")
        
        if not thumbnail_url:
            for s in soup.find_all("img"):
                if str(s).find("market") > 0 or str(s).find("pximg") > 0:
                    thumbnail_url = s.get("src") or s.get("data-original")
                    if thumbnail_url:
                        break
        
        # 詳細データを更新
        item_info.update({
            "title": title,
            "price": price,
            "likes": likes,
            "author": author,
            "description": description,
            "thumbnail_url": thumbnail_url
        })
        
        print(f"収集完了: {title} (スキ数: {likes})")
        return item_info