import json
import os
import sys
import time
from playwright.sync_api import sync_playwright

def main():
    state_file = "auth/linkedin_state.json"
    if not os.path.exists(state_file):
        print(f"Error: {state_file} not found. Run get_linkedin_session.py first.")
        sys.exit(1)
        
    if not os.path.exists("post.json"):
        print("Error: post.json not found.")
        sys.exit(1)
        
    with open("post.json", "r", encoding="utf-8") as f:
        post_data = json.load(f)
        
    post_text = post_data.get("post_text", "")
    if not post_text:
        print("Error: post_text is empty in post.json")
        sys.exit(1)
        
    image_path = os.path.abspath("docs/images/hero.png")
    has_image = os.path.exists(image_path)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=os.environ.get("CI") == "true",
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            storage_state=state_file,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            print("Navigating to LinkedIn feed...")
            page.goto("https://www.linkedin.com/feed/")
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(5000)
            
            # Click "Start a post"
            print("Clicking 'Start a post'...")
            start_post_btn = page.locator('button:has-text("Start a post")').first
            start_post_btn.click()
            page.wait_for_timeout(2000)
            
            # Find the editor and type the text
            print("Pasting post content...")
            editor = page.locator('div[role="textbox"]').first
            editor.click()
            
            # Because clipboard paste is safer for emojis and formatting, we will use it if possible, 
            # but page.keyboard.insert_text() handles emojis perfectly in Playwright.
            page.keyboard.insert_text(post_text)
            page.wait_for_timeout(2000)
            
            if has_image:
                print(f"Uploading image: {image_path}")
                # LinkedIn's image upload input is hidden. We trigger the file chooser.
                with page.expect_file_chooser() as fc_info:
                    # Click the "Add media" button (aria-label="Add media")
                    media_btn = page.locator('button[aria-label="Add media"]').first
                    media_btn.click()
                file_chooser = fc_info.value
                file_chooser.set_files(image_path)
                page.wait_for_timeout(3000)
                
                # Click "Next" or "Done" on the image preview modal
                done_btn = page.locator('button:has-text("Next")').first
                if not done_btn.is_visible():
                    done_btn = page.locator('button:has-text("Done")').first
                if done_btn.is_visible():
                    done_btn.click()
                page.wait_for_timeout(2000)
                
            # Click the "Post" button
            print("Clicking 'Post'...")
            post_btn = page.locator('button:has-text("Post")').last
            post_btn.click()
            
            # Wait for success notification or feed reload
            page.wait_for_timeout(5000)
            print("Successfully posted to LinkedIn!")
            
        except Exception as e:
            print(f"Error during posting: {e}")
            page.screenshot(path="error.png")
            print("Screenshot saved to error.png")
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    main()
