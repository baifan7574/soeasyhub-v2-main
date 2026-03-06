import os
import sys

# Add parent directory to path so we can import matrix_config if run from root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from matrix_config import config
from supabase import create_client, Client

SUPABASE_URL = config.supabase_url
SUPABASE_KEY = config.supabase_key

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Missing Supabase credentials.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def run_migration():
    print("Adding columns file_type and content_raw to grich_keywords_pool...")
    
    # Supabase Data API doesn't support raw DDL directly from the Python client.
    # However, sometimes rpc is used to run sql, or we just ask the user to run it via SQL editor.
    # We can try using rpc if there is a helper function, but if not we can just use the requests library to send a direct postgrest query if it allows.
    
    # Actually, we can just use requests with PostgREST if it has rpc for this,
    # or just try to update a dummy record to see if it throws an error.
    # The safest way is to ask the user to run it if there's no DB url.
    # Let's check if we can run RPC.
    
    try:
        # Try a dummy update to create the column? No, that won't create it.
        # Often there's an RPC like 'exec_sql'. We can try calling it.
        response = supabase.rpc("exec_sql", {"sql": "ALTER TABLE grich_keywords_pool ADD COLUMN IF NOT EXISTS file_type TEXT DEFAULT 'pdf', ADD COLUMN IF NOT EXISTS content_raw TEXT;"}).execute()
        print(f"Migration via RPC success: {response}")
    except Exception as e:
        print(f"RPC migration failed: {e}")
        print("\n\nIMPORTANT: Please run the following SQL in your Supabase SQL Editor:")
        print("ALTER TABLE grich_keywords_pool ADD COLUMN IF NOT EXISTS file_type TEXT DEFAULT 'pdf', ADD COLUMN IF NOT EXISTS content_raw TEXT;")

if __name__ == "__main__":
    run_migration()
