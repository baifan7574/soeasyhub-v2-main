import os
import time
import requests
import urllib3
from datetime import datetime, timezone
from supabase import create_client, Client

# Disable SSL warnings for gov sites
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================= Matrix Librarian (Script 2) =================
STORAGE_BUCKET = "raw-handbooks"

class MatrixLibrarian:
    def __init__(self):
        self.config = self._load_config()
        self.supabase: Client = create_client(self.config['url'], self.config['key'])
        self.tavily_key = self.config.get('tavily_key')

    def _load_config(self):
        config = {
            'url': os.getenv('SUPABASE_URL'),
            'key': os.getenv('SUPABASE_KEY'),
            'tavily_key': os.getenv('TAVILY_API_KEY')
        }
        if config['url'] and config['key']: return config

        token_paths = ['.agent/Token..txt', '../.agent/Token..txt', '../../.agent/Token..txt']
        for tp in token_paths:
            if os.path.exists(tp):
                with open(tp, 'r', encoding='utf-8') as f:
                    for line in f:
                        if "Project URL:" in line: config['url'] = line.split("URL:")[1].strip()
                        if "Secret keys:" in line: config['key'] = line.split("keys:")[1].strip()
                        if "tvly-" in line: config['tavily_key'] = line.split()[0].strip()
                return config
        return config

    def fetch_pending_tasks(self, limit=10):
        try:
            res = self.supabase.table("grich_keywords_pool")\
                .select("*")\
                .eq("is_downloaded", False)\
                .limit(limit)\
                .execute()
            return res.data
        except: return []

    def download_and_upload(self, pdf_url, slug):
        try:
            print(f"   ⬇️ Downloading: {pdf_url}")
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(pdf_url, headers=headers, timeout=20, verify=False)
            if r.status_code == 200 and 'pdf' in r.headers.get('Content-Type', '').lower():
                file_path = f"{slug}.pdf"
                self.supabase.storage.from_(STORAGE_BUCKET).upload(
                    file_path, r.content, 
                    file_options={"content-type": "application/pdf", "upsert": "true"}
                )
                return file_path
        except: return None

    def run(self):
        tasks = self.fetch_pending_tasks()
        if not tasks: return print("💤 No tasks.")
        for task in tasks:
            # Simple simulation of search if Tavily is missing or just use task keyword for demo
            # In real production, Tavily is needed.
            print(f"🔍 Processing: {task['keyword']}")
            # ... Search logic would go here ...
            time.sleep(1)

if __name__ == "__main__":
    MatrixLibrarian().run()
