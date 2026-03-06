import requests
import json
import os
from bs4 import BeautifulSoup
from matrix_refiner import MatrixRefiner
from matrix_config import config

# Initialize Refiner (reusing existing config logic)
# This requires valid config environment
try:
    refiner = MatrixRefiner(batch_size=1)
    print("[SUCCESS] MatrixRefiner initialized.")
except Exception as e:
    print(f"[ERROR] Failed to initialize MatrixRefiner: {e}")
    exit(1)

TEST_URLS = [
    "https://www.cdph.ca.gov/Programs/CHCQ/LCP/Pages/How-to-Complete-Your-Reciprocity-Application-Package.aspx?utm_source=chatgpt.com",
    "https://tea.texas.gov/texas-educators/certification/out-of-state-certification/out-of-state-certified-educators",
    "https://hcfl.gov/businesses/hillsgovhub/contractor-licensing/contractor-licensing-how-to-and-forms",
    "https://portal.ct.gov/dcp/occupational-and-professional-division/occupational--profess/cpa-certificate-by-reciprocity",
    "https://www.ilga.gov/ftp/JCAR/AdminCode/068/068014500D04400R.html"
]

def fetch_and_clean_html(url):
    print(f"[FETCHING]: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        res = requests.get(url, headers=headers, timeout=15, verify=False)
        res.raise_for_status()
        
        soup = BeautifulSoup(res.content, 'html.parser')
        
        # Remove scripts and styles
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
            
        text = soup.get_text(separator="\n")
        
        # Basic cleanup
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        print(f"   [ERROR] Fetch Error: {e}")
        return None

def test_html_refining():
    print("\n=== HTML Compatibility Blind Test ===\n")
    
    results = []
    
    for i, url in enumerate(TEST_URLS):
        print(f"--- Test Case {i+1} ---")
        text = fetch_and_clean_html(url)
        
        if not text:
            print("   [WARN] Skipping (No content)")
            results.append({"url": url, "status": "fetch_failed"})
            continue
            
        print(f"   [INFO] Extracted {len(text)} characters.")
        
        # Truncate if too long (LLM context limit)
        if len(text) > 20000:
            text = text[:20000]
            print("   [INFO] Truncated to 20000 chars.")
            
        # Use Refiner's AI Logic
        print("   [AI] Sending to AI...")
        try:
            # We bypass the DB part and call the LLM logic directly
            # refiner.refine_with_ai returns a JSON string or None
            
            # The prompt in refine_with_ai is:
            # "Extract structured data... application_fee, processing_time, requirements, steps, evidence..."
            
            json_str = refiner.refine_with_ai(text)
            
            if json_str:
                try:
                    data = json.loads(json_str)
                    print("   [SUCCESS] Valid JSON received.")
                    # Check quality
                    keys = ["application_fee", "processing_time", "requirements", "steps"]
                    missing = [k for k in keys if k not in data]
                    
                    if not missing:
                        print("   [SUCCESS] Schema Valid (All keys present).")
                        status = "pass"
                    else:
                        print(f"   [WARN] Schema Incomplete. Missing: {missing}")
                        status = "partial"
                        
                    results.append({
                        "url": url,
                        "status": status,
                        "data_preview": {k: str(v)[:50] + "..." for k, v in data.items() if isinstance(v, str)}
                    })
                    
                except json.JSONDecodeError:
                    print(f"   [ERROR] Invalid JSON format: {json_str[:100]}...")
                    results.append({"url": url, "status": "invalid_json"})
            else:
                print("   [ERROR] AI returned None.")
                results.append({"url": url, "status": "ai_failed"})
                
        except Exception as e:
            print(f"   [ERROR] Processing Error: {e}")
            results.append({"url": url, "status": "error", "msg": str(e)})
            
        print("\n")

    # Summary
    print("=== Test Summary ===")
    for r in results:
        print(f"{r['status'].upper()}: {r['url']}")
        if r.get('status') in ['pass', 'partial']:
            print(f"   Preview: {r.get('data_preview')}")

if __name__ == "__main__":
    test_html_refining()
