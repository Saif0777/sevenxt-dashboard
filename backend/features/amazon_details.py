import requests
import re
import json
import random
import time
from bs4 import BeautifulSoup

def extract_asin(url):
    """Extracts ASIN (B0...) from any Amazon URL"""
    # Matches /dp/ASIN, /gp/product/ASIN, etc.
    regex = r"(?:/dp/|/gp/product/)([A-Z0-9]{10})"
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None

def get_product_details(amazon_url):
    """
    Robust Amazon Scraper with Robot-Check Detection
    """
    asin = extract_asin(amazon_url)
    if not asin:
        return {"error": "Invalid Amazon Link. Could not find ASIN."}

    url = f"https://www.amazon.in/dp/{asin}"

    # ROTATING HEADERS (Crucial for bypassing blocks)
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0'
    ]

    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/',
        'Upgrade-Insecure-Requests': '1',
    }

    try:
        # Add a small random delay to look human
        time.sleep(random.uniform(1, 2))
        
        response = requests.get(url, headers=headers, timeout=10)
        
        # Check for Robot/Captcha Page
        if "api-services-support@amazon.com" in response.text or "Type the characters you see in this image" in response.text:
            return {"error": "Amazon detected a bot. Try again in 1 minute."}

        soup = BeautifulSoup(response.content, "html.parser")

        # 1. EXTRACT TITLE
        title_tag = soup.find("span", {"id": "productTitle"})
        title = title_tag.get_text().strip() if title_tag else ""
        
        if not title:
            # Fallback for meta title
            meta_title = soup.find("meta", {"name": "title"})
            title = meta_title['content'] if meta_title else f"Amazon Product {asin}"

        # 2. EXTRACT BRAND (New Logic)
        # Tries to find "Visit the Brand Store" or similar text
        brand = "SEVENXT" # Default
        by_line = soup.find("a", {"id": "bylineInfo"})
        if by_line:
            brand_text = by_line.get_text().replace("Visit the", "").replace("Store", "").strip()
            if brand_text: brand = brand_text

        # 3. EXTRACT IMAGE (High Res)
        img_url = "https://via.placeholder.com/800" # Fallback
        
        # Method A: Dynamic JSON
        img_div = soup.find("div", {"id": "imgTagWrapperId"})
        if img_div and img_div.find("img"):
            img_tag = img_div.find("img")
            if 'data-a-dynamic-image' in img_tag.attrs:
                try:
                    img_dict = json.loads(img_tag['data-a-dynamic-image'])
                    # Get the largest image (last key)
                    img_url = list(img_dict.keys())[-1]
                except:
                    img_url = img_tag.get('src')
        
        # Method B: Landing Image ID
        if "placeholder" in img_url:
            landing_img = soup.find("img", {"id": "landingImage"})
            if landing_img:
                img_url = landing_img.get('src')

        # 4. EXTRACT BULLETS
        bullets = []
        bullet_div = soup.find("div", {"id": "feature-bullets"})
        if bullet_div:
            for li in bullet_div.find_all("li"):
                txt = li.get_text().strip()
                if txt and not "show more" in txt.lower():
                    bullets.append(txt)
        
        description = " ".join(bullets[:4]) # Top 4 bullets

        return {
            "status": "success",
            "asin": asin,
            "title": title,
            "brand": brand, # Passing brand to frontend
            "image_url": img_url,
            "description": description,
            "seo_url": f"https://www.amazon.in/{title.replace(' ', '-').lower()[:50]}/dp/{asin}"
        }

    except Exception as e:
        return {"error": str(e)}