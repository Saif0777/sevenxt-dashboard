import os
import random
import httpx

class ImageGenerator:
    def __init__(self):
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")
        
    def generate_image(self, prompt: str, keywords: list = None) -> str:
        if not self.pexels_api_key:
            print("⚠️ PEXELS_API_KEY missing.")
            return "https://via.placeholder.com/800x400?text=No+API+Key"

        try:
            # Clean prompt for better search results
            search_query = prompt.replace("Complete Guide", "").replace("How to", "").strip()
            
            print(f"🎨 Searching Pexels for: '{search_query}'")
            
            url = "https://api.pexels.com/v1/search"
            headers = {"Authorization": self.pexels_api_key}
            params = {"query": search_query, "per_page": 3, "orientation": "landscape", "size": "medium"}
            
            with httpx.Client() as client:
                response = client.get(url, headers=headers, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('photos'):
                        return data['photos'][0]['src']['landscape']
            
            return "https://via.placeholder.com/800x400?text=No+Image+Found"

        except Exception as e:
            print(f"❌ Image Error: {e}")
            return "https://via.placeholder.com/800x400?text=Image+Error"