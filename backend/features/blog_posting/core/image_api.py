import os
import random
import requests
import urllib.parse
import time

class ImageGenerator:
    def __init__(self):
        self.pexels_key = os.getenv("PEXELS_API_KEY")
        self.unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY") # Add this to .env
        
        self.style_modifiers = [
            "cinematic lighting", "hyperrealistic", "8k resolution",
            "tech product photography", "studio lighting", "futuristic"
        ]

    # --- SOURCE 1: POLLINATIONS AI (Best for Uniqueness) ---
    def get_ai_image(self, prompt):
        try:
            clean_prompt = prompt.replace("Best", "").replace("Guide", "").strip()
            styles = ", ".join(random.sample(self.style_modifiers, 2))
            full_prompt = f"{clean_prompt}, {styles}, white background"
            encoded = urllib.parse.quote(full_prompt)
            seed = random.randint(1, 99999)
            
            # Try multiple models
            for model in ['flux', 'turbo']:
                url = f"https://pollinations.ai/p/{encoded}?width=1280&height=720&seed={seed}&model={model}&nologo=true"
                try:
                    # Verify it exists (Fast check)
                    check = requests.head(url, timeout=5)
                    if check.status_code == 200:
                        print(f"   🎨 AI Image Generated ({model})")
                        return url
                except: continue
        except Exception as e:
            print(f"   ⚠️ AI Failed: {e}")
        return None

    # --- SOURCE 2: UNSPLASH (Best for Quality) ---
    def get_unsplash_image(self, query):
        if not self.unsplash_key: return None
        try:
            print(f"   📷 Searching Unsplash for: {query}")
            url = "https://api.unsplash.com/search/photos"
            params = {
                "query": query,
                "per_page": 1,
                "orientation": "landscape",
                "client_id": self.unsplash_key
            }
            res = requests.get(url, params=params, timeout=5)
            if res.status_code == 200:
                data = res.json()
                if data['results']:
                    return data['results'][0]['urls']['regular']
        except: pass
        return None

    # --- SOURCE 3: PEXELS (Fallback) ---
    def get_pexels_image(self, query):
        if not self.pexels_key: return None
        try:
            headers = {"Authorization": self.pexels_key}
            url = f"https://api.pexels.com/v1/search?query={query}&per_page=1&orientation=landscape"
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200 and res.json().get('photos'):
                return res.json()['photos'][0]['src']['landscape']
        except: pass
        return None

    def generate_image(self, prompt: str, keywords: list = None) -> str:
        """
        Waterfall Strategy: AI -> Unsplash -> Pexels -> Placeholder
        """
        search_query = keywords[0] if keywords else prompt

        # 1. Try AI (Unique)
        img = self.get_ai_image(search_query)
        if img: return img
        
        # 2. Try Unsplash (High Quality)
        img = self.get_unsplash_image(search_query)
        if img: return img
        
        # 3. Try Pexels (Backup)
        img = self.get_pexels_image(search_query)
        if img: return img

        return "https://via.placeholder.com/1280x720?text=SevenXT+Tech"