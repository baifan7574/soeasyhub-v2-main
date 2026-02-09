import os
import json
import time
import argparse
import random
from openai import OpenAI
from supabase import create_client, Client

class MatrixComposer:
    def __init__(self):
        url = os.environ.get('SUPABASE_URL')
        key = os.environ.get('SUPABASE_KEY')
        ds_key = os.environ.get('DEEPSEEK_API_KEY')
        groq_key = os.environ.get('GROQ_API_KEY')

        if not url or not key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables.")
        
        self.supabase: Client = create_client(url, key)
        
        if groq_key:
            print("✍️ [Engine] Groq Llama-3.3")
            self.client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
            self.model = "llama-3.3-70b-versatile"
        elif ds_key:
            print("✍️ [Engine] DeepSeek-V3")
            self.client = OpenAI(api_key=ds_key, base_url="https://api.deepseek.com")
            self.model = "deepseek-chat"
        else:
            raise ValueError("Missing GROQ_API_KEY or DEEPSEEK_API_KEY environment variables.")

        self.personas = [
            "Senior Regulatory Consultant",
            "Professional Peer",
            "State Board Policy Auditor",
            "Specialized Compliance Expert"
        ]

    def fetch_records(self, target_slug=None, limit=5):
        query = self.supabase.table("grich_keywords_pool").select("*")
        if target_slug:
            res = query.eq("slug", target_slug).execute()
        else:
            res = query.not_.is_("content_json", "null").is_("final_article", "null").limit(limit).execute()
        return res.data

    def compose(self, record):
        keyword = record['keyword']
        data = record['content_json']
        persona = random.choice(self.personas)

        BUY_BUTTON = f"""
        <div style="background: #fff7ed; border: 2px dashed #f97316; padding: 35px; border-radius: 12px; margin: 45px 0; text-align: center;">
            <h3 style="color: #c2410c; margin-top: 0;">🚀 Skip the Labyrinth: Get Your 2026 {keyword} Fast-Track Bible</h3>
            <a href="/download/{record['slug']}" style="display: inline-block; background: #f97316; color: white; padding: 18px 45px; border-radius: 8px; font-weight: bold; text-decoration: none; font-size: 1.2rem;">Unlock Audit Report ($29.9)</a>
        </div>
        """

        prompt = f"""
        Persona: {persona}. Topic: {keyword}. 
        Data: {json.dumps(data)}.
        Output raw HTML only. Use <h1>, <h2>, <p>, <ul>, <table>.
        Insert this CTA exactly twice (at 30% and 90%):
        {BUY_BUTTON}
        """

        try:
            print(f"   🧠 Writing: {keyword}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": "Professional SEO HTML Writer."},
                          {"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content
            if "```html" in content: content = content.replace("```html", "").replace("```", "")
            return content.strip()
        except Exception as e:
            print(f"   ❌ Compose Error: {e}")
            return None

    def run(self, target_slug=None, batch_size=5):
        records = self.fetch_records(target_slug, batch_size)
        if not records:
            print("💤 No pending articles.")
            return

        for r in records:
            print(f"✍️ [Working] {r['slug']}")
            article = self.compose(r)
            if article:
                self.supabase.table("grich_keywords_pool").update({"final_article": article}).eq("id", r['id']).execute()
                print(f"   ✅ Article Saved.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", help="Process single record")
    parser.add_argument("--batch", type=int, default=1, help="Number of records")
    args = parser.parse_args()
    MatrixComposer().run(target_slug=args.slug, batch_size=args.batch)
