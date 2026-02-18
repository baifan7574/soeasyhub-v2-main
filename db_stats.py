import os
import requests

# Read from environment variables or use placeholders
SB = os.environ.get("SUPABASE_URL", "https://nbfzhxgkfljeuoncujum.supabase.co")
KEY = os.environ.get("SUPABASE_KEY", "MISSING_KEY_PLEASE_SET_ENV")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

# Total records
r1 = requests.get(f"{SB}/rest/v1/grich_keywords_pool?select=id", headers=H, timeout=10)
total = len(r1.json())

# Refined
r2 = requests.get(f"{SB}/rest/v1/grich_keywords_pool?select=id&is_refined=eq.true", headers=H, timeout=10)
refined = len(r2.json())

# Has article
r3 = requests.get(f"{SB}/rest/v1/grich_keywords_pool?select=id&final_article=not.is.null", headers=H, timeout=10)
composed = len(r3.json())

# Refined but no article (needs composing)
r4 = requests.get(f"{SB}/rest/v1/grich_keywords_pool?select=id,slug&is_refined=eq.true&final_article=is.null", headers=H, timeout=10)
need_compose = r4.json()

# Has pdf_url
r5 = requests.get(f"{SB}/rest/v1/grich_keywords_pool?select=id&pdf_url=not.is.null", headers=H, timeout=10)
has_pdf = len(r5.json())

print("=== DB Stats ===")
print(f"Total records: {total}")
print(f"Refined (is_refined=true): {refined}")
print(f"Has article (final_article not null): {composed}")
print(f"Has pdf_url: {has_pdf}")
print(f"Need composing (refined but no article): {len(need_compose)}")
if need_compose:
    for r in need_compose[:5]:
        print(f"  - {r['slug']}")
    if len(need_compose) > 5:
        print(f"  ... and {len(need_compose)-5} more")
