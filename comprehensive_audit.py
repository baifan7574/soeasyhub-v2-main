import os
import requests
import json
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("Audit")

# Force UTF-8 for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def get_supabase_config():
    """Retrieve Supabase config from env or file."""
    sb_url = os.environ.get("SUPABASE_URL")
    sb_key = os.environ.get("SUPABASE_KEY")
    
    if not sb_url or not sb_key:
        token_paths = [
            os.path.join(".agent", "Token..txt"),
            os.path.join("..", ".agent", "Token..txt"),
            os.path.join("soeasyhub-v2", ".agent", "Token..txt")
        ]
        for path in token_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        for line in f:
                            if "Project URL:" in line: sb_url = line.split("URL:")[1].strip()
                            if "Secret keys:" in line: sb_key = line.split("keys:")[1].strip()
                    break
                except Exception:
                    pass
    
    return sb_url, sb_key

def run_audit():
    print("\n" + "="*50)
    print("       ASSET INVENTORY AUDIT REPORT")
    print("="*50 + "\n")

    sb_url, sb_key = get_supabase_config()
    
    if not sb_url or not sb_key:
        print("❌ CRITICAL: Supabase credentials not found.")
        return

    headers = {
        "apikey": sb_key, 
        "Authorization": f"Bearer {sb_key}",
        "Content-Type": "application/json"
    }

    # --- 1. Database Inventory ---
    print("📦 [Database Inventory]")
    try:
        # Helper for counting
        def get_count(query_params={}):
            p = query_params.copy()
            p['select'] = 'count'
            # PostgREST 9+ uses count=exact in Prefer header usually, but select=count works in some versions returning [{count: N}]
            # Safer way compatible with check_stats_v2 approach (fetching IDs) if count is small, 
            # OR using HEAD + Prefer: count=exact
            
            # Method 1: HEAD with Prefer: count=exact
            h = headers.copy()
            h['Prefer'] = 'count=exact'
            r = requests.get(f"{sb_url}/rest/v1/grich_keywords_pool", params=p, headers=h)
            if r.status_code >= 400:
                # Fallback to len() if exact count fails or not supported easily
                p['select'] = 'id'
                del h['Prefer']
                r = requests.get(f"{sb_url}/rest/v1/grich_keywords_pool", params=p, headers=h)
                return len(r.json())
            
            # Content-Range: 0-24/25
            cr = r.headers.get("Content-Range")
            if cr:
                return cr.split('/')[-1]
            return "Unknown"

        # Total
        # Use simple len() approach from check_stats_v2 for reliability given environment
        print("  (Fetching counts, please wait...)")
        
        r = requests.get(f"{sb_url}/rest/v1/grich_keywords_pool?select=id", headers=headers)
        total = len(r.json()) if r.status_code == 200 else "Error"
        print(f"  • Total Keywords: {total}")

        # Refined
        r = requests.get(f"{sb_url}/rest/v1/grich_keywords_pool?select=id&is_refined=eq.true", headers=headers)
        refined = len(r.json()) if r.status_code == 200 else "Error"
        print(f"  • Refined Data:   {refined}")

        # Generated (Articles)
        r = requests.get(f"{sb_url}/rest/v1/grich_keywords_pool?select=id&final_article=not.is.null", headers=headers)
        articles = len(r.json()) if r.status_code == 200 else "Error"
        print(f"  • Generated Articles: {articles}")

        # PDFs
        r = requests.get(f"{sb_url}/rest/v1/grich_keywords_pool?select=id&pdf_url=not.is.null", headers=headers)
        pdfs = len(r.json()) if r.status_code == 200 else "Error"
        print(f"  • Generated PDFs:     {pdfs}")

    except Exception as e:
        print(f"  ❌ Error fetching DB stats: {e}")

    # --- 2. SEO Push Status ---
    print("\n🚀 [SEO Push Status]")
    # Note: Currently we don't track 'pushed' state in DB. We can only infer potential.
    # Future improvement: Add 'last_pushed_at' column to DB.
    print(f"  • Ready to Push: {articles} (Articles generated)")
    print("  • (Note: Push status is currently stateless. Recommended: Add tracking column to DB)")

    # --- 3. Indexing Status (Mock/Placeholder) ---
    print("\nmagni [Indexing Status]")
    # Real GSC check requires complex API auth flow.
    # We can check if we have GSC credentials available.
    gsc_key_path = os.environ.get("GSC_KEY_FILE", ".agent/gen-lang-client-0846513202-3d6c54387cae.json")
    if os.path.exists(gsc_key_path):
        print("  • GSC Credentials: Found ✅")
        print("  • Action: Run 'soeasyhub-v2/gsc_miner.py' for detailed keyword performance.")
    else:
        print("  • GSC Credentials: Not Found ❌ (Cannot verify indexing)")

    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    run_audit()
