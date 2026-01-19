import pandas as pd
import time
import requests
import os
import urllib.parse
from datetime import datetime

class AmazonSuggestionEngine:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
        self.scrape_do_token = os.getenv("SCRAPE_DO_TOKEN")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def fetch_suggestions(self, search_term):
        """
        Tries to fetch suggestions from Amazon API.
        Fallback: Uses Scrape.do proxy if direct request is blocked.
        """
        base_url = "https://completion.amazon.com/api/2017/suggestions"
        params = {
            'page-type': 'Search',
            'lop': 'en_US',
            'site-variant': 'desktop',
            'client-info': 'amazon-search-ui',
            'mid': 'ATVPDKIKX0DER',
            'alias': 'aps',
            'suggestion-type': 'KEYWORD',
            'prefix': search_term,
        }

        # 1. Try Direct Request (Fastest)
        try:
            response = self.session.get(base_url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [item['value'] for item in data.get('suggestions', [])]
        except:
            pass

        # 2. Fallback: Scrape.do (If blocked)
        if self.scrape_do_token:
            try:
                # Construct the full Amazon URL and pass it to Scrape.do
                amazon_url = f"{base_url}?{urllib.parse.urlencode(params)}"
                proxy_url = f"http://api.scrape.do?token={self.scrape_do_token}&url={urllib.parse.quote(amazon_url)}"
                
                response = requests.get(proxy_url, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    return [item['value'] for item in data.get('suggestions', [])]
            except Exception as e:
                print(f"Proxy Error: {e}")

        return []

    def process_file(self, input_path):
        """Reads Excel, fetches keywords, saves report."""
        try:
            df = pd.read_excel(input_path)
            # Auto-detect column: Takes the first column regardless of name
            product_col = df.columns[0]
            products = df[product_col].dropna().tolist()

            results = []
            print(f"🔄 Processing {len(products)} keywords...")

            for idx, product in enumerate(products):
                # Fetch
                suggestions = self.fetch_suggestions(str(product))
                
                # Structure Data
                row = {'Input Product': product}
                for i, sugg in enumerate(suggestions[:10]): # Top 10
                    row[f'Keyword_{i+1}'] = sugg
                
                # Fill 'All_Keywords' combined column
                row['All_Keywords'] = " | ".join(suggestions)
                
                results.append(row)
                
                # Respectful delay
                time.sleep(0.2) 

            # Create Output File
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"Amazon_Suggestions_{timestamp}.xlsx"
            output_path = os.path.join(self.upload_folder, output_filename)

            pd.DataFrame(results).to_excel(output_path, index=False)
            
            return {
                "success": True,
                "message": f"Generated {len(results)} rows",
                "file_url": f"/download/{output_filename}"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

# Wrapper function for the server
def run_suggestion_scraper(filepath, upload_folder):
    engine = AmazonSuggestionEngine(upload_folder)
    return engine.process_file(filepath)