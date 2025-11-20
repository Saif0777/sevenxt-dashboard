import os
import sys
import asyncio
from dotenv import load_dotenv

# 1. Load Env Vars
load_dotenv() 

# 2. Fix Path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from blog_posting.core.generate_blog import GroqAPI 
    from blog_posting.platforms import MultiPlatformPublisher
    from blog_posting.core.image_api import ImageGenerator
except ImportError as e:
    print(f"❌ CRITICAL IMPORT ERROR: {e}")
    GroqAPI = None
    MultiPlatformPublisher = None
    ImageGenerator = None

async def run_automation_logic(title, description, platforms):
    log = []
    log.append(f"🚀 Job Started: {title}")
    
    if not GroqAPI:
        return {"log": ["❌ Error: Core files missing."], "status": "error"}

    # --- KEYWORDS ---
    keywords = [k.strip() for k in description.split(' ')] if description else [title]

    # --- DATA HOLDER ---
    final_title = title
    final_content = ""
    generated_image = "https://via.placeholder.com/800x400?text=SevenXT+Electronics"

    # ================================
    # STEP 1: GENERATE TEXT
    # ================================
    try:
        log.append("🤖 AI Agent: Generating SEO Blog Post...")
        groq = GroqAPI()
        
        if not os.getenv("GROQ_API_KEY"):
            raise Exception("GROQ_API_KEY missing")

        blog_data = await groq.generate_blog(
            topic=title,
            keywords=keywords[:5], 
            brand_name="SEVENXT ELECTRONICS",
            industries=["Consumer Electronics", "Home Theater", "Smart Office","tv accessories","audio devices","phone accessories","mobile cases"]
        )
        
        final_content = blog_data['content']
        final_title = blog_data['title']
        # Use the AI's better keywords
        if blog_data.get('keywords'):
            keywords = blog_data['keywords']

        log.append(f"✅ Text Generated: {len(final_content.split())} words.")

    except Exception as e:
        print(f"⚠️ AI Service Error: {e}")
        log.append(f"⚠️ AI Issue. Using Fallback Content.")
        final_title = f"{title}: The SevenXT Guide"
        final_content = f"# {final_title}\n\nRead more at SevenXT Electronics."

    # ================================
    # STEP 2: GENERATE IMAGE
    # ================================
    if ImageGenerator:
        try:
            log.append("🎨 AI Agent: Searching Pexels for visuals...")
            img_gen = ImageGenerator()
            search_prompt = f"{title} technology"
            img_result = img_gen.generate_image(prompt=search_prompt)
            
            if "http" in img_result:
                generated_image = img_result
                log.append(f"✅ Image Found: {generated_image}")
            else:
                log.append("⚠️ No relevant image found. Using default.")
        except Exception as img_e:
            log.append(f"⚠️ Image search skipped: {img_e}")
    
    # ================================
    # STEP 3: PREPARE CREDENTIALS & PAYLOAD
    # ================================
    
    # Create a short description for Social Media Captions (First 200 chars of content)
    social_caption = f"{final_title} - \n\n{final_content[:180]}...\n\nRead more: [LINK]\n\n#{keywords[0]} #SevenXT"

    seo_payload = {
        "focus_keyword": keywords[0] if keywords else title,
        "meta_description": f"Discover everything about {title} with SEVENXT ELECTRONICS.",
        "seo_title": final_title
    }

    credentials = {
        # --- DIRECT API KEYS ---
        "wordpress_url": os.getenv("WORDPRESS_URL"),
        "wordpress_key": os.getenv("WORDPRESS_KEY"),
        "devto_api_key": os.getenv("DEVTO_API_KEY"),
        
        # --- THE AUTOMATION BRIDGE ---
        "make_webhook_url": os.getenv("MAKE_WEBHOOK_URL"), # <--- CRITICAL NEW LINE
        
        # --- PAYLOAD DATA ---
        "image_url": generated_image,
        "tags": keywords, 
        "seo_data": seo_payload,
        "social_caption": social_caption # Pass this for FB/LinkedIn/Insta
    }

    # ================================
    # STEP 4: PUBLISH
    # ================================
    publisher = MultiPlatformPublisher()
        
    # 1. Publish WordPress FIRST (The Source of Truth)
    wp_link = None
    if "WordPress" in platforms:
        log.append("📡 Publishing to WordPress (Master)...")
        wp_link = publisher.distribute("wordpress", final_title, final_content, credentials)
        if wp_link:
            log.append(f"   ✅ WP Live: {wp_link}")
            credentials['wordpress_link_output'] = wp_link 
        else:
            log.append("   ❌ WP Failed. Social posts will use Homepage URL.")
            credentials['wordpress_link_output'] = os.getenv("WORDPRESS_URL") # Fallback
        
    # 2. Publish Others (Dev.to = API, Rest = Make.com)
    for platform in platforms:
        if platform == "WordPress": continue 
            
        log.append(f"📡 Routing to {platform}...")
        
        # The distribute function now handles the switch to Make
        url = publisher.distribute(platform, final_title, final_content, credentials)
            
        if url: 
            if "make.com" in str(url):
                log.append(f"   ✅ Sent to Make Automation: {platform}")
            else:
                log.append(f"   ✅ Published: {platform}")
        else: 
            log.append(f"   ⚠️ Failed: {platform}")
            
        await asyncio.sleep(1) # Slight delay to prevent rate limits

    log.append("🏁 Campaign Finished.")
    
    return {
        "log": log, 
        "status": "success",
        "preview": {
            "title": final_title,
            "image": generated_image,
            "link": wp_link
        }
    }

def start_blog_automation(title, description, platforms):
    return asyncio.run(run_automation_logic(title, description, platforms))