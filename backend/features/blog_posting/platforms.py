import os
import requests
import base64
import markdown
import json
import urllib3
import time
from io import BytesIO
from PIL import Image

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    from .cms_publishers import CMSPublisher
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from core.cms_publishers import CMSPublisher

class MultiPlatformPublisher(CMSPublisher):

    def _get_or_create_term(self, base_api, headers, taxonomy, name):
        """
        Robust Helper: Handles spaces and special characters in tags/categories correctly.
        """
        if not name: return None
        
        try:
            # 1. Search existing (Using params= handles URL encoding automatically)
            # This fixes the "Smart TV" -> "Smart%20TV" bug
            search_res = requests.get(
                f"{base_api}/{taxonomy}", 
                headers=headers, 
                params={'search': name}, 
                verify=False, 
                timeout=10
            )
            
            if search_res.status_code == 200:
                items = search_res.json()
                # Exact match check
                for item in items:
                    if item['name'].lower() == name.lower():
                        print(f"   found existing {taxonomy}: {name} -> ID {item['id']}")
                        return item['id']
            
            # 2. Create if not found
            create_res = requests.post(
                f"{base_api}/{taxonomy}", 
                headers=headers, 
                json={"name": name}, 
                verify=False, 
                timeout=10
            )
            
            if create_res.status_code == 201:
                new_id = create_res.json()['id']
                print(f"   created new {taxonomy}: {name} -> ID {new_id}")
                return new_id
                
        except Exception as e:
            print(f"   ⚠️ Error setting {taxonomy} '{name}': {e}")
            
        return None

    def publish_wordpress(self, title, content, creds, image_url=None):
        print(f"   [WordPress] Connecting...")
        url = creds.get('wordpress_url')
        api_key = creds.get('wordpress_key')
        seo_data = creds.get('seo_data', {})
        focus_kw = seo_data.get('focus_keyword', title)
        product_link = creds.get('wordpress_link_output')
        
        category_name = creds.get('wp_category', 'Electronics')
        tag_names = creds.get('wp_tags', [])
        
        if not url or not api_key: return None

        token = base64.b64encode(api_key.encode()).decode()
        headers = {'Authorization': f'Basic {token}', 'Content-Type': 'application/json'}
        base_api = f"{url.rstrip('/')}/wp-json/wp/v2"

        # --- STEP 1: RESOLVE CATEGORIES & TAGS (FIXED) ---
        print(f"   [WP] Resolving Category: {category_name} & Tags: {tag_names}")
        
        cat_id = self._get_or_create_term(base_api, headers, 'categories', category_name)
        tag_ids = []
        for tag in tag_names:
            tid = self._get_or_create_term(base_api, headers, 'tags', tag)
            if tid: tag_ids.append(tid)

        # --- STEP 2: OPTIMIZED IMAGE UPLOAD ---
        featured_media_id = None
        media_link = None 

        if image_url and "http" in image_url:
            try:
                dl_headers = {'User-Agent': 'Mozilla/5.0'}
                img_response = requests.get(image_url, headers=dl_headers, verify=False, timeout=30)
                
                if img_response.status_code == 200:
                    image_obj = Image.open(BytesIO(img_response.content))
                    if image_obj.mode in ("RGBA", "P"): image_obj = image_obj.convert("RGB")
                    
                    if image_obj.width > 1200:
                        ratio = 1200 / float(image_obj.width)
                        new_height = int((float(image_obj.height) * float(ratio)))
                        image_obj = image_obj.resize((1200, new_height), Image.Resampling.LANCZOS)

                    img_buffer = BytesIO()
                    image_obj.save(img_buffer, format="JPEG", quality=85, optimize=True)
                    
                    filename = f"sevenxt_{int(time.time())}.jpg"
                    media_headers = {
                        'Authorization': f'Basic {token}',
                        'Content-Type': 'image/jpeg',
                        'Content-Disposition': f'attachment; filename={filename}'
                    }
                    
                    media_res = requests.post(f"{base_api}/media", headers=media_headers, data=img_buffer.getvalue(), timeout=60)
                    
                    if media_res.status_code == 201: 
                        media_json = media_res.json()
                        featured_media_id = media_json['id']
                        media_link = media_json['source_url']
                        requests.post(f"{base_api}/media/{featured_media_id}", headers=headers, json={'alt_text': focus_kw}, timeout=10)
                        print("   ✅ Image Uploaded Successfully")

            except Exception as e:
                print(f"   ⚠️ Image Error: {e}")

        # --- STEP 3: CONTENT FORMATTING ---
        html_content = markdown.markdown(content, extensions=['nl2br', 'extra'])
        
        # Inject Buy Button
        if product_link:
            cta_html = f'''
            <div style="margin-bottom: 20px; padding: 15px; background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; text-align: center;">
                <p style="margin: 0 0 10px 0; font-weight: bold; color: #166534;">Compatible with your device</p>
                <a href="{product_link}" target="_blank" rel="nofollow" style="background-color: #eab308; color: black; padding: 10px 20px; text-decoration: none; font-weight: bold; border-radius: 5px; display: inline-block;">
                   Check Price on Amazon.in
                </a>
            </div>
            '''
            html_content = cta_html + "\n" + html_content

        if media_link:
            img_html = f'<img src="{media_link}" alt="{focus_kw}" style="width:100%; border-radius:8px; margin-bottom:20px;" />'
            html_content = img_html + "\n" + html_content

        html_content += f'<p>Check out more electronics at <a href="{url}">SevenXT Electronics</a>.</p>'
        html_content += f'<p><small>Reference: Read more about <a href="https://en.wikipedia.org/wiki/Consumer_electronics" target="_blank">Consumer Electronics on Wikipedia</a>.</small></p>'

        # Meta Payload
        yoast_meta = {
            '_yoast_wpseo_focuskw': focus_kw,
            '_yoast_wpseo_metadesc': seo_data.get('meta_description', ''),
            '_yoast_wpseo_linkdex': '90' 
        }

        post_data = {
            'title': title, 
            'content': html_content, 
            'status': 'publish', 
            'featured_media': featured_media_id, 
            'meta': yoast_meta,
            'categories': [cat_id] if cat_id else [], # Fixed
            'tags': tag_ids # Fixed
        }
        
        try:
            res = requests.post(f"{base_api}/posts", headers=headers, json=post_data, timeout=60)
            if res.status_code == 201:
                link = res.json().get('link')
                print(f"   ✅ Published to WP: {link}")
                return link
            else:
                print(f"   ❌ Publish Failed: {res.status_code} {res.text[:100]}")
        except Exception as e: 
            print(f"   ❌ Publish Error: {e}")
        
        return None

    def publish_devto(self, title, content, creds, image_url, canonical_url=None):
        return None 

    def distribute(self, platform_name, title, content, credentials):
        key = platform_name.lower().strip()
        img = credentials.get('image_url')
        if key == 'wordpress': 
            return self.publish_wordpress(title, content, credentials, img)
        return None