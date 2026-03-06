import os
import sys
from matrix_config import config
from supabase import create_client, Client
import xml.etree.ElementTree as ET

def main():
    print("[SITEMAP RECONCILIATION STARTED]")
    
    # 1. Database Connection
    url = config.supabase_url
    key = config.supabase_key
    
    if not url or not key:
        print("[X] CRITICAL ERROR: Supabase configuration missing!")
        return

    try:
        supabase: Client = create_client(url, key)
    except Exception as e:
        print(f"[X] Database Connection Failed: {e}")
        return

    # 2. Fetch DB Slugs
    print("Fetching finished articles from DB...")
    try:
        # Assuming 'final_article' not null means it's a finished web product
        res = supabase.table('grich_keywords_pool').select('id, slug').neq('final_article', 'null').execute()
        db_slugs = {item['slug']: item['id'] for item in res.data}
        print(f"DB Finished Count: {len(db_slugs)}")
    except Exception as e:
        print(f"[X] Failed to fetch from DB: {e}")
        return

    # 3. Parse Sitemap
    sitemap_path = os.path.join(os.path.dirname(__file__), 'sitemap.xml')
    sitemap_slugs = set()
    
    if os.path.exists(sitemap_path):
        try:
            tree = ET.parse(sitemap_path)
            root = tree.getroot()
            namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            urls = root.findall('ns:url', namespaces)
            if not urls:
                urls = root.findall('url')
            
            for url_elem in urls:
                loc = url_elem.find('ns:loc', namespaces)
                if loc is None:
                    loc = url_elem.find('loc')
                
                if loc is not None:
                    url_text = loc.text
                    # Extract slug from URL (assuming format https://domain.com/slug or similar)
                    # Adjust based on actual URL structure in sitemap
                    parts = url_text.strip('/').split('/')
                    slug = parts[-1]
                    sitemap_slugs.add(slug)
            
            print(f"Sitemap URL Count: {len(sitemap_slugs)}")
        except Exception as e:
            print(f"[X] Error parsing sitemap: {e}")
            return
    else:
        print(f"[X] Sitemap not found at {sitemap_path}")
        return

    # 4. Compare
    missing_slugs = []
    for slug, id in db_slugs.items():
        if slug not in sitemap_slugs:
            # Check for potential variations (e.g. sitemap might have .html extension or different casing)
            # Assuming exact match for now based on matrix_scout logic
            missing_slugs.append((id, slug))
    
    print(f"\n[MISSING FROM SITEMAP] Count: {len(missing_slugs)}")
    if missing_slugs:
        print(f"{'ID':<10} | {'SLUG'}")
        print("-" * 50)
        for id, slug in missing_slugs:
            print(f"{id:<10} | {slug}")
    else:
        print("✅ No discrepancies found! Sitemap is in sync.")

if __name__ == "__main__":
    main()
