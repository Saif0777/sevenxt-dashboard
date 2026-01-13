import os
import requests
import httpx
import json
import asyncio
import urllib.parse
import pandas as pd
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

current_file_path = os.path.abspath(__file__)
features_dir = os.path.dirname(current_file_path)
backend_dir = os.path.dirname(features_dir)
features_parent = os.path.dirname(features_dir)
env_path = os.path.join(features_parent, '.env')
load_dotenv(dotenv_path=env_path)

class HybridKeywordGenerator:
    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.scrape_do_token = os.getenv("SCRAPE_DO_TOKEN")
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.client = httpx.AsyncClient(timeout=60.0)
        
        # Path setup
        this_file_folder = os.path.dirname(os.path.abspath(__file__))
        features_folder = os.path.dirname(this_file_folder)
        backend_folder = os.path.dirname(features_folder)
        self.uploads_dir = os.path.join(backend_folder, 'uploads')
        os.makedirs(self.uploads_dir, exist_ok=True)

    async def extract_seed_keyword(self, long_title: str) -> str:
        """AI determines the best search query."""
        if not self.groq_key: return " ".join(long_title.split()[:3])

        prompt = f"""
        Extract the MAIN Amazon Search Query (2-4 words) from this product title.
        Input: "{long_title}"
        OUTPUT ONLY THE SEARCH TERM. NO QUOTES.
        """
        try:
            response = await self.client.post(
                self.groq_url,
                headers={"Authorization": f"Bearer {self.groq_key}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1
                }
            )
            return response.json()["choices"][0]["message"]["content"].strip().replace('"', '')
        except:
            return " ".join(long_title.split()[:3])

    async def _ai_verify_trends(self, product_name: str, trends: List[str], specs: str) -> List[str]:
        """
        🚀 NEW: SEMANTIC AI FILTER (Universally Robust)
        Uses AI to decide if a trend is misleading based on the Product & Specs.
        """
        if not trends or not self.groq_key: return trends

        # Create a prompt that asks AI to act as a strict moderator
        trend_list_str = "\n".join([f"- {t}" for t in trends])
        
        prompt = f"""
        You are an Amazon Product Data Validator.
        
        MY PRODUCT: "{product_name}"
        MY SPECS: "{specs[:500]}" (Truncated)

        MARKET TRENDS (Potential Keywords):
        {trend_list_str}

        TASK:
        Filter out ANY trend that is **Misleading**, **Incompatible**, or **Refers to an Accessory** I am not selling.
        
        EXAMPLES OF LOGIC:
        - If Product is "TV Remote" -> REMOVE "Remote Cover", "Remote Battery", "Remote Holder".
        - If Product is "Water Bottle" -> REMOVE "Bottle Cage", "Bottle Brush".
        - If Product is "iPhone 13" -> REMOVE "iPhone 13 Case" (unless I am selling a case).
        - If Specs say "Standard Remote" -> REMOVE "Voice Remote", "Magic Remote".

        OUTPUT:
        Return ONLY the valid trends as a JSON list of strings.
        Example: ["valid trend 1", "valid trend 2"]
        """

        try:
            response = await self.client.post(
                self.groq_url,
                headers={"Authorization": f"Bearer {self.groq_key}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": "You are a JSON filter. Output JSON list only."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1
                }
            )
            content = response.json()["choices"][0]["message"]["content"]
            # Clean markup if present
            content = content.replace("```json", "").replace("```", "").strip()
            
            valid_trends = json.loads(content)
            
            # Logging what was removed
            removed = set(trends) - set(valid_trends)
            if removed:
                print(f"🛡️ [AI Smart Filter] Blocked {len(removed)} misleading trends: {list(removed)[:3]}...")
            
            return valid_trends

        except Exception as e:
            print(f"⚠️ Filter Error: {e}. Using raw trends.")
            return trends # Fallback to raw list if AI fails

    async def fetch_real_time_trends(self, clean_query: str) -> List[str]:
        encoded_query = urllib.parse.quote(clean_query)
        print(f"📡 Fetching Market Data for: '{clean_query}'...")
        
        url_internal = f"https://completion.amazon.in/api/2017/suggestions?mid=A21TJRUUN4KGV&alias=aps&prefix={encoded_query}"
        url_global = f"https://completion.amazon.in/search/complete?client=psy-ab&q={encoded_query}"

        suggestions = []
        
        if self.scrape_do_token:
            for target_url in [url_internal, url_global]:
                try:
                    proxy_url = f"http://api.scrape.do?token={self.scrape_do_token}&url={urllib.parse.quote(target_url)}"
                    response = requests.get(proxy_url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        suggestions = self._parse_response(data)
                        if suggestions:
                            print(f"✅ [Scrape.do] Captured {len(suggestions)} signals.")
                            return suggestions
                except: pass

        try:
            headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}
            response = requests.get(url_internal, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                suggestions = self._parse_response(data)
                if suggestions:
                    print(f"✅ [Local-Direct] Captured {len(suggestions)} signals.")
                    return suggestions
        except: pass

        return []

    def _parse_response(self, data):
        try:
            if isinstance(data, dict) and 'suggestions' in data:
                return [item.get("value") for item in data["suggestions"]]
            elif isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
                return data[1]
        except: pass
        return []

    async def generate_advanced_strategy(self, product_name: str, asin: str, specs: str) -> Dict:
        if not self.groq_key: return {"error": "Missing GROQ_API_KEY"}

        # 1. AI PRE-PROCESSING
        seed_keyword = await self.extract_seed_keyword(product_name)
        
        # 2. GET RAW TRENDS
        raw_trends = await self.fetch_real_time_trends(seed_keyword)
        
        # 3. AI SMART FILTERING (The New Robust Layer)
        safe_trends = await self._ai_verify_trends(product_name, raw_trends, specs)
        
        market_data_str = ", ".join(safe_trends)
        
        # 4. FEED VERIFIED DATA TO STRATEGIST
        prompt = f"""
        You are a Technical Amazon SEO Strategist.
        
        PRODUCT CONTEXT:
        Name: "{product_name}"
        Specs: "{specs[:500]}"
        
        VERIFIED MARKET TRENDS (Safe to use):
        {market_data_str}
        
        TASK:
        Generate exactly 12 High-Converting Keywords using the Verified Trends.
        
        CRITICAL RULES:
        1. **PRIORITIZE TRENDS:** Use the "VERIFIED MARKET TRENDS" list to fill the templates.
        2. **STRICT RELEVANCE:** Do not use features (Voice, Bluetooth) unless they are in the Specs.
        3. **COMPETITORS:** Identify rival brands from the Trends list (e.g. Xiaomi, Samsung) and use them in Strategy #7.

        TEMPLATES:
        1. [Main Product]
        2. [Product + Key Feature]
        3. [Product + Use Case]
        4. [Product + Compatibility]
        5. [Product + Benefit]
        6. [Product + Material/Spec]
        7. [Competitor/Generic]
        8. [Trending Variation 1]
        9. [Trending Variation 2]
        10. [Trending Variation 3]
        11. [Trending Variation 4]
        12. [Trending Variation 5]

        OUTPUT: Raw text list only.
        """

        # --- 🛡️ UPDATED: ROBUST API CALL WITH DEBUG LOGGING ---
        try:
            print(f"📡 Sending request to Groq Model: llama-3.3-70b-versatile...")
            
            response = await self.client.post(
                self.groq_url,
                headers={"Authorization": f"Bearer {self.groq_key}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2
                }
            )

            # 🛑 CRITICAL CHECK: Did the API Request Fail?
            if response.status_code != 200:
                print(f"❌ CRITICAL AI ERROR: Status {response.status_code}")
                print(f"⚠️ API Response Body: {response.text}")
                return {"error": f"AI Error {response.status_code}: {response.text}"}
            
            # If 200 OK, proceed safely
            content = response.json()["choices"][0]["message"]["content"]
            raw_lines = [line.replace('*', '').strip() for line in content.strip().split('\n') if line.strip()]
            
            final_data = []
            templates = ["Main Product", "Feature Focus", "Use Case", "Compatibility", "Benefit Focus", "Spec Focus", "Competitor/Generic", "Trending #1", "Trending #2", "Trending #3", "Trending #4", "Trending #5"]

            for i, kw in enumerate(raw_lines[:12]):
                if len(kw) > 0 and kw[0].isdigit():
                    try: kw = kw.split('.', 1)[1].strip()
                    except: pass
                
                slug = kw.lower().replace(" ", "-").replace("/", "-").replace("+", "")
                url = f"https://www.amazon.in/{slug}/dp/{asin}"
                strategy_name = templates[i] if i < len(templates) else "Bonus"
                
                is_trend_match = any(trend.lower() in kw.lower() for trend in safe_trends)
                
                source_label = "🔥 Market Data" if is_trend_match else "🧠 AI Strategy"
                source_color = "green" if is_trend_match else "blue"
                
                final_data.append({
                    "strategy": strategy_name,
                    "keyword": kw, 
                    "url": url,
                    "source": source_label,
                    "source_color": source_color
                })

            df = pd.DataFrame(final_data)
            filename = f"SevenXT_SEO_{asin}_{int(datetime.now().timestamp())}.xlsx"
            file_path = os.path.join(self.uploads_dir, filename)
            df.to_excel(file_path, index=False)
            
            return {
                "data": final_data,
                "file_url": f"/download/{filename}" 
            }

        except Exception as e:
            # 🛑 GLOBAL ERROR CATCHER
            print(f"❌ CRITICAL PYTHON ERROR: {str(e)}")
            return {"error": f"Internal Error: {str(e)}"}

def get_hybrid_keywords(product, asin, specs):
    gen = HybridKeywordGenerator()
    return asyncio.run(gen.generate_advanced_strategy(product, asin, specs))