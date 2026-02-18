import requests
import os

ZONE_ID = os.environ.get("CLOUDFLARE_ZONE_ID", "8a616a9b04d8160cba0765f98318a4cc")
EMAIL = os.environ.get("CLOUDFLARE_EMAIL", "baifan7574@gmail.com")
API_KEY = os.environ.get("CLOUDFLARE_API_KEY", "MISSING_KEY_PLEASE_SET_ENV")

url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/purge_cache"
headers = {
    "X-Auth-Email": EMAIL,
    "X-Auth-Key": API_KEY,
    "Content-Type": "application/json"
}
data = {"purge_everything": True}

print(f"Purging cache for Zone ID: {ZONE_ID}...")
try:
    response = requests.post(url, headers=headers, json=data, timeout=15)
    if response.status_code == 200:
        res_json = response.json()
        if res_json.get("success"):
            print("✅ Cache purged successfully!")
        else:
            print(f"❌ Failed to purge cache: {res_json}")
    else:
        print(f"❌ HTTP Error {response.status_code}: {response.text}")
except Exception as e:
    print(f"❌ Exception: {e}")
