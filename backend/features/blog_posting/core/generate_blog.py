import os
import httpx
import json
from typing import List

class GroqAPI:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.client = httpx.AsyncClient(timeout=120.0)

    def _sanitize_json(self, raw_text):
        """Clean markdown wrappers"""
        text = raw_text.replace("```json", "").replace("```", "").strip()
        return text

    async def generate_blog(self, topic, keywords, brand_name, industries, context="", attempt=1):
        if not self.api_key: raise ValueError("GROQ_API_KEY missing")

        # --- HYPER-STRICT SEO PROMPT ---
        prompt = f"""
        You are a SEO Algorithm Beater. Write a **1500-Word Product Guide** in STRICT JSON format.

        PRODUCT DATA:
        Name: {topic}
        Specs: {context}
        Brand: {brand_name}

        --- CRITICAL SEO RULES (PASS/FAIL) ---
        1. **Focus Keyphrase:** Pick a specific 3-4 word keyword (e.g., "{brand_name} TV Remote").
        2. **Title:** Must START with the Keyphrase. Max 60 chars.
        3. **Introduction Rule:** The text MUST start exactly with: "The **[Keyphrase]** is the perfect solution for..."
        4. **Density Rule:** You must use the Keyphrase EXACTLY 5 times in the entire article.
           - 1x in Intro
           - 1x in the first H2
           - 2x in the Body
           - 1x in Conclusion
           - STOP using it after 5 times. Use "this device" instead.
        5. **Subheading Rule:** The first H2 Header MUST be exactly: "Why Choose the [Keyphrase]?"

        --- CONTENT SKELETON (1500 Words) ---
        1. **Introduction (150 Words):** Hook the reader immediately.
        2. **Why Choose the [Keyphrase]? (300 Words):** (This H2 satisfies the SEO rule). Explain the main value proposition.
        3. **Detailed Features (400 Words):** Expand on specs. Explain *why* IR range or button layout matters.
        4. **Setup Guide (300 Words):** Step-by-step pairing instructions.
        5. **Comparison vs Generic (200 Words):** Durability, tactility, and brand trust.
        6. **Conclusion (150 Words):** Final summary.

        OUTPUT JSON STRUCTURE:
        {{
            "focus_keyphrase": "Samsung TV Remote",
            "seo_title": "Samsung TV Remote: The Ultimate Guide",
            "meta_description": "Upgrade your setup with the Samsung TV Remote. Features long range and easy setup. (145 chars)",
            "wp_category": "Electronics",
            "wp_tags": ["Samsung", "Remote", "Smart TV"],
            "content": "# Title\\n\\n## Introduction\\n\\nThe [Keyphrase] is... (write full content)..."
        }}
        """

        try:
            response = await self.client.post(
                self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": "You are a strict SEO bot. You follow density rules exactly."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1 # Lowest temp for maximum obedience
                }
            )
            result = response.json()
            raw_content = result["choices"][0]["message"]["content"]
            
            clean_json = self._sanitize_json(raw_content)
            
            try:
                data = json.loads(clean_json, strict=False)
            except json.JSONDecodeError:
                return {
                    'title': f"Review: {topic}",
                    'content': raw_content, 
                    'meta_description': f"Review of {topic}.",
                    'keywords': ["Tech"],
                    'focus_keyphrase': "Tech",
                    'wp_category': "Uncategorized",
                    'wp_tags': []
                }
            
            return {
                'title': data.get('seo_title', topic), 
                'content': data.get('content', raw_content),
                'meta_description': data.get('meta_description', ''),
                'keywords': [data.get('focus_keyphrase', 'Tech')],
                'focus_keyphrase': data.get('focus_keyphrase', 'Review'),
                'wp_category': data.get('wp_category', 'Electronics'),
                'wp_tags': data.get('wp_tags', [])
            }

        except Exception as e:
            print(f"AI Error: {e}")
            return {
                'title': topic,
                'content': f"# {topic}\n\n**Error:** Could not generate content.",
                'meta_description': "Product review.",
                'keywords': ["Review"],
                'focus_keyphrase': "Review",
                'wp_category': "Uncategorized",
                'wp_tags': []
            }

def search_trending_topics(category: str) -> List[str]:
    return ["Guide to Electronics", "Best Tech 2025"]