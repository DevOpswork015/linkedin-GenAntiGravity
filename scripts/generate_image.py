import json
import urllib.parse
import urllib.request
import os

def download_image(prompt, filepath):
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1200&height=630&nologo=true"
    print(f"Downloading image for prompt: {prompt}")
    for attempt in range(3):
        try:
            urllib.request.urlretrieve(url, filepath)
            print(f"Saved {filepath}")
            return
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            import time
            time.sleep(2)
    print(f"Failed to download image after 3 attempts.")

def main():
    if not os.path.exists("post.json"):
        print("post.json not found. Run generate_post.py first.")
        return
        
    with open("post.json", "r") as f:
        post_data = json.load(f)
        
    os.makedirs("docs/images", exist_ok=True)
    
    hero_prompt = post_data.get("hero_image_prompt", "Tech blog banner")
    download_image(hero_prompt, "docs/images/hero.png")

if __name__ == "__main__":
    main()
