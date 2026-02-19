"""SoEasyHub v2 Article Cleaner - Production Grade"""
import os
import re
import requests
import sys

# Force UTF-8 encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

# Read from environment variables
SB = os.environ.get("SUPABASE_URL", "MISSING_URL_PLEASE_SET_ENV")
KEY = os.environ.get("SUPABASE_KEY", "MISSING_KEY_PLEASE_SET_ENV")
headers = {
    'apikey': KEY,
    'Authorization': f'Bearer {KEY}',
    'Content-Type': 'application/json'
}

def clean_html(content, title):
    """Replicate _ensure_html logic from matrix_composer.py"""
    if not content:
        return content
    
    # 1. Boilerplate Strip
    content = content.replace('<!DOCTYPE html>', '').replace('<!doctype html>', '')
    
    # Regex for more complex tags
    content = re.sub(r'<html[^>]*>', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'</html>', '', content, flags=re.IGNORECASE)
    
    # Aggressively remove head block
    content = re.sub(r'<head>.*?</head>', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'<head\s+[^>]*>.*?</head>', '', content, flags=re.IGNORECASE | re.DOTALL)
    
    content = re.sub(r'<body[^>]*>', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'</body>', '', content, flags=re.IGNORECASE)
    
    # 2. Ghost Placeholder Purge
    content = content.replace("{{TITLE}}", title)
    content = content.replace("{{title}}", title)
    content = content.replace("{{", "").replace("}}", "")
    
    # 3. Ad/Extra Box Strip
    content = re.sub(r'<div[^>]*sponsored[^>]*>.*?</div>', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'<section[^>]*sponsored[^>]*>.*?</section>', '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # 4. Markdown Cleanup (simplified)
    if "## " in content or "**" in content:
        # If markdown present, we'd need markdown library, but skip for now
        pass
    
    # 5. Final aggressive strip
    if '<html' in content.lower() or '<body' in content.lower():
        body_match = re.search(r'<body[^>]*>(.*?)</body>', content, flags=re.IGNORECASE | re.DOTALL)
        if body_match:
            content = body_match.group(1).strip()
            content = re.sub(r'<html[^>]*>', '', content, flags=re.IGNORECASE | re.DOTALL)
            content = re.sub(r'</html>', '', content, flags=re.IGNORECASE)
            content = re.sub(r'<head>.*?</head>', '', content, flags=re.IGNORECASE | re.DOTALL)
            content = re.sub(r'<head\s+[^>]*>.*?</head>', '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # 6. Remove any remaining meta tags
    content = re.sub(r'<meta[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<title[^>]*>.*?</title>', '', content, flags=re.IGNORECASE | re.DOTALL)
    
    return content.strip()

def main():
    slug = "does-california-have-reciprocity-for-teachers"
    print(f"Fetching record for slug: {slug}")
    r = requests.get(f"{SB}/rest/v1/grich_keywords_pool?slug=eq.{slug}", headers=headers, timeout=10)
    if r.status_code != 200:
        print(f"Error fetching: {r.status_code} {r.text}")
        return
    data = r.json()
    if not isinstance(data, list) or len(data) == 0:
        print("No record found")
        return
    record = data[0]
    record_id = record['id']
    keyword = record['keyword']
    article = record.get('final_article', '')
    print(f"Current article length: {len(article)}")
    
    # Clean article
    cleaned = clean_html(article, keyword)
    print(f"Cleaned article length: {len(cleaned)}")
    
    # Check for unwanted tags
    unwanted = ['<!DOCTYPE', '<html', '<head', '<body', '<title>', '<meta charset', '<meta name="viewport"']
    for tag in unwanted:
        if tag.lower() in cleaned.lower():
            print(f"WARNING: Still contains {tag}")
    
    # Update database
    update_data = {"final_article": cleaned}
    update_r = requests.patch(f"{SB}/rest/v1/grich_keywords_pool?id=eq.{record_id}", headers=headers, json=update_data, timeout=10)
    if update_r.status_code == 204 or update_r.status_code == 200:
        print("Successfully updated article in database")
    else:
        print(f"Failed to update: {update_r.status_code} {update_r.text}")

if __name__ == "__main__":
    main()