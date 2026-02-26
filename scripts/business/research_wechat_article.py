
import requests
from bs4 import BeautifulSoup
import sys
import os

def fetch_wechat_article(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        print(f"Fetching URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Check if we got a verification page
        if "验证" in response.text and "verify" in response.url:
             print("❌ Encountered WeChat verification page.")
             return None

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # WeChat article title
        title_tag = soup.select_one('h1.rich_media_title')
        title = title_tag.get_text(strip=True) if title_tag else "Unknown Title"
        
        # WeChat article content
        content_tag = soup.select_one('#js_content')
        if not content_tag:
            # Fallback for some layouts
            content_tag = soup.select_one('.rich_media_content')
            
        if content_tag:
            # Get text with some structure
            content = content_tag.get_text(separator='\n', strip=True)
            return {"title": title, "content": content}
        else:
            print("❌ Could not find article content div.")
            # debug: print partial html
            # print(response.text[:500])
            return None
            
    except Exception as e:
        print(f"❌ Error fetching article: {e}")
        return None

if __name__ == "__main__":
    url = "https://mp.weixin.qq.com/s/hCN9UV_R4YVIz9AI6gyOrQ"
    result = fetch_wechat_article(url)
    
    if result:
        print(f"✅ Successfully fetched article: {result['title']}")
        print("-" * 50)
        print(result['content'][:500] + "...") # Print start of content
        
        # Save to file for further processing
        with open("temp_wechat_article.txt", "w", encoding="utf-8") as f:
            f.write(f"Title: {result['title']}\n\n")
            f.write(result['content'])
        print(f"\nSaved content to temp_wechat_article.txt")
    else:
        print("Failed to fetch article content.")
        sys.exit(1)
