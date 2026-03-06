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
# Priority: Env Var > Default
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", 200))

# Environment variable names for cloud deployment
ENV_SUPABASE_URL = "SUPABASE_URL"
ENV_SUPABASE_KEY = "SUPABASE_KEY"
ENV_TAVILY_KEY = "TAVILY_KEY"

class MatrixLibrarian:
    def __init__(self):
        self.config = self._load_config()
        self.supabase: Client = create_client(self.config['url'], self.config['key'])
        # tavily_keys are managed in _load_config and get_tavily_key
        
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
                config['tavily_keys'] = [k.strip() for k in tavily_key.split(',') if k.strip()]
            else:
                raise ValueError(f"Critical: Environment variable {ENV_TAVILY_KEY} is missing.")
            
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
                    if 'tavily_keys' not in config:
                        config['tavily_keys'] = []
                    # Could be multiple keys if space-separated, but let's grab the token
                    for part in line.split():
                        if part.startswith("tvly-"):
                            config['tavily_keys'].append(part.strip())
        
        if 'url' not in config or 'key' not in config:
            raise ValueError("Configuration incomplete. Check Token..txt or environment variables.")

        if 'tavily_keys' not in config:
             raise ValueError("Critical: TAVILY_KEY is missing. Search cannot proceed.")
        
        self.tavily_keys = config['tavily_keys']
        self.current_tavily_idx = 0
        
        print("⚠️  Config loaded from local Token file (development mode).")
        return config

    def get_tavily_key(self):
        return self.tavily_keys[self.current_tavily_idx % len(self.tavily_keys)]

    def next_tavily_key(self):
        self.current_tavily_idx += 1
        print(f"   🔄 Switched to Tavily Key {self.current_tavily_idx % len(self.tavily_keys) + 1}")

    def fetch_pending_tasks(self) -> List[dict]:
        print(f"📋 Fetching batch of {BATCH_SIZE} tasks (Simple & Brutal)...")
        try:
            # Simple & Brutal: 强制全量拉取 is_downloaded = false 的记录
            # User Instruction: SELECT * FROM grich_keywords_pool WHERE is_downloaded = false LIMIT 200
            res = self.supabase.table("grich_keywords_pool")\
                .select("*")\
                .eq("is_downloaded", False)\
                .limit(BATCH_SIZE)\
                .execute()
            
            data = res.data
            print(f"   ℹ️ Found {len(data)} pending tasks.")
            return data
        except Exception as e:
            print(f"❌ Fetch Error: {e}")
            return []

    def search_document(self, keyword):
        # 1. First Tap: Search for PDF
        query_pdf = f"site:.gov filetype:pdf {keyword} report handbook"
        url = "https://api.tavily.com/search"
        payload_pdf = {
            "api_key": self.get_tavily_key(),
            "query": query_pdf,
            "max_results": 1,
            "search_depth": "advanced"
        }
        
        try:
            res = requests.post(url, json=payload_pdf, timeout=15)
            if res.status_code == 429 or res.status_code == 401 or res.status_code == 403:
                self.next_tavily_key()
                payload_pdf["api_key"] = self.get_tavily_key()
                res = requests.post(url, json=payload_pdf, timeout=15)
                
            data = res.json()
            if 'results' in data and len(data['results']) > 0:
                result = data['results'][0]
                result['file_type'] = 'pdf'
                return result
        except Exception as e:
            print(f"   ⚠️ PDF Search Error: {e}")
            
        # 2. Second Tap: Search for HTML if PDF not found
        print(f"   🔄 PDF not found, performing Second Tap (HTML)...")
        query_html = f"site:.gov {keyword} requirements"
        payload_html = {
            "api_key": self.get_tavily_key(),
            "query": query_html,
            "max_results": 1,
            "search_depth": "advanced"
        }
        
        try:
            res = requests.post(url, json=payload_html, timeout=15)
            if res.status_code == 429 or res.status_code == 401 or res.status_code == 403:
                self.next_tavily_key()
                payload_html["api_key"] = self.get_tavily_key()
                res = requests.post(url, json=payload_html, timeout=15)
                
            data = res.json()
            if 'results' in data and len(data['results']) > 0:
                result = data['results'][0]
                # Default to html if not explicitly ending in pdf
                result['file_type'] = 'pdf' if result['url'].lower().endswith('.pdf') else 'html'
                return result
        except Exception as e:
            print(f"   ⚠️ HTML Search Error: {e}")
            
        return None

    def download_and_upload(self, doc_url, slug, file_type):
        try:
            print(f"   ⬇️ Downloading (Bypassing SSL): {doc_url}")
            headers = {'User-Agent': 'Mozilla/5.0'}
            # verify=False is critical for CDPH and other gov sites
            with requests.get(doc_url, headers=headers, stream=True, timeout=30, verify=False) as r:
                r.raise_for_status()
                content_type = r.headers.get('Content-Type', '').lower()
                
                # Check actual content type
                actual_file_type = 'pdf' if 'pdf' in content_type else 'html'
                
                if actual_file_type == 'html':
                    # Instead of uploading to bucket, just return HTML text
                    # We will save this directly to the database
                    html_content = r.text
                    print(f"   ☁️ Downloaded HTML content ({len(html_content)} bytes)")
                    return "HTML_CONTENT", actual_file_type, html_content
                else:
                    file_path = f"{slug}.pdf"
                    self.supabase.storage.from_(STORAGE_BUCKET).upload(
                        file_path, r.content, 
                        file_options={"content-type": "application/pdf", "upsert": "true"}
                    )
                    
                    # Strict check to verify file exists in bucket before marking DB
                    try:
                        # We use the public URL and verify it returns 200 OK
                        public_url = self.supabase.storage.from_(STORAGE_BUCKET).get_public_url(file_path)
                        verify_req = requests.head(public_url, timeout=10)
                        if verify_req.status_code >= 400:
                            print(f"   ❌ Upload Verification Failed: 404 Not Found at {public_url}")
                            return None, None, None
                    except Exception as ve:
                        print(f"   ❌ Upload Verification Exception: {ve}")
                        return None, None, None
                        
                    print(f"   ☁️ Uploaded and Verified: {file_path}")
                    return file_path, actual_file_type, None
        except Exception as e:
            print(f"   ❌ Download Failed: {e}")
            return None, None, None

    def run_batch(self):
        tasks = self.fetch_pending_tasks()
        if not tasks:
            print("💤 No pending tasks found in DB. Check if 'grich_keywords_pool' has entries with is_downloaded=false.")
            return

        for task in tasks:
            print(f"\n======== Processing Task {task.get('id')} ========")
            print(f"🔍 Searching: {task['keyword']}")
            
            # 1. Search for document (Double Tap)
            result = self.search_document(task['keyword'])
            
            if result:
                doc_url = result['url']
                doc_type = result.get('file_type', 'pdf')
                print(f"   🎯 Found {doc_type.upper()} URL: {doc_url}")
                
                # 2. Download & Process
                path, actual_type, html_content = self.download_and_upload(doc_url, task['slug'], doc_type)
                
                if path:
                    # Success
                    update_data = {
                        "is_downloaded": True, 
                        "state": "downloaded",
                        "pdf_url": doc_url,  # Optional: Store source URL if schema allows
                        "file_type": actual_type
                    }
                    if actual_type == 'html' and html_content:
                        update_data["content_raw"] = html_content
                        
                    self.supabase.table("grich_keywords_pool").update(update_data).eq("id", task['id']).execute()
                    print(f"   ✅ [DB Success] Marked as downloaded ({actual_type}).")
                else:
                    # Download failed but search succeeded
                    self.supabase.table("grich_keywords_pool").update({
                        "state": "download_failed"
                    }).eq("id", task['id']).execute()
                    print("   ⚠️ [DB Update] Marked as download_failed.")
            else:
                print("   🚫 No document found via Tavily.")
            
            time.sleep(1) # Rate limit protection

if __name__ == "__main__":
    librarian = MatrixLibrarian()
    librarian.run_batch()
