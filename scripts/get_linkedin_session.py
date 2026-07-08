from playwright.sync_api import sync_playwright
import os

def main():
    os.makedirs("auth", exist_ok=True)
    state_file = "auth/linkedin_state.json"
    
    print("Launching headed browser for LinkedIn login...")
    print("Please log in manually. Once you reach the LinkedIn feed, the session will be saved automatically.")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context()
        page = context.new_page()
        
        page.goto("https://www.linkedin.com/login")
        
        # Wait for the feed to load after login
        print("Waiting for login to complete and feed to load...")
        page.wait_for_url("https://www.linkedin.com/feed/", timeout=300000) # 5 minutes timeout
        page.wait_for_load_state("domcontentloaded")
        
        # Save state
        context.storage_state(path=state_file)
        print(f"✅ Login successful! Session saved to {state_file}")
        print("IMPORTANT: Add the contents of this file to your GitHub Repository Secrets as LINKEDIN_STATE")
        
        browser.close()

if __name__ == "__main__":
    main()
