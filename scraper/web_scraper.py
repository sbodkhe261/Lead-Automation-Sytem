import asyncio
import re
import sys
import threading
from typing import Optional
import httpx
from bs4 import BeautifulSoup

if sys.platform == 'win32':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

def _run_in_dedicated_proactor(coro_fn, *args, **kwargs):
    result = None
    exc = None
    def runner():
        nonlocal result, exc
        if sys.platform == 'win32':
            loop = asyncio.ProactorEventLoop()
        else:
            loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(coro_fn(*args, **kwargs))
        except Exception as e:
            exc = e
        finally:
            try:
                loop.close()
            except Exception:
                pass
    t = threading.Thread(target=runner, daemon=True)
    t.start()
    t.join()
    if exc:
        raise exc
    return result

async def _playwright_extract_text(url: str, user_agent: str) -> str:
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(user_agent=user_agent)
        await page.goto(url, timeout=20000, wait_until="domcontentloaded")
        content = await page.inner_text("body")
        await browser.close()
        return content

async def scrape_website(url: str, timeout_sec: int = 15) -> str:
    """
    Scrapes a company website and returns clean Markdown/Text for the LLM.
    Uses lightweight fast HTTP fetching with fallback to Playwright/Crawl4AI.
    """
    if not url or not url.startswith("http"):
        return ""

    print(f"[CRAWL] Scraping website: {url}")
    
    # Method 1: Fast HTTP + BeautifulSoup (reliable & non-blocking)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    try:
        async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=timeout_sec, verify=False) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Strip scripts, styles, navs
                for s in soup(["script", "style", "svg", "noscript", "iframe"]):
                    s.decompose()
                    
                title = soup.title.string.strip() if soup.title and soup.title.string else ""
                
                # Get meta description
                meta_desc = ""
                meta_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
                if meta_tag and meta_tag.get("content"):
                    meta_desc = meta_tag["content"].strip()
                    
                # Collect text paragraphs & headings
                text_blocks = []
                if title:
                    text_blocks.append(f"Title: {title}")
                if meta_desc:
                    text_blocks.append(f"Description: {meta_desc}")
                    
                for el in soup.find_all(['h1', 'h2', 'h3', 'p', 'li']):
                    txt = el.get_text(separator=" ", strip=True)
                    if len(txt) > 25 and txt not in text_blocks:
                        text_blocks.append(txt)
                        
                combined_text = "\n".join(text_blocks)
                # Clean multiple whitespaces
                combined_text = re.sub(r'\s+', ' ', combined_text).strip()
                
                if len(combined_text) > 100:
                    print(f"[CRAWL SUCCESS] Extracted {len(combined_text)} chars from {url}")
                    return combined_text[:6000]
    except Exception as e:
        print(f"[CRAWL NOTICE] Fast HTTP fetch failed for {url}: {e}. Trying browser engine...")

    # Method 2: Playwright fallback for SPA / Javascript heavy websites
    try:
        content = await asyncio.to_thread(_run_in_dedicated_proactor, _playwright_extract_text, url, headers["User-Agent"])
        if content:
            clean_content = re.sub(r'\s+', ' ', content).strip()
            print(f"[CRAWL SUCCESS] Playwright extracted {len(clean_content)} chars from {url}")
            return clean_content[:6000]
    except Exception as e:
        print(f"[CRAWL ERROR] Playwright failed for {url}: {e}")

    return ""

if __name__ == "__main__":
    test_url = "https://example.com"
    content = asyncio.run(scrape_website(test_url))
    print(f"Content preview: {content[:150] if content else 'No content'}")
