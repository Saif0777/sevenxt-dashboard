import requests
import re
import os
import json
import urllib.parse
from bs4 import BeautifulSoup
from dotenv import load_dotenv

current_file_path = os.path.abspath(__file__)
features_dir = os.path.dirname(current_file_path)
backend_dir = os.path.dirname(features_dir)
env_path = os.path.join(backend_dir, '.env')
load_dotenv(dotenv_path=env_path)

def extract_asin(url):
    """Extracts ASIN (B0...) from any Amazon URL"""
    regex = r"(?:/dp/|/gp/product/)([A-Z0-9]{10})"
    match = re.search(regex, url)
    if match: return match.group(1)
    return None

def get_product_details(amazon_url):
    """
    ROBUST VERSION: Uses Scrape.do Proxy API + BeautifulSoup Parsing.
    """
    api_token = os.getenv("SCRAPE_DO_TOKEN")
    if not api_token:
        return {"error": "Critical: SCRAPE_DO_TOKEN missing in .env"}

    asin = extract_asin(amazon_url)
    if not asin: return {"error": "Invalid Amazon Link."}

    print(f"📡 Fetching Amazon Page for ASIN: {asin} via Scrape.do...")

    try:
        # 1. Construct Scrape.do URL
        # We target the clean DP link to minimize noise
        target_url = f"https://www.amazon.in/dp/{asin}"
        encoded_url = urllib.parse.quote(target_url)
        
        # Scrape.do API Endpoint
        # render=false (Cheaper, 1 credit) usually works for Amazon product text
        proxy_url = f"http://api.scrape.do?token={api_token}&url={encoded_url}"

        response = requests.get(proxy_url, timeout=60)
        
        if response.status_code != 200:
            return {"error": f"Scrape.do Failed: {response.status_code} - {response.text[:100]}"}

        # 2. Parse HTML with BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # --- DATA EXTRACTION LOGIC ---

        # A. Title
        title_tag = soup.find("span", {"id": "productTitle"})
        title = title_tag.get_text().strip() if title_tag else f"Amazon Product {asin}"

        # B. Brand
        brand = "SEVENXT"
        byline = soup.find("a", {"id": "bylineInfo"})
        if byline:
            # Usually says "Visit the Sony Store"
            text = byline.get_text().replace("Visit the", "").replace("Store", "").strip()
            if text: brand = text

        # C. HD Image (The Hard Part)
        # Amazon hides Hi-Res images in a JSON object inside a script tag
        img_url = "https://via.placeholder.com/800"
        
        # Method 1: Dynamic Image Data (Best Quality)
        img_div = soup.find("div", {"id": "imgTagWrapperId"})
        if img_div:
            img_tag = img_div.find("img")
            if img_tag and 'data-a-dynamic-image' in img_tag.attrs:
                try:
                    # It's a JSON dictionary: {"url": [width, height], ...}
                    img_data = json.loads(img_tag['data-a-dynamic-image'])
                    # The last key is usually the largest image
                    img_url = list(img_data.keys())[-1]
                    print("   ✅ Found HD Image via Dynamic JSON")
                except: pass
        
        # Method 2: Landing Image Fallback
        if "placeholder" in img_url:
            landing_img = soup.find("img", {"id": "landingImage"})
            if landing_img:
                img_url = landing_img.get('src')
                # Strip resizing code if present (e.g. ._AC_XY200_.jpg)
                img_url = re.sub(r'\._AC_.*?_\.', '.', img_url)

        # D. Description (Bullet Points)
        bullets = []
        feature_div = soup.find("div", {"id": "feature-bullets"})
        if feature_div:
            for li in feature_div.find_all("li"):
                # Remove "Show more" buttons or hidden text
                if "a-declarative" not in li.get('class', []):
                    text = li.get_text().strip()
                    if text: bullets.append(text)
        
        description = " ".join(bullets[:5]) # Top 5 bullets
        if not description:
            # Fallback to meta description
            meta = soup.find("meta", {"name": "description"})
            if meta: description = meta['content']

        print(f"✅ Data Ready: {title[:20]}... | Image Extracted.")

        return {
            "status": "success",
            "asin": asin,
            "title": title,
            "brand": brand,
            "image_url": img_url, 
            "description": description,
            "seo_url": f"https://www.amazon.in/{title.replace(' ', '-').lower()[:50]}/dp/{asin}"
        }

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e)}