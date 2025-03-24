"""
BOOTHページのスキ数を取得するモジュール
Playwrightを使用してページから動的に読み込まれる「スキ」数を取得します
"""
import asyncio
from playwright.async_api import async_playwright
import re

async def get_booth_likes_async(url):
    """
    Playwrightを使用してBOOTHページのスキ数を非同期で取得する関数
    
    Args:
        url (str): BOOTHの商品ページURL
    
    Returns:
        int or None: スキ数、取得できない場合はNone
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        try:
            # ページの読み込み
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)
            
            # スキ数を含む要素を探す
            if await page.locator("#js-item-wishlist-button").count() > 0:
                # JavaScript経由で要素内のテキストを取得
                likes_count = await page.evaluate("""
                    () => {
                        const el = document.getElementById('js-item-wishlist-button');
                        if (!el) return null;
                        
                        // ボタン内の全テキストから数字を抽出
                        const text = el.textContent || '';
                        const match = text.match(/\\d+/);
                        if (match) return parseInt(match[0]);
                        
                        // 子要素も探索
                        const childrenWithDigits = Array.from(el.querySelectorAll('*')).find(
                            child => /\\d+/.test(child.textContent)
                        );
                        
                        if (childrenWithDigits) {
                            const match = childrenWithDigits.textContent.match(/\\d+/);
                            return match ? parseInt(match[0]) : null;
                        }
                        
                        return null;
                    }
                """)
                
                return likes_count
                
            return None
            
        except Exception as e:
            print(f"スキ数取得エラー: {e}")
            return None
            
        finally:
            await browser.close()

def get_booth_likes(url):
    """
    BOOTHページのスキ数を同期的に取得する関数（非同期関数のラッパー）
    
    Args:
        url (str): BOOTHの商品ページURL
    
    Returns:
        int or None: スキ数、取得できない場合はNone
    """
    return asyncio.run(get_booth_likes_async(url))
