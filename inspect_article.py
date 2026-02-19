"""SoEasyHub v2 Article Inspector - Production Grade"""
import os
import requests
import re

# Read from environment variables
SB = os.environ.get("SUPABASE_URL", "MISSING_URL_PLEASE_SET_ENV")
KEY = os.environ.get("SUPABASE_KEY", "MISSING_KEY_PLEASE_SET_ENV")
headers = {
    'apikey': KEY,
    'Authorization': f'Bearer {KEY}',
    'Content-Type': 'application/json'
}

def main():
    slug = "does-california-have-reciprocity-for-teachers"
    r = requests.get(f"{SB}/rest/v1/grich_keywords_pool?slug=eq.{slug}", headers=headers, timeout=10)
    if r.status_code == 200:
        data = r.json()
        if isinstance(data, list) and data:
            rec = data[0]
            article = rec.get('final_article', '')
            print(f"Article length: {len(article)}")
            # Show first 500 chars
            print("\n=== First 500 chars ===")
            print(article[:500])
            print("\n=== Checking for unwanted tags ===")
            # Check for unwanted tags
            unwanted = ['<!DOCTYPE', '<html', '<head', '<body', '<title>', '<meta charset', '<meta name="viewport"']
            for tag in unwanted:
                if tag.lower() in article.lower():
                    print(f"Found: {tag}")
            # Count occurrences
            for tag in ['<!DOCTYPE', '<html', '<head', '<body', '</html>', '</head>', '</body>']:
                count = article.lower().count(tag.lower())
                if count > 0:
                    print(f"Count of {tag}: {count}")
            # Check for placeholders
            if '{{' in article or '}}' in article:
                print("Found placeholder braces")
            # Check for markdown
            if '##' in article or '**' in article:
                print("Found markdown syntax")
            # Check for double $29.9 buttons
            if '$29.9' in article or '$29.9' in article:
                print("Found $29.9 button reference")
            else:
                print("No $29.9 button found (may need injection)")
            # Show snippet around first button if any
            button_pattern = r'\$29\.9|\$29\s*\.\s*9|29\.9|29\s*\.\s*9'
            matches = re.findall(button_pattern, article, re.IGNORECASE)
            if matches:
                print(f"Found {len(matches)} potential price references")
                # find first occurrence index
                match = re.search(button_pattern, article, re.IGNORECASE)
                if match:
                    start = max(0, match.start() - 50)
                    end = min(len(article), match.end() + 50)
                    print(f"Context: ...{article[start:end]}...")
            else:
                print("No price references found")
    else:
        print(f"Failed to fetch: {r.status_code} {r.text}")

if __name__ == "__main__":
    main()