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
        
        # まず、item-description コンテナを探す (最も一般的)
        item_description = soup.find("div", class_="item-description")
        if item_description:
            # 説明文のテキストをすべて取得（HTMLタグを除去）
            description = item_description.get_text(separator='\n', strip=True)
        
        # 取得できなかった場合、クラス名に基づく候補を試す
        if not description:
            description_candidates = [
                soup.find("div", class_="description"),
                soup.find("div", class_="with-indent"),
                soup.find("div", class_="detail-description"),
                soup.find("div", id="description"),
                soup.find("div", class_="booth-description"),
                soup.find("div", class_="item-body"),
                soup.find("section", class_="item-description-container"),
                soup.find("div", attrs={"itemprop": "description"}),
            ]
            
            for candidate in description_candidates:
                if candidate and candidate.get_text(strip=True):
                    description = candidate.get_text(separator='\n', strip=True)
                    break
        
        # どのセレクタでも見つからない場合、メインコンテンツから探す
        if not description:
            # 商品詳細セクションを特定
            main_content = soup.find("div", class_="main-content-container") or soup.find("div", class_="item-main-content")
            if main_content:
                # 明らかにナビゲーションやヘッダーの要素を除外
                for nav in main_content.find_all(["nav", "header", "footer", "aside"]):
                    nav.decompose()
                
                # 価格や購入ボタンを含む要素を除外
                for elem in main_content.find_all(class_=lambda c: c and any(x in str(c) for x in ["price", "cart", "button", "header", "purchase", "variation"])):
                    elem.decompose()
                
                # 残りのコンテンツから一定の長さのテキストを持つブロックを見つける
                content_blocks = main_content.find_all(["div", "p", "section"], class_=lambda c: c != "item-header")
                for block in content_blocks:
                    text = block.get_text(strip=True)
                    if len(text) > 100:  # 一定以上の長さがあれば説明文と判断
                        description = block.get_text(separator='\n', strip=True)
                        break
        
        # それでも見つからない場合、最後の手段として大きなテキストブロックを探す
        if not description:
            # ページ全体から十分な長さのテキストブロックを持つ要素を見つける
            potential_desc_blocks = []
            for block in soup.find_all(["div", "section", "article"]):
                # ヘッダー、フッター、ナビゲーション要素をスキップ
                if block.find_parent(["header", "footer", "nav", "aside"]):
                    continue
                    
                text = block.get_text(strip=True)
                # 商品説明っぽい長さのテキストを持つブロックを見つける
                if len(text) > 150 and not any(x in str(block.get('class', '')) for x in ["header", "footer", "nav", "cart"]):
                    potential_desc_blocks.append((block, len(text)))
            
            # テキスト長でソートして最も長いブロックを選択
            if potential_desc_blocks:
                potential_desc_blocks.sort(key=lambda x: x[1], reverse=True)
                description = potential_desc_blocks[0][0].get_text(separator='\n', strip=True)
        
        # 説明文の整形と改行の保持
        if description:
            # 余分な空白行を削除し、適切な改行を保持
            description = re.sub(r'\n{3,}', '\n\n', description)
            description = description.strip()
            
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