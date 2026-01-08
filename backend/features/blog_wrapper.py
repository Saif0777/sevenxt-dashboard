import os
import sys
import asyncio
from dotenv import load_dotenv

# --- 1. FORCE LOAD .ENV FROM BACKEND ROOT ---
# Get the absolute path to the 'backend' folder
current_file_path = os.path.abspath(__file__)             # features/blog_wrapper.py
features_dir = os.path.dirname(current_file_path)         # features/
backend_dir = os.path.dirname(features_dir)               # backend/
env_path = os.path.join(backend_dir, '.env')              # backend/.env

# Explicitly load this specific file (override any cached vars)
load_dotenv(dotenv_path=env_path, override=True)

# --- 2. DEBUG PRINT (Check the Console when you save) ---
print(f"🔍 DEBUG: Loading .env from: {env_path}")
print(f"🔍 DEBUG: WordPress Key Loaded? {'YES' if os.getenv('WORDPRESS_URL') else 'NO'}")
print(f"🔍 DEBUG: Dev.to Key Loaded?    {'YES' if os.getenv('DEVTO_API_KEY') else 'NO'}")
# ---------------------------------------------

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from blog_posting.core.generate_blog import GroqAPI 
    from blog_posting.platforms import MultiPlatformPublisher
    from blog_posting.core.image_api import ImageGenerator
except ImportError:
    GroqAPI = None

async def run_automation_logic(title, description, platforms, forced_image=None, product_link=None, brand_name="SEVENXT"):
    log = []
    log.append(f"🚀 Job Started: {title}")
    
    # 1. Generate
    groq = GroqAPI()
    keywords = [k.strip() for k in description.split(',')] if (description and ',' in description) else [title]
    
    log.append(f"🤖 Generating Content for Brand: {brand_name}...")
    
    blog_data = await groq.generate_blog(
        topic=title,
        keywords=keywords,
        brand_name=brand_name, # <--- DYNAMIC BRAND NAME
        industries=["Electronics"],
        context=description
    )
    
    final_content = blog_data['content']
    final_title = blog_data['title']

    # 2. Image Handling
    generated_image = "https://via.placeholder.com/800x400?text=Product+Image"
    
    if forced_image and "http" in forced_image:
        log.append("📸 Using Amazon Product Image.")
        generated_image = forced_image

    # 3. Credentials & Payload
    creds = {
        "wordpress_url": os.getenv("WORDPRESS_URL"),
        "wordpress_key": os.getenv("WORDPRESS_KEY"),
        "devto_api_key": os.getenv("DEVTO_API_KEY"),
        "make_webhook_url": os.getenv("MAKE_WEBHOOK_URL"),
        "image_url": generated_image,
        
        # --- NEW DATA PASSED HERE ---
        "wp_category": blog_data.get('wp_category', 'Electronics'), 
        "wp_tags": blog_data.get('wp_tags', []), 
        
        "tags": blog_data.get('keywords', []), # Fallback for old logic
        "seo_data": {
            "focus_keyword": blog_data['focus_keyphrase'],
            "meta_description": blog_data['meta_description']
        },
        "social_caption": f"{blog_data['meta_description']} #SevenXT",
        "wordpress_link_output": product_link if product_link else os.getenv("WORDPRESS_URL")
    }

    # 4. Publish
    publisher = MultiPlatformPublisher()
    wp_link = None
    
    if "WordPress" in platforms:
        log.append("📡 Publishing to WordPress...")
        # Note: We pass product_link here if you want to use it as a canonical or source, 
        # but usually we just publish content. 
        wp_link = publisher.distribute("wordpress", final_title, final_content, creds)
        
        if wp_link:
            log.append(f"✅ WP Success: {wp_link}")
            # Update the link for other platforms to point to the Blog Post
            creds['wordpress_link_output'] = wp_link
        else:
            log.append("❌ WP Failed.")

    # 5. Distribute to Others (n8n/Make)
    for platform in platforms:
        if platform == "WordPress": continue
        
        log.append(f"📡 Sending {platform} to Automation...")
        res = publisher.distribute(platform, final_title, final_content, creds)
        if res: log.append(f"✅ Sent: {platform}")
        else: log.append(f"❌ Failed: {platform}")

    log.append("🏁 Job Complete.")
    
    # 6. Return Preview Data
    return {
        "log": log, 
        "status": "success",
        "preview": {
            "title": final_title,
            "content": final_content,
            "image": generated_image, 
            "link": wp_link or product_link or "#"
        }
    }

# UPDATED: Accepts the new arguments
def start_blog_automation(title, description, platforms, forced_image=None, product_link=None, brand_name="SEVENXT"):
    return asyncio.run(run_automation_logic(title, description, platforms, forced_image, product_link, brand_name))