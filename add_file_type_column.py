import os
import requests
import json

# Try multiple locations for Token file
TOKEN_FILES = [
    os.path.join(".agent", "Token..txt"),
    os.path.join("..", ".agent", "Token..txt"),
    os.path.join("d:/quicktoolshub/rader/美国跨州合规报告/.agent", "Token..txt")
]

def parse_token_file():
    config = {}
    token_file = None
    for p in TOKEN_FILES:
        if os.path.exists(p):
            token_file = p
            break
            
    if not token_file:
        print("❌ Cannot find Token file.")
        return config

    with open(token_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if "Project ID:" in line:
                config['ref'] = line.split("Project ID:")[1].strip()
            if "api令牌" in line:
                parts = line.split("：") if "：" in line else line.split(":")
                if len(parts) > 1:
                    config['pat'] = parts[1].strip()
    return config

def main():
    config = parse_token_file()
    ref = config.get('ref')
    pat = config.get('pat')
    
    if not ref or not pat:
        print("❌ Missing Project Ref or PAT in Token file.")
        return

    # Using Supabase Management API to run SQL
    url = f"https://api.supabase.com/v1/projects/{ref}/query" 
    
    headers = {
        "Authorization": f"Bearer {pat}",
        "Content-Type": "application/json"
    }
    
    sql = """
    ALTER TABLE grich_keywords_pool 
    ADD COLUMN IF NOT EXISTS file_type TEXT DEFAULT 'pdf',
    ADD COLUMN IF NOT EXISTS content_raw TEXT;
    """
    payload = {"query": sql}
    
    print(f"🔌 Parsing SQL to {url}...")
    res = requests.post(url, json=payload, headers=headers)
    
    if res.status_code in [200, 201]:
         print("✅ SQL Executed Successfully.")
    elif res.status_code == 404:
         print("⚠️ /query endpoint not found, trying /sql...")
         url2 = f"https://api.supabase.com/v1/projects/{ref}/sql"
         res2 = requests.post(url2, json=payload, headers=headers)
         if res2.status_code in [200, 201]:
             print("✅ SQL Executed Successfully via /sql.")
         else:
             print(f"❌ Failed via /sql: {res2.status_code} {res2.text}")
    else:
         print(f"❌ Failed: {res.status_code} {res.text}")

if __name__ == "__main__":
    main()
