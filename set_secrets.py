import os
import sys
import requests
from base64 import b64encode
from nacl import encoding, public
from dotenv import load_dotenv

load_dotenv()

# We will use GITHUB_CLASSIC_PAT if available, else GITHUB_PAT
TOKEN = os.environ.get("GITHUB_CLASSIC_PAT") or os.environ.get("GITHUB_PAT")
if not TOKEN:
    print("No GitHub token found in .env")
    sys.exit(1)
    
REPO = "DevOpswork015/medicum-GenAntiGravity-"
HEADERS = {
    "Authorization": f"token {TOKEN.strip()}",
    "Accept": "application/vnd.github.v3+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

def encrypt(public_key: str, secret_value: str) -> str:
    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")

def main():
    # Get repo public key
    print(f"Fetching public key for repo {REPO}...")
    r = requests.get(f"https://api.github.com/repos/{REPO}/actions/secrets/public-key", headers=HEADERS)
    if r.status_code != 200:
        print(f"Error getting public key: {r.status_code} {r.text}")
        sys.exit(1)
    
    key_data = r.json()
    key_id = key_data["key_id"]
    public_key = key_data["key"]
    
    # Secrets to upload
    secrets = {}
    
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key:
        secrets["GROQ_API_KEY"] = groq_key
        
    if os.path.exists("auth/medium_state.json"):
        with open("auth/medium_state.json", "r") as f:
            secrets["MEDIUM_STATE"] = f.read()
            
    for secret_name, secret_value in secrets.items():
        encrypted_value = encrypt(public_key, secret_value)
        
        data = {
            "encrypted_value": encrypted_value,
            "key_id": key_id
        }
        
        r = requests.put(
            f"https://api.github.com/repos/{REPO}/actions/secrets/{secret_name}",
            headers=HEADERS,
            json=data
        )
        
        if r.status_code in [201, 204]:
            print(f"Successfully set {secret_name}")
        else:
            print(f"Failed to set {secret_name}: {r.status_code} {r.text}")

if __name__ == "__main__":
    main()
