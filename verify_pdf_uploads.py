import os
import sys
from supabase import create_client

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

def get_credentials():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if url and key:
        return url, key
    
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
        print("❌ Credentials not found")
        return

    supabase = create_client(url, key)
    BUCKET = "raw-handbooks"

    print(f"🔍 Verifying uploads in bucket '{BUCKET}'...")

    # 1. Get list of files in bucket (with pagination/limit)
    try:
        # Default limit is 100, increase to 1000
        files = supabase.storage.from_(BUCKET).list(path=None, options={"limit": 1000, "offset": 0})
        file_names = [f['name'] for f in files]
        print(f"✅ Found {len(file_names)} files in storage.")
    except Exception as e:
        print(f"❌ Failed to list storage files: {e}")
        return

    # 2. Get downloaded tasks from DB
    res = supabase.table("grich_keywords_pool").select("slug").eq("is_downloaded", True).execute()
    db_slugs = {item['slug'] for item in res.data}
    print(f"✅ Found {len(db_slugs)} marked as downloaded in DB.")

    # 3. Cross-reference
    missing_in_storage = []
    for slug in db_slugs:
        expected_file = f"{slug}.pdf"
        if expected_file not in file_names:
            missing_in_storage.append(slug)

    extra_in_storage = []
    for fname in file_names:
        if not fname.endswith(".pdf"): continue
        slug = fname[:-4]
        if slug not in db_slugs:
            extra_in_storage.append(fname)

    # 4. Report
    print("\n📊 Discrepancy Report:")
    if missing_in_storage:
        print(f"⚠️  {len(missing_in_storage)} files missing in storage (DB says downloaded):")
        for s in missing_in_storage[:5]:
            print(f"   - {s}.pdf")
        if len(missing_in_storage) > 5: print("   ... and more")
    else:
        print("✅ All DB downloaded records have corresponding files in storage.")

    if extra_in_storage:
        print(f"⚠️  {len(extra_in_storage)} files in storage but not marked in DB:")
        for f in extra_in_storage[:5]:
            print(f"   - {f}")
    else:
        print("✅ No orphaned files in storage.")

if __name__ == "__main__":
    main()
