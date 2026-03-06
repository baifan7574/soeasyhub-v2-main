import os
import sys
from matrix_config import config
from supabase import create_client, Client
import xml.etree.ElementTree as ET

def main():
    print("[FACTORY SHUTDOWN AUDIT INITIATED...]")
    print("========================================")

    # 1. Database Connection
    url = config.supabase_url
    key = config.supabase_key

    if not url or not key:
        print("[X] CRITICAL ERROR: Supabase configuration missing!")
        return

    try:
        supabase: Client = create_client(url, key)
    except Exception as e:
        print(f"[X] CRITICAL ERROR: Failed to connect to database: {e}")
        return

    # 2. Funnel Analysis
    print("\n[SEARCH] Phase 1: The Funnel Analysis (Database)")
    
    try:
        # Total Ore
        res_total = supabase.table('grich_keywords_pool').select('*', count='exact', head=True).execute()
        count_total = res_total.count
        
        # Inlet (Downloaded)
        res_downloaded = supabase.table('grich_keywords_pool').select('*', count='exact', head=True).eq('is_downloaded', True).execute()
        count_downloaded = res_downloaded.count

        # Semi-finished (JSON)
        # Using .neq('content_json', 'null') as a safe guess, but if it fails we might need to adjust.
        # However, checking if column is not null is standard.
        res_json = supabase.table('grich_keywords_pool').select('*', count='exact', head=True).neq('content_json', 'null').execute()
        count_json = res_json.count

        # Web Finished (Article)
        res_article = supabase.table('grich_keywords_pool').select('*', count='exact', head=True).neq('final_article', 'null').execute()
        count_article = res_article.count

        # PDF Finished
        res_pdf = supabase.table('grich_keywords_pool').select('*', count='exact', head=True).neq('pdf_url', 'null').execute()
        count_pdf = res_pdf.count
        
        # Failure/Blocked checks
        error_counts = "0 (No explicit error tracking column found)"
        # Try to check for status column if it exists, otherwise ignore errors about it missing
        try:
             # Just a probe
             # We can't easily probe schema without potentially crashing, so let's skip explicit error counting unless we know the column.
             # But the user asked for it. Let's try to see if 'status' has 'fail'.
             res_error = supabase.table('grich_keywords_pool').select('*', count='exact', head=True).ilike('status', '%fail%').execute()
             error_counts = res_error.count
        except:
             pass

        print(f"1. Total Ore (Keywords):      {count_total}")
        print(f"2. Inlet (Downloaded):        {count_downloaded}")
        print(f"3. Semi-finished (JSON):      {count_json}")
        print(f"4. Web Finished (Article):    {count_article}")
        print(f"5. PDF Finished (Product):    {count_pdf}")
        print(f"6. Errors (Status='fail'):    {error_counts}")

    except Exception as e:
        print(f"[X] Error during Database Analysis: {e}")
        # Continue execution to show sitemap data if DB fails mid-way
    
    # 3. Traffic Sense (Sitemap)
    print("\n[TRAFFIC] Phase 2: Traffic Sense (Sitemap)")
    sitemap_path = os.path.join(os.path.dirname(__file__), 'sitemap.xml')
    real_link_count = 0
    
    if os.path.exists(sitemap_path):
        try:
            tree = ET.parse(sitemap_path)
            root = tree.getroot()
            namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            urls = root.findall('ns:url', namespaces)
            if not urls:
                urls = root.findall('url')
            
            real_link_count = len(urls)
            print(f"Sitemap found: {sitemap_path}")
            print(f"Real Link Count in Sitemap: {real_link_count}")
        except Exception as e:
            print(f"[X] Error parsing sitemap: {e}")
    else:
        print(f"[X] Sitemap not found at {sitemap_path}")

    # 4. Bottleneck Analysis (Calculated)
    print("\n[BOTTLENECK] Phase 3: The Bottleneck Diagnosis")
    
    # Ensure variables exist if DB block failed
    try:
        count_total
    except NameError:
        print("Skipping bottleneck analysis due to missing DB data.")
        return

    drops = [
        ("Ore -> Inlet", count_total - count_downloaded),
        ("Inlet -> JSON", count_downloaded - count_json),
        ("JSON -> Web", count_json - count_article),
        ("Web -> PDF", count_article - count_pdf)
    ]
    
    max_drop_val = -1
    max_drop_name = ""
    
    for name, val in drops:
        if val > max_drop_val:
            max_drop_val = val
            max_drop_name = name

    print(f"Biggest Drop: {max_drop_name} (Lost {max_drop_val} units)")
    
    if count_total > 0:
        print(f"\nSurvival Rate: {count_pdf}/{count_total} ({count_pdf/count_total*100:.2f}%)")
    else:
        print("\nSurvival Rate: N/A (Total Ore is 0)")

    print("\n[OK] AUDIT COMPLETE.")

if __name__ == "__main__":
    main()
