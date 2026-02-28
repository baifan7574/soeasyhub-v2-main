import os
import json
import logging
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_latest_urls():
    """Fetch the latest 200 published URLs from Supabase."""
    supabase_url = os.environ.get("SUPABASE_URL", "").strip()
    supabase_key = os.environ.get("SUPABASE_KEY", "").strip()
    
    if not supabase_url or not supabase_key:
        logging.error("Missing SUPABASE_URL or SUPABASE_KEY environment variables.")
        return []

    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}"
    }
    
    # Get 200 URLs that have a final_article (published) ordered by id descending (assuming newer records have higher IDs or we just limit to 200)
    # Ideally, we order by updated_at or created_at if they exist. Using id.desc for now.
    url = f"{supabase_url}/rest/v1/grich_keywords_pool?select=slug&final_article=not.is.null&order=id.desc&limit=200"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        records = response.json()
        urls = [f"https://soeasyhub.com/{record['slug']}" for record in records if record.get('slug')]
        logging.info(f"Fetched {len(urls)} URLs from Supabase.")
        return urls
    except Exception as e:
        logging.error(f"Error fetching URLs from Supabase: {e}")
        return []

def push_to_google(urls):
    """Push URLs to Google Indexing API."""
    json_creds_str = os.environ.get("GOOGLE_SEO_JSON")
    if not json_creds_str:
        logging.warning("Missing GOOGLE_SEO_JSON environment variable. Skipping Google Indexing API.")
        return

    try:
        creds_info = json.loads(json_creds_str)
        credentials = service_account.Credentials.from_service_account_info(
            creds_info, scopes=["https://www.googleapis.com/auth/indexing"]
        )
        service = build("indexing", "v3", credentials=credentials)
        
        success_count = 0
        error_count = 0
        
        for url in urls:
            try:
                # We can update or delete, using URL_UPDATED for new/updated pages
                body = {
                    "url": url,
                    "type": "URL_UPDATED"
                }
                response = service.urlNotifications().publish(body=body).execute()
                logging.info(f"Google Indexing API success for {url}: {response}")
                success_count += 1
            except Exception as e:
                logging.error(f"Google Indexing API error for {url}: {e}")
                error_count += 1
                if "Quota exceeded" in str(e):
                    logging.warning("Google Indexing API quota exceeded. Stopping further Google requests.")
                    break
        
        logging.info(f"Google Indexing Summary: {success_count} success, {error_count} errors.")
        
    except Exception as e:
        logging.error(f"Failed to initialize Google Indexing API: {e}")

def push_to_bing(urls):
    """Push URLs to Bing IndexNow API."""
    if not urls:
        return
        
    bing_key = "822834cd8b83498a90e4fd5ef715fa14"
    host = "soeasyhub.com"
    endpoint = "https://api.indexnow.org/indexnow"
    
    payload = {
        "host": host,
        "key": bing_key,
        "keyLocation": f"https://{host}/{bing_key}.txt", # IndexNow standard key location (or in our case worker.js handles it if hit directly)
        "urlList": urls
    }
    
    try:
        response = requests.post(endpoint, json=payload, timeout=10)
        if response.status_code in [200, 202]:
            logging.info(f"Bing IndexNow success. Pushed {len(urls)} URLs. Status Code: {response.status_code}")
        else:
            logging.error(f"Bing IndexNow error. Status Code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        logging.error(f"Bing IndexNow request failed: {e}")

if __name__ == "__main__":
    logging.info("Starting SEO Pusher...")
    target_urls = get_latest_urls()
    
    if target_urls:
        push_to_google(target_urls)
        push_to_bing(target_urls)
    else:
        logging.info("No URLs found to push.")
    
    logging.info("SEO Pusher completed.")
