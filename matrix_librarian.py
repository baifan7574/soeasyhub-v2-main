import os
import time
import requests
import urllib3
from datetime import datetime, timezone
from supabase import create_client, Client
from typing import List

# Disable insecure request warnings for government sites with SSL issues
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================= Configuration =================
TOKEN_FILE = os.path.join(".agent", "Token..txt")  # Fallback for local development
STORAGE_BUCKET = "raw-handbooks"
BATCH_SIZE = 50

# Environment variable names for cloud deployment
ENV_SUPABASE_URL = "SUPABASE_URL"
ENV_SUPABASE_KEY = "SUPABASE_KEY"
ENV_TAVILY_KEY = "TAVILY_KEY"

class MatrixLibrarian:
    def __init__(self):
        self.config = self._load_config()
        self.supabase: Client = create_client(self.config['url'], self.config['key'])
        self.tavily_key = self.config.get('tavily_key')
        
    def _load_config(self):
        config = {}
        
        # Priority 1: Read from environment variables (cloud deployment)
        supabase_url = os.environ.get(ENV_SUPABASE_URL)
        supabase_key = os.environ.get(ENV_SUPABASE_KEY)
        tavily_key = os.environ.get(ENV_TAVILY_KEY)
        
        if supabase_url and supabase_key:
            config['url'] = supabase_url
            config['key'] = supabase_key
            if tavily_key:
                config['tavily_key'] = tavily_key
            print("✅ Config loaded from environment variables.")
            return config
        
        # Priority 2: Fallback to local Token file (development)
        token_path = None
        if os.path.exists(TOKEN_FILE):
            token_path = TOKEN_FILE
        else:
            # Try alternative relative path
            alt_path = os.path.join("..", ".agent", "Token..txt")
            if os.path.exists(alt_path):
                token_path = alt_path
        
        if not token_path:
            raise FileNotFoundError(
                f"Critical: {TOKEN_FILE} not found and environment variables {ENV_SUPABASE_URL}/{ENV_SUPABASE_KEY} not set."
            )
        
        with open(token_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                if "Project URL:" in line:
                    config['url'] = line.split("URL:")[1].strip()
                if "Secret keys:" in line:
                    config['key'] = line.split("keys:")[1].strip()
                if "tvly-" in line:
                    config['tavily_key'] = line.split()[0].strip()
        
        if 'url' not in config or 'key' not in config:
            raise ValueError("Configuration incomplete. Check Token..txt or environment variables.")
        
        print("⚠️  Config loaded from local Token file (development mode).")
        return config

    def fetch_pending_tasks(self) -> List[dict]:
        print(f"📋 Fetching batch of {BATCH_SIZE} tasks (Medical Priority)...")
        try:
            res = self.supabase.table("grich_keywords_pool")\
                .select("*")\
                .eq("category", "Medical")\
                .eq("is_downloaded", False)\
                .limit(BATCH_SIZE)\
                .execute()
            return res.data
        except Exception as e:
            print(f"❌ Fetch Error: {e}")
            return []

    def search_pdf(self, keyword):
        if not self.tavily_key: return None
        query = f"site:.gov filetype:pdf {keyword}"
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self.tavily_key,
            "query": query,
            "max_results": 1,
        }
        try:
            res = requests.post(url, json=payload, timeout=10)
            data = res.json()
            if 'results' in data and len(data['results']) > 0:
                return data['results'][0] 
            return None
        except:
            return None

    def download_and_upload(self, pdf_url, slug):
        try:
            print(f"   ⬇️ Downloading (Bypassing SSL): {pdf_url}")
            headers = {'User-Agent': 'Mozilla/5.0'}
            # verify=False is critical for CDPH and other gov sites
            with requests.get(pdf_url, headers=headers, stream=True, timeout=20, verify=False) as r:
                r.raise_for_status()
                if 'html' in r.headers.get('Content-Type', '').lower():
                     return None
                
                file_path = f"{slug}.pdf"
                self.supabase.storage.from_(STORAGE_BUCKET).upload(
                    file_path, r.content, 
                    file_options={"content-type": "application/pdf", "upsert": "true"}
                )
                print(f"   ☁️ Uploaded: {file_path}")
                return file_path
        except Exception as e:
            print(f"   ❌ Download Failed: {e}")
            return None

    def run_batch(self):
        tasks = self.fetch_pending_tasks()
        if not tasks:
            print("💤 No pending tasks.")
            return

        for task in tasks:
            print(f"\n🔍 Searching: {task['keyword']}")
            result = self.search_pdf(task['keyword'])
            if result:
                path = self.download_and_upload(result['url'], task['slug'])
                if path:
                    self.supabase.table("grich_keywords_pool").update({"is_downloaded": True, "state": "downloaded"}).eq("id", task['id']).execute()
                    print("   ✅ [DB Success]")
                else:
                    self.supabase.table("grich_keywords_pool").update({"state": "download_failed"}).eq("id", task['id']).execute()
            time.sleep(2)

if __name__ == "__main__":
    librarian = MatrixLibrarian()
    librarian.run_batch()
