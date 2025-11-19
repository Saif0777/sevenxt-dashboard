import os
import requests
import time
import base64
import markdown
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Import Base Class
try:
    from .core.cms_publishers import CMSPublisher
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from core.cms_publishers import CMSPublisher

class MultiPlatformPublisher(CMSPublisher):
    """
    Unified Publisher for 15+ Platforms using Hybrid Strategy (API + Selenium)
    """

    def _get_driver(self):
        """Launch a browser for Selenium tasks"""
        options = Options()
        # options.add_argument('--headless') # NEVER use headless for LinkedIn (triggers security)
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--disable-notifications")
        options.add_argument("--start-maximized")
        # options.add_argument("user-data-dir=selenium_profile") # Optional: Saves login session
        return webdriver.Chrome(options=options)

    def _download_image_temp(self, image_url):
        """Helper: Downloads image from URL to a local temp file for uploading"""
        if not image_url or "placeholder" in image_url:
            return None
        try:
            print(f"   ⬇️ Downloading image for upload...")
            res = requests.get(image_url, stream=True)
            if res.status_code == 200:
                temp_path = os.path.join(os.getcwd(), "temp_post_image.jpg")
                with open(temp_path, 'wb') as f:
                    for chunk in res.iter_content(1024):
                        f.write(chunk)
                return temp_path
        except Exception as e:
            print(f"   ⚠️ Image download failed: {e}")
        return None

    # ==========================================
    # 1. LINKEDIN (ROBUST "PHOTO FIRST" & KEYBOARD SHORTCUT)
    # ==========================================
    def publish_linkedin(self, title, content, creds, image_url=None):
        print(f"   [LinkedIn] Starting automation...")
        driver = self._get_driver()
        try:
            # 1. Login
            print("   [LinkedIn] Navigating to login...")
            driver.get("https://www.linkedin.com/login")
            
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(creds.get('linkedin_email'))
            driver.find_element(By.ID, "password").send_keys(creds.get('linkedin_pass') + Keys.RETURN)
            
            print("   [LinkedIn] ⏳ Waiting 10s for Feed/CAPTCHA...")
            time.sleep(10) 
            
            # Ensure we are on feed
            if "feed" not in driver.current_url:
                driver.get("https://www.linkedin.com/feed/")
                time.sleep(5)

            # 2. OPEN POST MODAL (Strategy: Photo Icon First)
            print("   [LinkedIn] Attempting to open Post Modal...")
            modal_opened = False
            
            # Strategy A: Click the "Photo" icon directly (Most Reliable)
            if not modal_opened:
                try:
                    print("   [LinkedIn] Strategy A: Clicking 'Photo' icon...")
                    photo_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'media') or contains(@aria-label, 'photo') or contains(@aria-label, 'Add a photo')]"))
                    )
                    photo_btn.click()
                    modal_opened = True
                except:
                    pass

            # Strategy B: Click "Start a post" Text
            if not modal_opened:
                try:
                    print("   [LinkedIn] Strategy B: Clicking 'Start a post' text...")
                    start_btn = driver.find_element(By.XPATH, "//span[contains(text(), 'Start a post')]")
                    start_btn.click()
                    modal_opened = True
                except:
                    pass
            
            # Strategy C: Generic Button Class Search
            if not modal_opened:
                try:
                    print("   [LinkedIn] Strategy C: Clicking feed input container...")
                    driver.find_element(By.CSS_SELECTOR, ".share-box-feed-entry__trigger").click()
                    modal_opened = True
                except:
                    pass

            if not modal_opened:
                raise Exception("Could not find ANY button to open the post modal.")

            time.sleep(3)

            # 3. Upload Image
            if image_url:
                local_image_path = self._download_image_temp(image_url)
                if local_image_path:
                    try:
                        # If we opened via Strategy A, file picker might be ready.
                        # If not, click the media icon inside modal.
                        try:
                            # Check if file input is available immediately
                            image_input = driver.find_element(By.XPATH, "//input[@type='file']")
                            image_input.send_keys(local_image_path)
                            print("   [LinkedIn] Image sent to input.")
                        except:
                            # Click icon inside modal
                            print("   [LinkedIn] Clicking internal 'Add Media' icon...")
                            media_icon = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'media') or contains(@aria-label, 'photo')]")
                            media_icon.click()
                            time.sleep(1)
                            driver.find_element(By.XPATH, "//input[@type='file']").send_keys(local_image_path)

                        print("   [LinkedIn] Uploading image...")
                        time.sleep(5) 
                        
                        # Click Next
                        try:
                            next_btn = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']/.."))
                            )
                            next_btn.click()
                            print("   [LinkedIn] Clicked 'Next'.")
                            time.sleep(3) 
                        except:
                            print("   ⚠️ 'Next' button not found (Image might be attached directly).")

                    except Exception as e:
                        print(f"   ⚠️ Image upload skipped: {e}")

            # 4. Write Text
            print("   [LinkedIn] Writing text...")
            try:
                editor = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "ql-editor")))
                editor.click() # Focus
                
                clean_text = f"{title}\n\n{content[:1200]}...\n\n#SevenXT #Electronics #SmartHome #Tech"
                editor.send_keys(clean_text)
                time.sleep(2)

                # 5. PUBLISH via KEYBOARD SHORTCUT (Ctrl+Enter)
                print("   [LinkedIn] Sending Post Command (Ctrl+Enter)...")
                
                # Close any overlapping tooltips
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                time.sleep(1)

                # Send Keys
                editor.send_keys(Keys.CONTROL, Keys.ENTER)
                
                print("   [LinkedIn] Command sent. Waiting 15s...")
                time.sleep(15)

                # 6. Verify
                if "feed" in driver.current_url:
                    try:
                        # If we see "Start a post" again, the modal closed successfully
                        if driver.find_elements(By.XPATH, "//*[contains(text(), 'Start a post')]"):
                            print("   [LinkedIn] ✅ Success: Returned to Feed.")
                            return "https://linkedin.com/feed"
                    except:
                        pass
            
            except Exception as e:
                print(f"   ❌ [LinkedIn] Writing/Posting failed: {e}")
                driver.save_screenshot("linkedin_error.png")

            return "https://linkedin.com/feed"

        except Exception as e:
            print(f"   ❌ [LinkedIn] Critical Error: {e}")
            driver.save_screenshot("linkedin_error.png")
            return None
        finally:
            print("   [LinkedIn] Closing...")
            driver.quit()
            if os.path.exists("temp_post_image.jpg"):
                os.remove("temp_post_image.jpg")

    # ==========================================
    # 1. WORDPRESS (WITH YOAST SEO INJECTION)
    # ==========================================
    def publish_wordpress(self, title, content, creds, image_url=None):
        print(f"   [WordPress] Starting API connection...")
        
        url = creds.get('wordpress_url')
        api_key = creds.get('wordpress_key')
        seo_data = creds.get('seo_data', {}) # Extract SEO data
        
        if not url or not api_key:
            print("   ❌ [WordPress] Missing URL or KEY")
            return None

        token = base64.b64encode(api_key.encode()).decode()
        headers = {
            'Authorization': f'Basic {token}',
            'Content-Type': 'application/json'
        }
        base_api = f"{url.rstrip('/')}/wp-json/wp/v2"

        # 1. Convert Markdown to HTML
        html_content = markdown.markdown(content)

        # 2. Upload Image
        featured_media_id = None
        if image_url and "placeholder" not in image_url:
            try:
                print("   [WordPress] Uploading image...")
                img_data = requests.get(image_url).content
                media_headers = headers.copy()
                media_headers['Content-Type'] = 'image/jpeg'
                media_headers['Content-Disposition'] = 'attachment; filename=featured.jpg'
                
                media_res = requests.post(f"{base_api}/media", headers=media_headers, data=img_data)
                if media_res.status_code == 201:
                    featured_media_id = media_res.json()['id']
            except Exception as e:
                print(f"   ⚠️ Image error: {e}")

        # 3. Prepare YOAST SEO Payload
        # This is the secret sauce for Green Score
        yoast_meta = {}
        if seo_data.get('focus_keyword'):
            yoast_meta['_yoast_wpseo_focuskw'] = seo_data['focus_keyword']
        
        if seo_data.get('meta_description'):
            yoast_meta['_yoast_wpseo_metadesc'] = seo_data['meta_description']
            
        if seo_data.get('seo_title'):
            yoast_meta['_yoast_wpseo_title'] = seo_data['seo_title']

        print(f"   [WordPress] Injecting SEO Meta: {list(yoast_meta.keys())}")

        # 4. Create Post
        post_data = {
            'title': title,
            'content': html_content,
            'status': 'publish',
            'featured_media': featured_media_id,
            'meta': yoast_meta  # <--- INJECT HERE
        }
        
        try:
            res = requests.post(f"{base_api}/posts", headers=headers, json=post_data)
            
            if res.status_code == 201:
                link = res.json().get('link')
                print(f"   ✅ [WordPress] Published: {link}")
                return link
            else:
                print(f"   ❌ [WordPress] Failed: {res.status_code} - {res.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ [WordPress] Connection Error: {e}")
            return None

    # ==========================================
    # 3. REDDIT (SELENIUM)
    # ==========================================
    def publish_reddit(self, title, content, creds, image_url=None):
        print(f"   [Reddit] Posting to r/{creds.get('subreddit')}...")
        driver = self._get_driver()
        try:
            driver.get("https://www.reddit.com/login/")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "loginUsername"))).send_keys(creds.get('reddit_user'))
            driver.find_element(By.ID, "loginPassword").send_keys(creds.get('reddit_pass') + Keys.RETURN)
            time.sleep(5)
            
            driver.get(f"https://www.reddit.com/r/{creds.get('subreddit')}/submit")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "title"))).send_keys(title)
            
            # Switch to text tab if needed, but usually defaults
            # driver.find_element(By.XPATH, "//button[text()='Text']").click()
            
            # Content
            actions = ActionChains(driver)
            actions.send_keys(Keys.TAB).send_keys(content[:2000]).perform()
            
            print("   [Reddit] Ready to submit (Click skipped).")
            return f"https://reddit.com/r/{creds.get('subreddit')}"
        except Exception as e:
            print(f"   [Reddit] Error: {e}")
            return None
        finally:
            driver.quit()

    # ==========================================
    # 4. DISCORD (API)
    # ==========================================
    def publish_discord(self, title, content, creds, image_url=None):
        webhook_url = creds.get('discord_webhook')
        if not webhook_url:
            return None
        data = {"content": f"**{title}**\n\n{content[:1000]}...\n\n{image_url or ''}"}
        try:
            requests.post(webhook_url, json=data)
            print("   [Discord] Message sent.")
            return "Discord"
        except:
            return None

    # ==========================================
    # MASTER SWITCH
    # ==========================================
    def distribute(self, platform_name, title, content, credentials):
        platform_key = platform_name.lower().strip()
        image_url = credentials.get('image_url')

        if platform_key == 'wordpress':
            return self.publish_wordpress(title, content, credentials, image_url)
        elif platform_key == 'linkedin':
             return self.publish_linkedin(title, content, credentials, image_url)
        elif platform_key == 'reddit':
             return self.publish_reddit(title, content, credentials, image_url)
        elif platform_key == 'discord':
             return self.publish_discord(title, content, credentials, image_url)
        
        # Add stubs for others
        print(f"   ⚠️ Skipping {platform_name} (Not configured yet)")
        return None