import pandas as pd
import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager # <--- Added for stability

class AmazonSuggestionScraper:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        
    def method1_api_approach(self, search_term):
        """Fast method using Amazon's suggestion API"""
        try:
            url = f"https://completion.amazon.com/api/2017/suggestions"
            params = {
                'session-id': '1', 'customer-id': '', 'request-id': '',
                'page-type': 'Search', 'lop': 'en_US', 'site-variant': 'desktop',
                'client-info': 'amazon-search-ui', 'mid': 'ATVPDKIKX0DER',
                'alias': 'aps', 'suggestion-type': 'KEYWORD', 'prefix': search_term,
                'event': 'onkeypress', 'limit': 10
            }
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                suggestions = [item['value'] for item in data.get('suggestions', [])]
                return suggestions
            return []
        except:
            return []
    
    def method2_selenium_approach(self, search_term):
        """Backup method using Selenium"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless') 
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # --- UPDATED: Use ChromeDriverManager for auto-setup ---
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            driver.get("https://www.amazon.com")
            
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
            )
            
            search_box.clear()
            for char in search_term:
                search_box.send_keys(char)
                time.sleep(0.1)
            
            time.sleep(2)
            
            suggestions = []
            suggestion_elements = driver.find_elements(By.CSS_SELECTOR, "div.autocomplete-results-container div.s-suggestion")
            
            for element in suggestion_elements:
                text = element.get_attribute('aria-label')
                if text: suggestions.append(text)
            
            driver.quit()
            return suggestions[:10]
            
        except Exception as e:
            print(f"Selenium error: {e}")
            if 'driver' in locals(): driver.quit()
            return []
    
    def scrape_suggestions(self):
        """Main function to process all products"""
        df_input = pd.read_excel(self.input_file)
        product_column = df_input.columns[0] 
        products = df_input[product_column].tolist()
        all_results = []
        
        print(f"Processing {len(products)} products...")
        
        for i, product in enumerate(products, 1):
            print(f"Searching: {product}")
            suggestions = self.method1_api_approach(product)
            
            if not suggestions:
                print("API failed, trying Selenium...")
                suggestions = self.method2_selenium_approach(product)
            
            result = {
                'Search_Term': product,
                'Keyword_1': suggestions[0] if len(suggestions) > 0 else '',
                'Keyword_2': suggestions[1] if len(suggestions) > 1 else '',
                'Keyword_3': suggestions[2] if len(suggestions) > 2 else '',
                'Keyword_4': suggestions[3] if len(suggestions) > 3 else '',
                'Keyword_5': suggestions[4] if len(suggestions) > 4 else '',
                'Keyword_6': suggestions[5] if len(suggestions) > 5 else '',
                'Keyword_7': suggestions[6] if len(suggestions) > 6 else '',
                'Keyword_8': suggestions[7] if len(suggestions) > 7 else '',
                'Keyword_9': suggestions[8] if len(suggestions) > 8 else '',
                'Keyword_10': suggestions[9] if len(suggestions) > 9 else '',
                'All_Keywords': ' | '.join(suggestions)
            }
            all_results.append(result)
            time.sleep(1) # Small delay
        
        df_output = pd.DataFrame(all_results)
        
        with pd.ExcelWriter(self.output_file, engine='openpyxl') as writer:
            df_output.to_excel(writer, sheet_name='All_Suggestions', index=False)
        
        return df_output