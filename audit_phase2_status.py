import os
import sys
from supabase import create_client

# Force UTF-8 output for Windows terminals
sys.stdout.reconfigure(encoding='utf-8')

def get_credentials():
    # Priority 1: Env Vars
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if url and key:
        return url, key
    
    # Priority 2: Token file (for local audit)
    token_path = os.path.join(".agent", "Token..txt")
    if not os.path.exists(token_path):
        token_path = os.path.join("..", ".agent", "Token..txt")
    
    if os.path.exists(token_path):
        config = {}
        with open(token_path, 'r', encoding='utf-8') as f:
            for line in f:
                if "Project URL:" in line:
                    config['url'] = line.split("URL:")[1].strip()
                if "Secret keys:" in line:
                    config['key'] = line.split("keys:")[1].strip()
        return config.get('url'), config.get('key')
    
    return None, None

def main():
    url, key = get_credentials()
    if not url or not key:
        print("❌ Could not load Supabase credentials.")
        return

    supabase = create_client(url, key)
    print(f"✅ Connected to Supabase: {url[:20]}...")

    # 1. Check Total Tasks
    res = supabase.table("grich_keywords_pool").select("id", count="exact").execute()
    total = res.count
    print(f"Total Tasks: {total}")

    # 2. Check Phase 2 Status (Downloaded)
    res = supabase.table("grich_keywords_pool").select("id", count="exact").eq("is_downloaded", True).execute()
    downloaded = res.count
    print(f"Downloaded (is_downloaded=True): {downloaded}")

    # 3. Check Failed Downloads
    res = supabase.table("grich_keywords_pool").select("id", count="exact").eq("state", "download_failed").execute()
    failed = res.count
    print(f"Download Failed (state='download_failed'): {failed}")

    # 4. Check PDF URL populated
    res = supabase.table("grich_keywords_pool").select("id", count="exact").not_.is_("pdf_url", "null").execute()
    pdf_url_count = res.count
    print(f"PDF URL Populated: {pdf_url_count}")

    # 5. Sample Check
    print("\n🔍 Sample of downloaded tasks:")
    res = supabase.table("grich_keywords_pool").select("slug, pdf_url, state").eq("is_downloaded", True).limit(5).execute()
    for item in res.data:
        print(f"- {item['slug']}: {item['pdf_url']} ({item['state']})")

if __name__ == "__main__":
    main()
