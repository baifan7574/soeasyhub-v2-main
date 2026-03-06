import os
import requests
import sys

SB = os.environ.get("SUPABASE_URL", "https://nbfzhxgkfljeuoncujum.supabase.co")
KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5iZnpoeGdrZmxqZXVvbmN1anVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDAyNTk2NjQsImV4cCI6MjA1NTgzNTY2NH0.pq7kCx1-vcC6SHd4qm_kTVH8jU9DZ9p6vJfJXq5n5pU")
headers = {
    'apikey': KEY,
    'Authorization': f'Bearer {KEY}',
    'Content-Type': 'application/json'
}

print(f"Testing connection to {SB}")
print(f"Using key: {KEY[:10]}...")

try:
    r = requests.get(f"{SB}/rest/v1/grich_keywords_pool?select=count", headers=headers, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Exception: {e}")

# Fetch specific slug
slug = "does-california-have-reciprocity-for-teachers"
try:
    r2 = requests.get(f"{SB}/rest/v1/grich_keywords_pool?slug=eq.{slug}", headers=headers, timeout=10)
    print(f"\nFetch slug {slug}:")
    print(f"Status: {r2.status_code}")
    data = r2.json()
    print(f"Data type: {type(data)}")
    if isinstance(data, list):
        print(f"Length: {len(data)}")
        if data:
            rec = data[0]
            print(f"Record ID: {rec.get('id')}")
            print(f"final_article length: {len(str(rec.get('final_article', '')))}")
            print(f"final_article preview: {str(rec.get('final_article', ''))[:200]}")
    else:
        print(f"Unexpected response: {data}")
except Exception as e:
    print(f"Exception: {e}")