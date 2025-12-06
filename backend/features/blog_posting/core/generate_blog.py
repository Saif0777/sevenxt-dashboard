import os
import httpx
import requests
import random
import json
import re
from typing import List

class GroqAPI:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.client = httpx.AsyncClient(timeout=120.0)

    async def generate_blog(self, topic, keywords, brand_name, industries, context="", attempt=1):
        if not self.api_key: raise ValueError("GROQ_API_KEY missing")

        # --- PERFECTED SEO PROMPT ---
        prompt = f"""
        You are a World-Class SEO Copywriter. 
        I will give you a product. You must write a Blog Post and generate SEO Metadata in STRICT JSON format.

        PRODUCT DETAILS:
        Name: {topic}
        Context/Specs: {context}
        Brand: {brand_name}

        CRITICAL SEO RULES (Must Follow Exactly):
        1. **Focus Keyphrase:** Pick a SHORT, high-volume keyword (Max 3-4 words) derived from the product (e.g., "Sony TV Remote").
        2. **Introduction Rule:** The Introduction MUST start with the Focus Keyphrase. (Example: "The **Sony TV Remote** is the perfect replacement...")
        3. **Density Rule:** Use the Focus Keyphrase exactly 4 to 6 times in the entire article. DO NOT overuse it. Use synonyms like "this device", "the controller", "the unit".
        4. **Heading Rule:** At least 2 Subheadings (H2) MUST contain the Focus Keyphrase exactly.
        5. **Meta Description:** Must be between 130-155 characters long and include the keyphrase.

        OUTPUT FORMAT (Must be valid JSON):
        {{
            "focus_keyphrase": "The short keyword you chose",
            "seo_title": "A catchy title starting with the keyphrase (Max 60 chars)",
            "meta_description": "A compelling summary between 130-155 characters including the keyphrase.",
            "content": "# Blog Title\\n\\n## Introduction\\n[Start with keyphrase]... (Write full 600-word article in Markdown)...\\n\\n## Why choose this [Keyphrase]?\\n..."
        }}
        """

        try:
            response = await self.client.post(
                self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": "You are a JSON-only response bot. Do not output anything except valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.4 # Lower temperature for stricter adherence to rules
                }
            )
            response.raise_for_status()
            result = response.json()
            raw_content = result["choices"][0]["message"]["content"]
            
            # --- CLEANUP JSON ---
            clean_json = raw_content.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            
            return {
                'title': data['seo_title'], 
                'content': data['content'],
                'meta_description': data['meta_description'],
                'keywords': [data['focus_keyphrase']],
                'focus_keyphrase': data['focus_keyphrase']
            }

        except Exception as e:
            print(f"AI Error: {e}")
            return {
                'title': topic,
                'content': f"# {topic}\n\nError generating content. Please try again.",
                'meta_description': "Product review.",
                'keywords': ["Review"],
                'focus_keyphrase': "Review"
            }

# --- SEARCH TRENDS (Unchanged) ---
def search_trending_topics(category: str) -> List[str]:
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key: return ["Best Smart Remotes", "4K HDMI Cables", "Wall Mount Guide"]
    try:
        url = "https://serpapi.com/search.json"
        params = {"engine": "google_autocomplete", "q": category, "api_key": api_key}
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if "suggestions" in data:
            return [item.get("value") for item in data["suggestions"]][:8]
        return ["Guide to Electronics", "Best Tech 2025"]
    except: return ["Review", "Guide"]