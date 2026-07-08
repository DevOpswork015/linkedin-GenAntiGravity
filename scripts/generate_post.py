import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY not set")
        return
        
    client = Groq(api_key=api_key)
    
    with open("prompt_template.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
        
    print("Generating LinkedIn post with Llama 3.3...")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            response_content = completion.choices[0].message.content
            break # Success, exit retry loop
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                print("Max retries reached. Exiting.")
                return
            print("Retrying...")
            
    # Extract json
    json_str = response_content
    match = re.search(r"```json\s*(.*?)\s*```", response_content, re.DOTALL)
    if match:
        json_str = match.group(1)
        
    try:
        post_data = json.loads(json_str)
        # Ensure directory exists before saving
        os.makedirs(os.path.dirname("post.json") or ".", exist_ok=True)
        with open("post.json", "w", encoding="utf-8") as f:
            json.dump(post_data, f, indent=2, ensure_ascii=False)
        print("Successfully generated post.json")
    except json.JSONDecodeError as e:
        print("Failed to parse JSON response from Groq:")
        print(response_content)
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
