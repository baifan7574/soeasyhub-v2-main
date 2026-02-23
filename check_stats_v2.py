import os
import requests
import json

# Try to load from Token file if env vars are missing
if not os.environ.get("SUPABASE_KEY"):
    token_paths = [
        os.path.join(".agent", "Token..txt"),
        os.path.join("..", ".agent", "Token..txt"),
        os.path.join("soeasyhub-v2", ".agent", "Token..txt")
    ]
    
    for path in token_paths:
        if os.path.exists(path):
            print(f"Loading config from {path}")
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if "Project URL:" in line: os.environ["SUPABASE_URL"] = line.split("URL:")[1].strip()
                    if "Secret keys:" in line: os.environ["SUPABASE_KEY"] = line.split("keys:")[1].strip()
            break

# Read from environment variables
SB = os.environ.get("SUPABASE_URL", "https://nbfzhxgkfljeuoncujum.supabase.co")
KEY = os.environ.get("SUPABASE_KEY", "MISSING_KEY_PLEASE_SET_ENV")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

print(f"Checking DB: {SB}")

try:
    # Total records
    print("Fetching total records...")
    r1 = requests.get(f"{SB}/rest/v1/grich_keywords_pool?select=id", headers=H, timeout=10)
    if r1.status_code != 200:
        print(f"Error fetching total: {r1.status_code} {r1.text}")
        total = 0
    else:
        total = len(r1.json())

    # Refined
    print("Fetching refined count...")
    r2 = requests.get(f"{SB}/rest/v1/grich_keywords_pool?select=id&is_refined=eq.true", headers=H, timeout=10)
    if r2.status_code == 200:
        refined = len(r2.json())
    else:
        print(f"Error refined: {r2.text}")
        refined = 0

    # Has article
    print("Fetching composed count...")
    r3 = requests.get(f"{SB}/rest/v1/grich_keywords_pool?select=id&final_article=not.is.null", headers=H, timeout=10)
    if r3.status_code == 200:
        composed = len(r3.json())
    else:
        print(f"Error composed: {r3.text}")
        composed = 0

    # Refined but no article (needs composing)
    print("Fetching needs_composing count...")
    # Using 'is' operator for null check in newer PostgREST syntax if needed, checking standard syntax
    # PostgREST: is_refined=eq.true & final_article=is.null
    r4 = requests.get(f"{SB}/rest/v1/grich_keywords_pool?select=id,slug&is_refined=eq.true&final_article=is.null", headers=H, timeout=10)
    if r4.status_code == 200:
        need_compose_list = r4.json()
    else:
        print(f"Error need_compose: {r4.text}")
        need_compose_list = []

    # Has pdf_url
    print("Fetching pdf count...")
    r5 = requests.get(f"{SB}/rest/v1/grich_keywords_pool?select=id&pdf_url=not.is.null", headers=H, timeout=10)
    if r5.status_code == 200:
        has_pdf = len(r5.json())
    else:
        print(f"Error has_pdf: {r5.text}")
        has_pdf = 0

    print("\n=== DB Stats ===")
    print(f"Total records: {total}")
    print(f"Refined (is_refined=true): {refined}")
    print(f"Has article (final_article not null): {composed}")
    print(f"Has pdf_url: {has_pdf}")
    print(f"Need composing (refined but no article): {len(need_compose_list)}")
    
    if need_compose_list:
        print("\nSample items needing composition:")
        for r in need_compose_list[:5]:
            print(f"  - {r.get('slug', 'unknown')}")
        if len(need_compose_list) > 5:
            print(f"  ... and {len(need_compose_list)-5} more")

except Exception as e:
    print(f"Exception during DB check: {e}")
