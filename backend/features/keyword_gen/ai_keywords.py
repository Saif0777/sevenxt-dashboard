import os
import requests
import httpx
import json
import asyncio
from typing import List, Dict

class HybridKeywordGenerator:
    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.serp_key = os.getenv("SERPAPI_API_KEY")
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.client = httpx.AsyncClient(timeout=60.0)

    def fetch_real_time_trends(self, query: str) -> List[str]:
        """
        Robust Fetcher:
        1. Tries Direct Amazon India API (Fast).
        2. If blocked (JSON Error), falls back to SerpApi Google Autocomplete (Reliable).
        """
        # Smart Truncation (Keep query short for better matches)
        clean_query = " ".join(query.split()[:4]) 
        print(f"📡 Fetching Market Data for: '{clean_query}'...")
        
        suggestions = []

        # --- STRATEGY 1: Direct Amazon India (Fastest) ---
        try:
            url = f"https://completion.amazon.in/search/complete?client=amazon-search-ui&mkt=1&search-alias=aps&q={clean_query}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=3)
            
            # This line caused the crash before. Now we catch it.
            data = response.json() 
            
            if isinstance(data, list) and len(data) > 1:
                suggestions = data[1]
                print(f"✅ [Direct] Captured {len(suggestions)} signals.")
                return suggestions

        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️ Direct Amazon blocked (Soft 403/Captcha). Switching to SerpApi...")

        # --- STRATEGY 2: SerpApi Fallback (Robust) ---
        if self.serp_key:
            try:
                # We use Google Autocomplete as a proxy for market intent
                # (Since SerpApi 'amazon' engine is for products, not autocomplete)
                params = {
                    "engine": "google_autocomplete",
                    "q": clean_query,
                    "api_key": self.serp_key,
                    "gl": "in" # Geography: India
                }
                response = requests.get("https://serpapi.com/search.json", params=params, timeout=10)
                data = response.json()
                
                if "suggestions" in data:
                    suggestions = [item.get("value") for item in data["suggestions"]]
                    print(f"✅ [SerpApi] Captured {len(suggestions)} signals.")
            except Exception as e:
                print(f"❌ SerpApi Failed: {e}")

        return suggestions

    async def generate_advanced_strategy(self, product_name: str, asin: str) -> List[Dict]:
        if not self.groq_key:
            return [{"keyword": "Error", "url": "Missing GROQ_API_KEY"}]

        # 1. GET REAL DATA (Now Crash-Proof)
        real_market_data = self.fetch_real_time_trends(product_name)
        
        # 2. FEED DATA TO AI
        prompt = f"""
        You are an Advanced Amazon SEO Strategist for the Indian Market.
        
        CONTEXT:
        Product: "{product_name}"
        Real-Time Search Trends: {real_market_data}
        
        TASK:
        Generate exactly 12 Optimized URL Slugs following the client's strict template.
        
        CRITICAL RULES:
        1. Keep keywords short (2-5 words max).
        2. DO NOT use question marks or full sentences.
        3. Use the "Real-Time Trends" to find Competitor names and specific Specs.
        4. If the product is a "Remote", use keywords like "Replacement", "Compatible", "Bluetooth".

        TEMPLATE (Generate 1 line for each):
        1. [Main Product] (e.g. "Universal Remote Samsung")
        2. [Product + Key Feature] (e.g. "Smart TV Remote Voice Control")
        3. [Product + Use Case] (e.g. "Remote for Old Samsung LCD")
        4. [Product + Compatibility] (e.g. "Remote for UA32 Series")
        5. [Product + Benefit] (e.g. "No Setup Required Remote")
        6. [Product + Material/Spec] (e.g. "Long Range IR Remote")
        7. [Competitor/Generic] (e.g. "Replacment for BN59-01199F") <--- VERY IMPORTANT
        8. [Trending Variation 1]
        9. [Trending Variation 2]
        10. [Trending Variation 3]
        11. [Trending Variation 4]
        12. [Trending Variation 5]

        OUTPUT FORMAT:
        Return ONLY the raw list of 12 keyword phrases. No numbering.
        """

        try:
            response = await self.client.post(
                self.groq_url,
                headers={"Authorization": f"Bearer {self.groq_key}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": "You are a data-driven SEO engine. Output raw text only."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.5 
                }
            )
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # 3. PARSE AND BUILD URLs
            clean_keywords = []
            raw_lines = content.strip().split('\n')
            
            for line in raw_lines:
                clean = line.replace('*', '').replace('"', '').strip()
                if len(clean) > 0 and clean[0].isdigit():
                    try:
                        clean = clean.split('.', 1)[1].strip()
                    except: pass
                
                if clean and len(clean) < 60: 
                    clean_keywords.append(clean)
            
            # Ensure we have 12
            final_data = []
            templates = [
                "Main Product", "Feature Focus", "Use Case", "Compatibility", 
                "Benefit Focus", "Spec Focus", "Competitor/Generic", "Long Tail", 
                "Trending #1", "Trending #2", "Trending #3", "Trending #4"
            ]

            for i, kw in enumerate(clean_keywords[:12]):
                slug = kw.lower().replace(" ", "-").replace("/", "-").replace("+", "")
                url = f"https://www.amazon.in/{slug}/dp/{asin}"
                strategy_name = templates[i] if i < len(templates) else "Bonus Strategy"
                
                final_data.append({
                    "strategy": strategy_name,
                    "keyword": kw, 
                    "url": url
                })
                
            return final_data

        except Exception as e:
            print(f"❌ Hybrid Engine Error: {e}")
            return []

# Wrapper for server.py
def get_hybrid_keywords(product, asin):
    gen = HybridKeywordGenerator()
    return asyncio.run(gen.generate_advanced_strategy(product, asin))