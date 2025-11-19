import os
import sys
import pandas as pd

# --- PATH FIX: Force Python to find the 'keyword_gen' folder ---
current_dir = os.path.dirname(os.path.abspath(__file__))
keyword_gen_folder = os.path.join(current_dir, 'keyword_gen')
sys.path.append(keyword_gen_folder)

# Now import directly from scraper.py
try:
    from scraper import AmazonSuggestionScraper
except ImportError:
    # Backup import if the first one fails
    from features.keyword_gen.scraper import AmazonSuggestionScraper

def process_keyword_file(input_filepath):
    """
    Receives the uploaded file path, runs the scraper, 
    and returns the path to the new result file.
    """
    try:
        # 1. Define Output Path
        directory = os.path.dirname(input_filepath)
        filename = os.path.basename(input_filepath)
        output_filepath = os.path.join(directory, f"processed_{filename}")

        # 2. Instantiate the Scraper Logic
        print(f"Initializing Scraper with input: {input_filepath}")
        scraper = AmazonSuggestionScraper(input_filepath, output_filepath)
        
        # 3. Run It
        print("Starting Amazon Scraper...")
        scraper.scrape_suggestions()
        print("Scraping Complete.")
        
        # 4. Return the path so Flask can send it to the user
        return output_filepath

    except Exception as e:
        print(f"Wrapper Error: {e}")
        return None