import os
from supabase import create_client

def get_sb():
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables.")
    return create_client(url, key)

def run_audit():
    try:
        sb = get_sb()
        # Audit the production line
        downloaded = sb.table('grich_keywords_pool').select('id', count='exact').eq('is_downloaded', True).execute().count
        refined = sb.table('grich_keywords_pool').select('id', count='exact').eq('is_refined', True).execute().count
        composed = sb.table('grich_keywords_pool').select('id', count='exact').not_.is_('final_article', 'null').execute().count
        
        print("--- PRODUCTION LINE AUDIT ---")
        print(f"1. PDF Downloaded (Script 2): {downloaded}")
        print(f"2. Data Refined (Script 3): {refined}")
        print(f"3. Articles Composed (Script 4): {composed}")
    except Exception as e:
        print(f"❌ Audit Failed: {e}")
        exit(1)

if __name__ == "__main__":
    run_audit()
