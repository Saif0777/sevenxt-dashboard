import os
import time
import undetected_chromedriver as uc

def setup_profiles():
    print("="*50)
    print("   MANUAL LOGIN SETUP TOOL")
    print("   1. Pinterest (CRITICAL: Log in & Create a Board named 'Tech')")
    print("   2. Medium (Log in via Google/Email)")
    print("   3. Reddit (Log in)")
    print("="*50)

    current_dir = os.getcwd()
    profile_path = os.path.join(current_dir, "selenium_profile")
    
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")

    try:
        driver = uc.Chrome(options=options, headless=False, use_subprocess=True)
        
        # Open Tabs
        driver.get("https://www.pinterest.com/login/")
        driver.execute_script("window.open('https://medium.com/m/signin', '_blank');")
        driver.execute_script("window.open('https://www.reddit.com/login', '_blank');")
        
        print("\n✅ BROWSER OPENED!")
        print("---------------------------------------------------")
        print("👉 TASK 1: Log in to all 3 websites.")
        print("👉 TASK 2: On Pinterest, go to your Profile -> Saved -> '+' -> Board. Create a board named 'Tech'.")
        print("👉 TASK 3: Close the browser window when done.")
        print("---------------------------------------------------")
        
        input("\nPress ENTER here AFTER you have closed the browser... ")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    setup_profiles()