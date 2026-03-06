import os
import sys
import random
import requests
import urllib3
from supabase import create_client, Client
from matrix_config import config

# Disable warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    print("[LIBRARIAN AUDIT STARTED]")
    
    # 1. Setup
    supabase_url = config.supabase_url
    supabase_key = config.supabase_key
    tavily_key = os.environ.get("TAVILY_KEY") or config._config.get('tavily_key') # Try to get from config object if exposed, else need to parse again or assume env.
    
    # Re-parsing config if needed because matrix_config might not expose tavily_key property directly 
    # (it does expose zhipu, groq, ds, but let's check source code of matrix_config again... it didn't expose tavily_key property explicitly in the file I read).
    # I'll just manually parse Token..txt if env is missing, similar to matrix_librarian.py
    
    if not tavily_key:
         # Try to find Token file manually as fallback
         token_path = os.path.join(".agent", "Token..txt")
         if not os.path.exists(token_path):
             token_path = os.path.join("..", ".agent", "Token..txt")
         
         if os.path.exists(token_path):
             with open(token_path, 'r', encoding='utf-8') as f:
                 for line in f:
                     if "tvly-" in line:
                         tavily_key = line.split()[0].strip()
    
    if not tavily_key:
        print("[X] CRITICAL: TAVILY_KEY not found. Cannot perform live audit.")
        return

    try:
        supabase: Client = create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"[X] Database Connection Failed: {e}")
        return

    # 2. Fetch Sample
    print("Fetching 50 random samples...")
    # Getting a larger batch and sampling in python since random limit in SQL is tricky without RPC
    res = supabase.table("grich_keywords_pool").select("id, keyword, slug").eq("is_downloaded", False).limit(500).execute()
    all_candidates = res.data
    
    if not all_candidates:
        print("[!] No pending tasks found.")
        return

    sample_size = min(50, len(all_candidates))
    samples = random.sample(all_candidates, sample_size)
    
    print(f"Sampled {sample_size} keywords for stress testing.")
    
    results = {
        "A": 0, # Has PDF but download failed (Simulated: Tavily found PDF)
        "B": 0, # No PDF but HTML found
        "C": 0, # Nothing found
        "D": 0  # API Error
    }
    
    logs = []

    print("\n[AUDIT LOG]")
    print(f"{'ID':<5} | {'KEYWORD':<40} | {'STATUS':<20} | {'URL/NOTE'}")
    print("-" * 100)

    for item in samples:
        kw = item['keyword']
        search_query = f"site:.gov filetype:pdf {kw} report handbook"
        tavily_url = "https://api.tavily.com/search"
        payload = {
            "api_key": tavily_key,
            "query": search_query,
            "max_results": 3,
            "search_depth": "advanced"
        }
        
        status = "UNKNOWN"
        note = ""
        
        try:
            r = requests.post(tavily_url, json=payload, timeout=10)
            if r.status_code != 200:
                status = "D (API Error)"
                note = f"Status {r.status_code}"
                results["D"] += 1
            else:
                data = r.json()
                tav_results = data.get('results', [])
                
                if not tav_results:
                    # Try broader search without filetype:pdf to see if HTML exists
                    payload['query'] = f"site:.gov {kw} requirements"
                    r2 = requests.post(tavily_url, json=payload, timeout=10)
                    data2 = r2.json()
                    if data2.get('results'):
                        status = "B (HTML Found)"
                        note = data2['results'][0]['url']
                        results["B"] += 1
                    else:
                        status = "C (Nothing)"
                        note = "No relevant gov results"
                        results["C"] += 1
                else:
                    # Check if PDF
                    found_pdf = False
                    for res in tav_results:
                        if res['url'].lower().endswith('.pdf'):
                            status = "A (PDF Found)"
                            note = res['url']
                            results["A"] += 1
                            found_pdf = True
                            break
                    
                    if not found_pdf:
                         status = "B (HTML Found)" # Found results but not PDF
                         note = tav_results[0]['url']
                         results["B"] += 1

        except Exception as e:
            status = "D (Exception)"
            note = str(e)
            results["D"] += 1
            
        print(f"{item['id']:<5} | {kw[:38]:<40} | {status:<20} | {note[:50]}...")
        logs.append({"id": item['id'], "kw": kw, "status": status, "note": note})

    print("\n[SUMMARY]")
    print(f"Total Sampled: {sample_size}")
    print(f"A (PDF Found - Potential Download Fail): {results['A']}")
    print(f"B (HTML Found - Logic Too Strict):     {results['B']}")
    print(f"C (Ghost - Invalid Keyword):           {results['C']}")
    print(f"D (API/System Error):                  {results['D']}")

if __name__ == "__main__":
    main()
