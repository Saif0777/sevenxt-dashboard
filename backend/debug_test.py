# backend/debug_test.py
import os
import sys

# Setup paths so imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
features_dir = os.path.join(current_dir, 'features')
sys.path.append(features_dir)

try:
    print("----- 1. TESTING IMPORTS -----")
    from features.keyword_gen.scraper import AmazonSuggestionScraper
    print("✅ Scraper imported successfully.")

    print("\n----- 2. TESTING CONFIG -----")
    # Mock config to simulate what the server sees
    mock_config = {
        'anti_detection': {'use_proxies': False}, # We try to force False here
        'paths': {'proxy_file': 'features/keyword_gen/proxies.txt'},
        'scraping': {
            'delays': {'min_delay': 1, 'max_delay': 2, 'error_delay': 1},
            'timeouts': {'api_timeout': 10},
            'max_retries': 1
        },
        'api': {'endpoints': ['https://completion.amazon.com/search/complete'], 'marketplaces': {'US': {'mid': 'ATVPDKIKX0DER'}}}
    }
    
    print("\n----- 3. INITIALIZING SCRAPER -----")
    scraper = AmazonSuggestionScraper(mock_config)
    print("✅ Scraper Initialized. Security Lock did NOT trigger.")

    print("\n----- 4. RUNNING SCRAPE -----")
    keywords = scraper.scrape_suggestions("iphone 13")
    print(f"✅ Result: Found {len(keywords)} keywords")
    print(keywords)

except Exception as e:
    print("\n❌ CRITICAL ERROR CAUGHT:")
    print(str(e))
    print("\n💡 This is the exact error causing your 400 Bad Request.")