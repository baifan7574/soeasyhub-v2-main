
import os
import sys
import time
import codecs
import datetime
import pandas as pd
from supabase import create_client, Client
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- Configuration ---
# GSC API Config
GSC_KEY_FILE_PATH = os.environ.get("GSC_KEY_FILE", ".agent/gen-lang-client-0846513202-3d6c54387cae.json")
GSC_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
GSC_PROPERTY_URI = "sc-domain:soeasyhub.com"
GSC_API_RETRIES = 3

# Supabase Config
TOKEN_FILE = os.path.join(".agent", "Token..txt")
DB_TABLE = "grich_keywords_pool"

# --- Helper Functions ---
def make_slug(text):
    """Creates a URL-friendly slug from a text string."""
    return text.lower().replace(" ", "-").replace("/", "-").replace("--", "-").replace("?", "").replace(":", "")

# --- Main Logic ---
def main():
    """
    Connects to GSC API, finds high-potential keywords, checks against Supabase DB,
    and inserts new, unique keywords directly into the database.
    """
    # 1. Fetch Keywords from Google Search Console
    print("STEP 1: Fetching keywords from Google Search Console...")
    
    if not os.path.exists(GSC_KEY_FILE_PATH):
        print(f"❌ ERROR: GSC key file not found at '{GSC_KEY_FILE_PATH}'")
        sys.exit(1)

    try:
        creds = service_account.Credentials.from_service_account_file(GSC_KEY_FILE_PATH, scopes=GSC_SCOPES)
        webmasters_service = build("webmasters", "v3", credentials=creds)
    except Exception as e:
        print(f"❌ ERROR: Could not create GSC service: {e}")
        sys.exit(1)
    
    today = datetime.date.today()
    start_date = (today - datetime.timedelta(days=90)).strftime("%Y-%m-%d")
    end_date = (today - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    
    request = {
        "startDate": start_date, "endDate": end_date, "dimensions": ["query"],
        "rowLimit": 25000, "dataState": "all"
    }

    response = None
    for i in range(GSC_API_RETRIES):
        try:
            print(f"  - Attempt {i + 1}/{GSC_API_RETRIES} to fetch data...")
            response = webmasters_service.searchanalytics().query(siteUrl=GSC_PROPERTY_URI, body=request).execute()
            break
        except Exception as e:
            if "WinError 10060" in str(e) and i < GSC_API_RETRIES - 1:
                time.sleep(5 * (i + 1))
            else:
                print(f"❌ ERROR: GSC API call failed: {e}")
                sys.exit(1)

    if not response or "rows" not in response:
        print("✅ INFO: No search data returned from GSC. Exiting.")
        return

    df = pd.DataFrame(response["rows"])
    potential_df = df[(df["impressions"] >= 20) & (df["clicks"] == 0) & (df["position"] > 5)].copy()
    
    if potential_df.empty:
        print("✅ INFO: No new high-potential keywords found in GSC this time. Exiting.")
        return
        
    print(f"  - Found {len(potential_df)} high-potential keywords from GSC.")

    # 2. Connect to Supabase and get existing slugs
    print("\nSTEP 2: Connecting to Supabase to check for duplicates...")
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        try:
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
                    for line in f.read().split('\n'):
                        if 'Project URL:' in line: supabase_url = line.split('Project URL:')[1].strip()
                        if 'Secret keys:' in line: supabase_key = line.split('Secret keys:')[1].strip()
        except Exception as e:
            print(f"⚠️ WARNING: Could not read local token file: {e}")

    if not supabase_url or not supabase_key:
        print("❌ ERROR: Supabase URL/Key not found.")
        sys.exit(1)

    try:
        supabase: Client = create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"❌ ERROR: Could not create Supabase client: {e}")
        sys.exit(1)

    existing_slugs = set()
    try:
        page, page_size = 0, 1000
        while True:
            res = supabase.table(DB_TABLE).select("slug").range(page * page_size, (page + 1) * page_size - 1).execute()
            if not res.data: break
            for row in res.data: existing_slugs.add(row['slug'])
            page += 1
        print(f"  - Found {len(existing_slugs)} existing slugs in the database.")
    except Exception as e:
        print(f"❌ ERROR: Failed to query existing slugs: {e}")
        sys.exit(1)

    # 3. Filter, prepare, and insert new keywords
    print("\nSTEP 3: Preparing and inserting new unique keywords...")
    data_to_insert = []
    for query in potential_df['query']:
        slug = make_slug(query)
        if slug not in existing_slugs:
            data_to_insert.append({
                "slug": slug, "is_downloaded": False, "is_refined": False, "color_tag": "Blue",
            })
            existing_slugs.add(slug) # Add to set to avoid duplicates within the same run

    if not data_to_insert:
        print("✅ INFO: All high-potential keywords from GSC are already in the database. Nothing to do.")
        return

    try:
        res = supabase.table(DB_TABLE).insert(data_to_insert).execute()
        inserted_count = len(res.data)
        print(f"🚀 SUCCESS: Injected {inserted_count} new keywords into the '{DB_TABLE}' table!")
    except Exception as e:
        print(f"❌ ERROR: Database insert failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure UTF-8 output
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    main()
