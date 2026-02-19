import os
import json
import time
import argparse
import random
import google.generativeai as genai
from openai import OpenAI
from supabase import create_client, Client
import markdown
import httpx
import re

# ================= Matrix Composer (The Composer) - HOLY BIBLE EDITION v2.6 =================
# Status: Production Grade
# Mission: Clean HTML Snippet Production (No HTML/HEAD/BODY tags)
# ============================================================================================

# Local Token Fallback logic
def find_token_file():
    paths = [
        os.path.join(os.path.dirname(__file__), ".agent", "Token..txt"),
        os.path.join(os.path.dirname(__file__), "..", ".agent", "Token..txt"),
        os.path.join(".agent", "Token..txt")
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None

TOKEN_FILE = find_token_file()

# Environment variable names for cloud deployment
ENV_SUPABASE_URL = "SUPABASE_URL"
ENV_SUPABASE_KEY = "SUPABASE_KEY"
ENV_GOOGLE_API_KEY = "GOOGLE_API_KEY"

class MatrixComposer:
    def __init__(self):
        self.config = self._load_config()
        self.supabase: Client = create_client(self.config['url'], self.config['key'])
        
        self.personas = [
            "Senior Regulatory Consultant (25 years experience)",
            "Professional Peer & Active Licensing Advocate",
            "State Board Policy Auditor",
            "Specialized Compliance Immigration Expert",
            "Independent Licensing Industry Observer"
        ]
        
        if self.config.get('google_key'):
            self.google_key = self.config['google_key']
            self.client_type = "google_rest" 
            self.model = "gemini-3-pro-preview" 
            print(f"[Gemini Factory] Engine locked (REST Mode): {self.model}")
        else:
            raise ValueError("Missing Google API Key.")

    def _load_config(self):
        config = {}
        supabase_url = os.environ.get(ENV_SUPABASE_URL)
        supabase_key = os.environ.get(ENV_SUPABASE_KEY)
        google_key = os.environ.get(ENV_GOOGLE_API_KEY)
        
        if supabase_url and supabase_key:
            config['url'] = supabase_url
            config['key'] = supabase_key
            config['google_key'] = google_key
            return config

        if TOKEN_FILE and os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if "Project URL:" in line: config['url'] = line.split("URL:")[1].strip()
                    if "Secret keys:" in line: config['key'] = line.split("keys:")[1].strip()
                    if "GOOGLE_API_KEY:" in line: config['google_key'] = line.split("KEY:")[1].strip()
            if config.get('url') and config.get('key'):
                return config
        raise ValueError("Critical Error: Missing Config.")

    def fetch_records(self, target_slug=None, limit=5, force=False):
        query = self.supabase.table("grich_keywords_pool").select("*")
        if target_slug:
            res = query.eq("slug", target_slug).execute()
        else:
            query = query.not_.is_("content_json", "null").order("last_mined_at", desc=True)
            res = query.limit(limit * 2).execute()
        return res.data

    def compose_article(self, record):
        keyword = record['keyword']
        data = record['content_json']
        current_persona = random.choice(self.personas)
        
        fee = data.get('application_fee', '')
        time_est = data.get('processing_time', '')
        reqs = str(data.get('requirements', ''))
        steps = str(data.get('steps', ''))

        PAYHIP_LINK = "https://payhip.com/b/qoGLF"
        # CLEAN BUTTON: Minimalist anchor, no background boxes as requested by CEO
        BUY_BUTTON = f'<p style="text-align:center;margin:40px 0;"><a href="{PAYHIP_LINK}" style="background:#ea580c;color:white;padding:16px 40px;border-radius:50px;font-weight:700;text-decoration:none;font-size:1.2rem;box-shadow:0 10px 15px -3px rgba(234,88,12,0.3);">Download Official {keyword} Audit Report ($29.90)</a></p>'

        prompt = f"""
        PERSONA: {current_persona}.
        TOPIC: {keyword}.
        GOAL: Professional Regulatory Audit Report (Minimum 1800+ words).
        FORMAT: Output ONLY the article content. Start directly with the first paragraph or H2. 
        CRITICAL: DO NOT include <html>, <head>, <body>, or <title> tags. DO NOT include CSS.
        STRICTLY HTML SNIPPET ONLY.

        --- DATA ARSENAL ---
        - Fee: "{fee if fee else 'USE 2026 INDUSTRY ESTIMATE'}"
        - Timeline: "{time_est if time_est else 'USE 2026 INDUSTRY ESTIMATE'}"
        - Requirements: {reqs}
        - Steps: {steps}

        --- RULES ---
        1. HTML TAGS ONLY (<h1>, <h2>, <p>, <ul>, <li>, <strong>, <table>).
        2. NOCSS, NO JS.
        3. EXACTLY TWO CTAs: Insert the PROVIDED BUTTON at the 30% mark and 90% mark.
        4. NO SPONSORED CONTENT.
        5. NO PLACEHOLDERS: Use "{keyword}" instead of "{{{{TITLE}}}}".
        """

        print(f"   [Persona: {current_persona}] Writing {keyword}...")
        
        for attempt in range(3):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.google_key}"
                payload = {
                    "contents": [{"parts": [{"text": f"SYSTEM: You are a professional licensing auditor. Output HTML SNIPPETS ONLY. No page boilerplate. No Markdown.\n\nUSER: {prompt}"}]}],
                    "generationConfig": {"temperature": 0.7}
                }
                response = httpx.post(url, json=payload, timeout=300.0)
                if response.status_code == 200:
                    content = response.json()['candidates'][0]['content']['parts'][0]['text']
                    content = content.replace("```html", "").replace("```", "").strip()
                    return content
                else:
                    time.sleep(5)
            except Exception as e:
                time.sleep(5)
        return None

    def _ensure_html(self, content, title):
        if not content: return content
        
        # 1. Boilerplate Strip (If AI ignored instructions)
        content = re.sub(r'<!DOCTYPE.*?>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'<html.*?>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'<head.*?>.*?</head>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'<body.*?>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = content.replace('</html>', '').replace('</body>', '')
        
        # 2. Ghost Placeholder Purge
        content = content.replace("{{TITLE}}", title)
        content = content.replace("{{title}}", title)
        content = content.replace("{{", "").replace("}}", "")
        
        # 3. Ad/Extra Box Strip
        content = re.sub(r'<div[^>]*sponsored[^>]*>.*?</div>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'<section[^>]*sponsored[^>]*>.*?</section>', '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # 4. Markdown Cleanup
        if "## " in content or "**" in content:
            content = markdown.markdown(content, extensions=['extra', 'tables'])
            
        return content.strip()

    def run(self, target_slug=None, batch_size=5, force=False):
        records = self.fetch_records(target_slug, limit=batch_size, force=force)
        if not records: return
        for record in records:
            print(f"[Working] {record['slug']}")
            article = self.compose_article(record)
            if article:
                article = self._ensure_html(article, record['keyword'])
                self.supabase.table("grich_keywords_pool").update({"final_article": article}).eq("id", record['id']).execute()
                print(f"   [Success] {len(article)} chars")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", help="Regenerate one record")
    parser.add_argument("--batch", type=int, default=5, help="Number of records to process")
    parser.add_argument('--force', action='store_true', help='Force')
    args = parser.parse_args()
    composer = MatrixComposer()
    composer.run(target_slug=args.slug, batch_size=args.batch, force=args.force)
