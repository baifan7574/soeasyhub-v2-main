import os
import sys
import time
import codecs
import datetime
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- Configuration ---
# GSC API Config
# Assuming the script is run from soeasyhub-v2/ or similar context where .agent is in parent or sibling
# Adjust path logic to find .agent relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
GSC_KEY_FILE_PATH = os.path.join(PROJECT_ROOT, ".agent", "gen-lang-client-0846513202-3d6c54387cae.json")
GSC_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
GSC_PROPERTY_URI = "sc-domain:soeasyhub.com" # Taken from gsc_miner.py

def main():
    # Ensure UTF-8 output
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    
    print("=== Google Search Console Traffic Report ===")
    
    if not os.path.exists(GSC_KEY_FILE_PATH):
        print(f"❌ ERROR: GSC key file not found at '{GSC_KEY_FILE_PATH}'")
        return

    try:
        creds = service_account.Credentials.from_service_account_file(GSC_KEY_FILE_PATH, scopes=GSC_SCOPES)
        webmasters_service = build("webmasters", "v3", credentials=creds)
    except Exception as e:
        print(f"❌ ERROR: Could not create GSC service: {e}")
        return

    today = datetime.date.today()
    # Fetch last 30 days
    start_date = (today - datetime.timedelta(days=32)).strftime("%Y-%m-%d") # Go back a bit more to ensure data availability (GSC has lag)
    end_date = (today - datetime.timedelta(days=2)).strftime("%Y-%m-%d") # GSC usually has 2-3 days lag

    print(f"Fetching data for period: {start_date} to {end_date}")

    # 1. Total Traffic (Clicks, Impressions)
    request_totals = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["date"],
        "rowLimit": 25000
    }

    response_totals = None
    for i in range(3):
        try:
            response_totals = webmasters_service.searchanalytics().query(siteUrl=GSC_PROPERTY_URI, body=request_totals).execute()
            break
        except Exception as e:
            if "WinError 10060" in str(e) and i < 2:
                print(f"  - Connection timed out, retrying ({i+1}/3)...")
                time.sleep(5)
            else:
                print(f"❌ ERROR fetching total stats: {e}")
                # Don't break here completely, just stop retrying totals and try next steps if possible? 
                # Actually if totals fail, pages likely fail too. But let's keep it robust.
                break

    if response_totals and "rows" in response_totals:
        df_totals = pd.DataFrame(response_totals["rows"])
        total_clicks = df_totals["clicks"].sum()
        total_impressions = df_totals["impressions"].sum()
        avg_ctr = df_totals["ctr"].mean() * 100
        avg_position = df_totals["position"].mean()
        print(f"\n📊 Traffic Summary (Last ~30 Days):")
        print(f"  - Total Clicks: {total_clicks}")
        print(f"  - Total Impressions: {total_impressions}")
        print(f"  - Average CTR: {avg_ctr:.2f}%")
        print(f"  - Average Position: {avg_position:.1f}")
    else:
        print("\n⚠️ No traffic data found for this period (or API call failed).")

    # 2. Indexed/Active Pages (Pages with impressions)
    print("\nFetching active page counts...")
    request_pages = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["page"],
        "rowLimit": 25000 # Max limit
    }

    response_pages = None
    for i in range(3):
        try:
            response_pages = webmasters_service.searchanalytics().query(siteUrl=GSC_PROPERTY_URI, body=request_pages).execute()
            break
        except Exception as e:
            if "WinError 10060" in str(e) and i < 2:
                print(f"  - Connection timed out, retrying ({i+1}/3)...")
                time.sleep(5)
            else:
                print(f"❌ ERROR fetching page stats: {e}")
                break

    if response_pages and "rows" in response_pages:
        active_pages_count = len(response_pages["rows"])
        print(f"\n📄 Page Indexing Status (based on impressions):")
        print(f"  - Pages with impressions in last 30 days: {active_pages_count}")
        
        # Show top 5 pages by clicks
        df_pages = pd.DataFrame(response_pages["rows"])
        top_pages = df_pages.sort_values(by="clicks", ascending=False).head(5)
        print("\n🏆 Top 5 Pages by Clicks:")
        for index, row in top_pages.iterrows():
            print(f"  - {row['keys'][0]} (Clicks: {row['clicks']}, Impr: {row['impressions']})")
    else:
        print("\n⚠️ No active pages found (or API call failed).")

    # 3. Microsoft / Bing Check
    print("\n=== Microsoft / Bing Status ===")
    print("Checking for local configuration...")
    # Check for Bing API key in environment or files (if any)
    # Based on previous search, we only saw an IndexNow verification file.
    
    bing_file = os.path.join(PROJECT_ROOT, ".agent", "微软。822834cd8b83498a90e4fd5ef715fa14.txt")
    if os.path.exists(bing_file):
        with open(bing_file, 'r') as f:
            code = f.read().strip()
        print(f"✅ Bing verification file found: {os.path.basename(bing_file)}")
        print(f"   Verification Code: {code}")
        print("   (To see actual Bing traffic, please log in to Bing Webmaster Tools manually, as no API key was found for retrieval)")
    else:
         print("⚠️ No Bing verification file found in .agent/")

if __name__ == "__main__":
    main()
