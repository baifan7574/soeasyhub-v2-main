import os
import sys
import codecs
import requests

# --- Configuration ---
# Hardcoding credentials from .agent/Token..txt for reliability in this script
SUPABASE_URL = "https://nbfzhxgkfljeuoncujum.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5iZnpoeGdrZmxqZXVvbmN1anVtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDU0Mjg3MSwiZXhwIjoyMDgwMTE4ODcxfQ.44pmI9dqwsL-5lcRd0izq5RoKfVH8wr0KmSVLzBrfp8"

HEADERS = {
    "apikey": SUPABASE_KEY, 
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

DB_TABLE = "grich_keywords_pool"

def main():
    # Ensure UTF-8 output
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

    print("=== Internal Content / Indexing Status (Supabase) ===")
    print(f"Checking database: {DB_TABLE}")

    try:
        # Create a copy of headers for counting
        count_headers = HEADERS.copy()
        count_headers["Prefer"] = "count=exact"
        
        # 1. Total Keywords (Potential pages)
        # We use HEAD request or GET with limit 1
        r = requests.get(f"{SUPABASE_URL}/rest/v1/{DB_TABLE}", headers=count_headers, params={"select": "id", "limit": "1"})
        if r.status_code in [200, 206]:
            content_range = r.headers.get("Content-Range", "")
            total_records = content_range.split("/")[-1] if "/" in content_range else "Unknown"
        else:
            total_records = f"Error {r.status_code}: {r.text}"

        # 2. Refined Content (Ready for composing)
        r = requests.get(f"{SUPABASE_URL}/rest/v1/{DB_TABLE}", headers=count_headers, params={"select": "id", "is_refined": "eq.true", "limit": "1"})
        refined_count = r.headers.get("Content-Range", "").split("/")[-1] if r.status_code in [200, 206] else "Unknown"

        # 3. Composed/Published (Has article content) - Proxy for "Pages on Site"
        r = requests.get(f"{SUPABASE_URL}/rest/v1/{DB_TABLE}", headers=count_headers, params={"select": "id", "final_article": "not.is.null", "limit": "1"})
        published_count = r.headers.get("Content-Range", "").split("/")[-1] if r.status_code in [200, 206] else "Unknown"

        # 4. Has PDF URL (Files generated)
        r = requests.get(f"{SUPABASE_URL}/rest/v1/{DB_TABLE}", headers=count_headers, params={"select": "id", "pdf_url": "not.is.null", "limit": "1"})
        pdf_count = r.headers.get("Content-Range", "").split("/")[-1] if r.status_code in [200, 206] else "Unknown"

        print(f"\n📊 Database Stats (Content Pipeline):")
        print(f"  - Total Keywords/Topics Discovered: {total_records}")
        print(f"  - Refined Topics (Ready to Write):  {refined_count}")
        print(f"  - Articles Generated (Likely Published): {published_count}")
        print(f"  - PDFs Generated: {pdf_count}")

        print("\nNote: This reflects the *internal* state of your content generation system.")
        print("      'Articles Generated' is the closest proxy to 'pages on your site' from our side.")
        
    except Exception as e:
        print(f"❌ ERROR querying Supabase: {e}")

if __name__ == "__main__":
    main()
