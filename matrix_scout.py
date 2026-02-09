import os
import time
import random
import json
import requests
from datetime import datetime, timezone
from supabase import create_client, Client

class GrichMiner:
    def __init__(self):
        url = os.environ.get('SUPABASE_URL')
        key = os.environ.get('SUPABASE_KEY')
        if not url or not key:
            raise ValueError("Missing SUPABASE environment variables.")
        self.supabase: Client = create_client(url, key)
        self.ua_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        ]

    def save_keyword(self, keyword):
        slug = keyword.lower().strip().replace(' ', '-')
        data = {
            "keyword": keyword,
            "slug": slug,
            "category": "AutoMined",
            "is_downloaded": False,
            "is_refined": False,
            "last_mined_at": datetime.now(timezone.utc).isoformat()
        }
        try:
            self.supabase.table("grich_keywords_pool").upsert(data, on_conflict="slug").execute()
            print(f"   ✅ Saved: {keyword}")
        except Exception as e:
            print(f"   ❌ Save Error: {e}")

    def mine(self, seed):
        print(f"🚀 Mining: {seed}")
        url = f"https://www.google.com/complete/search?client=chrome&q={seed}"
        headers = {"User-Agent": random.choice(self.ua_list)}
        try:
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                suggestions = json.loads(res.text)[1]
                for kw in suggestions:
                    self.save_keyword(kw)
        except Exception as e:
            print(f"   ❌ Request Error: {e}")

if __name__ == "__main__":
    miner = GrichMiner()
    miner.mine("nursing license reciprocity")