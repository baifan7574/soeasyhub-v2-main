import os
import time
import random
import re
import json
import requests
import csv
from datetime import datetime, timezone
from supabase import create_client, Client

# ================= Grich Miner (Script 1) =================

class GrichMiner:
    def __init__(self):
        self.config = self._load_config()
        self.supabase: Client = create_client(self.config['url'], self.config['key'])
        self.ua_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        ]

    def _load_config(self):
        config = {
            'url': os.getenv('SUPABASE_URL'),
            'key': os.getenv('SUPABASE_KEY')
        }
        if config['url'] and config['key']: return config

        token_paths = ['.agent/Token..txt', '../.agent/Token..txt', '../../.agent/Token..txt']
        for tp in token_paths:
            if os.path.exists(tp):
                with open(tp, 'r', encoding='utf-8') as f:
                    for line in f:
                        if "Project URL:" in line: config['url'] = line.split("URL:")[1].strip()
                        if "Secret keys:" in line: config['key'] = line.split("keys:")[1].strip()
                return config
        return config

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
        except: pass

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
        except: pass

if __name__ == "__main__":
    miner = GrichMiner()
    miner.mine("nursing license reciprocity")