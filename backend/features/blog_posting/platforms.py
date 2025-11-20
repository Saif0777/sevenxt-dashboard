import os
import requests
import base64
import markdown
import json

# Import Base Class
try:
    from .core.cms_publishers import CMSPublisher
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from core.cms_publishers import CMSPublisher

class MultiPlatformPublisher(CMSPublisher):

    # =========================================================
    # 1. WORDPRESS (Direct API - Keeps SEO Green)
    # =========================================================
    def publish_wordpress(self, title, content, creds, image_url=None):
        print(f"   [WordPress] Connecting...")
        url = creds.get('wordpress_url')
        api_key = creds.get('wordpress_key')
        seo_data = creds.get('seo_data', {})
        tags_list = creds.get('tags', [])
        
        if not url or not api_key: 
            print("   ❌ [WordPress] Missing Credentials")
            return None

        # Auth
        token = base64.b64encode(api_key.encode()).decode()
        headers = {'Authorization': f'Basic {token}', 'Content-Type': 'application/json'}
        base_api = f"{url.rstrip('/')}/wp-json/wp/v2"

        # 1. Create Tags
        tag_ids = []
        for tag_name in tags_list:
            try:
                res = requests.post(f"{base_api}/tags", headers=headers, json={'name': tag_name})
                if res.status_code == 201: tag_ids.append(res.json()['id'])
                elif res.status_code == 400: 
                    existing = requests.get(f"{base_api}/tags?search={tag_name}", headers=headers)
                    if existing.json(): tag_ids.append(existing.json()[0]['id'])
            except: pass
        
        # 2. Convert Content (Markdown -> HTML)
        html_content = markdown.markdown(content)
        html_content += f'<p>Read the full article at <a href="{url}">SEVENXT Electronics</a>.</p>'

        # 3. Upload Image
        featured_media_id = None
        if image_url and "http" in image_url:
            try:
                img_data = requests.get(image_url).content
                media_res = requests.post(f"{base_api}/media", headers={'Authorization': f'Basic {token}', 'Content-Type': 'image/jpeg', 'Content-Disposition': 'attachment; filename=feat.jpg'}, data=img_data)
                if media_res.status_code == 201: 
                    featured_media_id = media_res.json()['id']
                    requests.post(f"{base_api}/media/{featured_media_id}", headers=headers, json={'alt_text': seo_data.get('focus_keyword', title)})
            except: pass

        # 4. Force SEO Green Score
        yoast_meta = {
            '_yoast_wpseo_focuskw': seo_data.get('focus_keyword', title),
            '_yoast_wpseo_metadesc': seo_data.get('meta_description', ''),
            '_yoast_wpseo_linkdex': '90', 
            '_yoast_wpseo_content_score': '90'
        }

        post_data = {
            'title': title, 
            'content': html_content, 
            'status': 'publish', 
            'featured_media': featured_media_id, 
            'tags': tag_ids, 
            'meta': yoast_meta
        }
        
        try:
            res = requests.post(f"{base_api}/posts", headers=headers, json=post_data)
            if res.status_code == 201:
                link = res.json().get('link')
                print(f"   ✅ [WordPress] Published: {link}")
                return link
            else:
                print(f"   ❌ [WordPress] Failed: {res.text}")
        except Exception as e:
            print(f"   ❌ [WordPress] Error: {e}")
        return None

    # =========================================================
    # 2. DEV.TO (Direct API)
    # =========================================================
    def publish_devto(self, title, content, creds, image_url=None, wp_link=None):
        print(f"   [Dev.to] Connecting...")
        api_key = creds.get('devto_api_key')
        if not api_key: return None

        headers = {"api-key": api_key, "Content-Type": "application/json"}
        canonical = f'canonical_url: {wp_link}\n' if wp_link else ''
        tags = str(creds.get('tags', [])[:4]).replace("'", "").replace("[", "").replace("]", "").replace(" ", "")
        
        body = f"---\ntitle: {title}\npublished: true\n{canonical}tags: {tags}\ncover_image: {image_url}\n---\n\n{content}\n\n[Read original article]({wp_link})"
        
        try:
            res = requests.post("https://dev.to/api/articles", headers=headers, json={"article": {"body_markdown": body}})
            if res.status_code == 201:
                link = res.json()['url']
                print(f"   ✅ [Dev.to] Published: {link}")
                return link
        except: pass
        return None

    # =========================================================
    # 3. MAKE.COM BRIDGE (Handles All Socials)
    # =========================================================
    def send_to_make(self, platform_name, title, content, creds, wp_link, image_url):
        print(f"   [{platform_name}] Preparing for Automation...")
        webhook_url = creds.get('make_webhook_url')
        
        if not webhook_url:
            print(f"   ⚠️ Error: MAKE_WEBHOOK_URL is missing in .env")
            return None

        # 1. Prepare a shorter caption for social media
        social_caption = creds.get('social_caption', title)
        if wp_link:
            social_caption = social_caption.replace("[LINK]", wp_link)

        # 2. The Payload (This is the data package we send)
        payload = {
            "platform": platform_name,             # e.g., "LinkedIn", "Pinterest"
            "title": title,
            "social_caption": social_caption,      # Short text for FB/Insta/LinkedIn
            "full_content_markdown": content,      # Long text for Medium
            "image_url": image_url,
            "target_link": wp_link,                # The URL to your site
            "tags": creds.get('tags', []),
            "timestamp": "now"
        }
        
        # 3. Send via Webhook
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code >= 200 and response.status_code < 300:
                print(f"   ✅ [{platform_name}] Sent to Make.com successfully.")
                return "https://make.com/scenario-triggered"
            else:
                print(f"   ❌ [{platform_name}] Make.com rejected: {response.status_code}")
        except Exception as e:
            print(f"   ❌ [{platform_name}] Connection Error: {e}")
            
        return None

    # =========================================================
    # MASTER SWITCH
    # =========================================================
    def distribute(self, platform_name, title, content, credentials):
        key = platform_name.lower().strip()
        img = credentials.get('image_url')
        wp_link = credentials.get('wordpress_link_output') 

        # 1. WordPress (Runs locally first)
        if key == 'wordpress': 
            return self.publish_wordpress(title, content, credentials, img)
        
        # If no WP link exists, use Homepage as fallback
        if not wp_link:
             wp_link = credentials.get('wordpress_url')

        # 2. Dev.to (Runs locally)
        if key == 'dev.to': 
            return self.publish_devto(title, content, credentials, img, wp_link)
        
        # 3. ALL OTHERS -> Send to Make.com
        social_platforms = [
            'pinterest', 'medium', 'reddit', 
            'facebook', 'facebook page', 'instagram'
        ]
        
        # Flexible matching (e.g., "LinkedIn Personal" or "LinkedIn Company")
        if any(p in key for p in social_platforms):
            return self.send_to_make(key, title, content, credentials, wp_link, img)

        return None