import os
import time
import requests
import urllib3
from supabase import create_client, Client

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
STORAGE_BUCKET = "raw-handbooks"

class MatrixLibrarian:
    def __init__(self):
        url = os.environ.get('SUPABASE_URL')
        key = os.environ.get('SUPABASE_KEY')
        self.tavily_key = os.environ.get('TAVILY_API_KEY')
        if not url or not key:
            raise ValueError("Missing SUPABASE environment variables.")
        self.supabase: Client = create_client(url, key)

    def fetch_pending_tasks(self, limit=10):
        try:
            res = self.supabase.table("grich_keywords_pool")\
                .select("*")\
                .eq("is_downloaded", False)\
                .limit(limit)\
                .execute()
            return res.data
        except: return []

    def run(self):
        tasks = self.fetch_pending_tasks()
        if not tasks: 
            print("💤 No pending tasks.")
            return
        for task in tasks:
            print(f"🔍 Processing: {task['keyword']}")
            # Simplified for now as the user focused on Script 4 behavior
            time.sleep(1)

if __name__ == "__main__":
    MatrixLibrarian().run()
