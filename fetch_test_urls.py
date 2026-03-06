import os
import random
import requests
import urllib3
from dotenv import load_dotenv

# Disable warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Config Loading (Borrowed from MatrixLibrarian)
TOKEN_FILE = os.path.join(".agent", "Token..txt")
ALT_TOKEN_FILE = os.path.join("..", ".agent", "Token..txt")

def load_config():
    config = {}
    
    # Try local file first (development)
    token_path = None
    if os.path.exists(TOKEN_FILE):
        token_path = TOKEN_FILE
    elif os.path.exists(ALT_TOKEN_FILE):
        token_path = ALT_TOKEN_FILE
        
    if token_path:
        print(f"Loading config from {token_path}")
        with open(token_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                if "tvly-" in line:
                    config['tavily_key'] = line.split()[0].strip()
    
    # Fallback to env vars
    if 'tavily_key' not in config:
        config['tavily_key'] = os.environ.get("TAVILY_KEY")
        
    if 'tavily_key' not in config:
        raise ValueError("Critical: TAVILY_KEY not found.")
        
    return config

def search_gov_html(keyword, api_key):
    # Explicitly exclude PDF filetype in query
    query = f"site:.gov -filetype:pdf {keyword} requirements license reciprocity"
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "max_results": 5, # Fetch more results to filter manually if needed
        "search_depth": "advanced",
        "include_domains": [".gov"],
        "exclude_domains": [] 
    }
    try:
        res = requests.post(url, json=payload, timeout=15)
        data = res.json()
        if 'results' in data:
            for result in data['results']:
                url = result['url']
                if not url.lower().endswith('.pdf'):
                    return url
        return None
    except Exception as e:
        print(f"Search Error: {e}")
        return None

if __name__ == "__main__":
    try:
        config = load_config()
        print("Tavily Key Loaded.")
        
        seeds = [
            "Nurse license reciprocity California",
            "Teacher license reciprocity Texas",
            "Electrician license reciprocity Florida",
            "CPA license reciprocity New York",
            "Real Estate Agent license reciprocity Illinois"
        ]
        
        print("\n=== Fetching 5 Real Government HTML URLs ===\n")
        
        found_urls = []
        for seed in seeds:
            print(f"Searching for: {seed}...")
            url = search_gov_html(seed, config['tavily_key'])
            if url:
                print(f"   -> Found: {url}")
                found_urls.append(url)
            else:
                print("   -> No results found.")
            
        print("\n=== Results ===")
        for i, u in enumerate(found_urls):
            print(f"{i+1}. {u}")
            
    except Exception as e:
        print(f"Error: {e}")
