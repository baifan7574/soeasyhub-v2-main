import os
import json
import time
import argparse
import random
from openai import OpenAI
from supabase import create_client, Client

# ================= Matrix Composer (The Composer) - HOLY BIBLE EDITION v2.1 =================
# Status: Final Revision (Aligns with SKILL.md)
# Features: HTML-Only Output, Persona Rotation, Anti-N/A Logic, Double CTA, Internal Siloing.
# ============================================================================================

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
        
        if self.config.get('groq_key'):
             print("✍️ [Monetization Master] Engine: Groq Llama-3.3")
             self.client = OpenAI(api_key=self.config['groq_key'], base_url="https://api.groq.com/openai/v1", max_retries=3)
             self.model = "llama-3.3-70b-versatile"
        elif self.config.get('ds_key'):
             print("✍️ [Content Heavyweight] Engine: DeepSeek-V3")
             self.client = OpenAI(api_key=self.config['ds_key'], base_url="https://api.deepseek.com", max_retries=3)
             self.model = "deepseek-chat"
        else:
            raise ValueError("❌ Missing API Keys (GROQ_API_KEY or DEEPSEEK_API_KEY).")

    def _load_config(self):
        config = {
            'url': os.getenv('SUPABASE_URL'),
            'key': os.getenv('SUPABASE_KEY'),
            'ds_key': os.getenv('DEEPSEEK_API_KEY') or os.getenv('DSAPI'),
            'groq_key': os.getenv('GROQ_API_KEY')
        }
        
        if config['url'] and config['key'] and (config['ds_key'] or config['groq_key']):
            print("✅ Environment Variables LOADED.")
            return config

        token_paths = [
            '.agent/Token..txt',
            '../.agent/Token..txt',
            '../../.agent/Token..txt'
        ]
        for tp in token_paths:
            if os.path.exists(tp):
                try:
                    with open(tp, 'r', encoding='utf-8') as f:
                        for line in f:
                            if "Project URL:" in line: config['url'] = line.split("URL:")[1].strip()
                            if "Secret keys:" in line: config['key'] = line.split("keys:")[1].strip()
                            if "DSAPI:" in line: config['ds_key'] = line.split("DSAPI:")[1].strip()
                            if "groqapi" in line: config['groq_key'] = line.split(":")[1].strip()
                    print(f"✅ Loaded from {tp}")
                    return config
                except: pass
        return config

    def fetch_records(self, target_slug=None, limit=5):
        query = self.supabase.table("grich_keywords_pool").select("*")
        if target_slug:
            res = query.eq("slug", target_slug).execute()
        else:
            res = query.not_.is_("content_json", "null").is_("final_article", "null").order("last_mined_at", desc=True).limit(limit).execute()
        return res.data

    def compose_article(self, record):
        keyword = record['keyword']
        data = record['content_json']
        current_persona = random.choice(self.personas)
        
        fee = data.get('application_fee', '')
        time_est = data.get('processing_time', '')
        reqs = "\n".join([f"- {r}" for r in data.get('requirements', [])]) if isinstance(data.get('requirements'), list) else str(data.get('requirements', ''))
        steps = "\n".join([f"{i+1}. {s}" for i, s in enumerate(data.get('steps', []))]) if isinstance(data.get('steps'), list) else str(data.get('steps', ''))
        evidence = data.get('evidence', 'Official state guidelines')

        BUY_BUTTON = f"""
        <div class="monetization-box" style="background: #fff7ed; border: 2px dashed #f97316; padding: 35px; border-radius: 12px; margin: 45px 0; text-align: center;">
            <h3 style="color: #c2410c; margin-top: 0;">🚀 Skip the Labyrinth: Get Your 2026 {keyword} Fast-Track Bible</h3>
            <p style="color: #7c2d12;">Includes supplement templates, back-door contact lists, and our proven 21-point rejection-proof checklist.</p>
            <a href="{{{{PDF_LINK}}}}" style="display: inline-block; background: #f97316; color: white; padding: 18px 45px; border-radius: 8px; font-weight: bold; text-decoration: none; font-size: 1.2rem; box-shadow: 0 10px 15px -3px rgba(249, 115, 22, 0.3);">Unlock Audit Report ($29.9)</a>
            <p style="font-size: 0.8rem; color: #9a3412; margin-top: 15px;">🔒 100% Policy-Aligned | Instant Access | Save Months of Uncertainty</p>
        </div>
        """

        prompt = f"""
        PERSONA: {current_persona}.
        TOPIC: {keyword}.
        GOAL: High-Conversion SEO (1200+ words).
        FORMAT: Output STRICTLY in clean HTML. No ##, no **, no | symbols.

        --- DATA (Single Source of Truth) ---
        - Fee: "{fee if fee else 'USE 2026 INDUSTRY ESTIMATE'}"
        - Timeline: "{time_est if time_est else 'USE 2026 INDUSTRY ESTIMATE'}"
        - Requirements: {reqs}
        - Steps: {steps}
        - Evidence: "{evidence}"

        --- RULES ---
        1. HTML ONLY: Use <h1>, <h2>, <p>, <ul>, <li>, <strong>, <table>.
        2. NO "UNKNOWN": Use industry benchmark simulator for results like "$150-$450" if missing.
        3. DOUBLE CTA: Insert the HTML CTA block twice: 30% mark and before conclusion.
        4. INTERNAL SILO: Add "Explore Related Pathways" with 2-3 HTML links at the end.
        5. NO CODE BLOCKS.
        
        {BUY_BUTTON}
        """

        try:
            print(f"   🧠 [Persona: {current_persona}] Writing {keyword} (HTML)...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "HTML SEO Writer. No Markdown."},
                    {"role": "user", "content": prompt},
                ],
                timeout=300
            )
            content = response.choices[0].message.content
            if "```html" in content: content = content.replace("```html", "").replace("```", "")
            elif "```" in content: content = content.replace("```", "")
            return content.strip()
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None

    def run(self, target_slug=None, batch_size=5):
        records = self.fetch_records(target_slug, limit=batch_size)
        if not records: return print("💤 No work.")
        for record in records:
            print(f"✍️ [Working] {record['slug']}")
            article = self.compose_article(record)
            if article:
                self.supabase.table("grich_keywords_pool").update({"final_article": article}).eq("id", record['id']).execute()
                print(f"   ✅ [Success] Chars: {len(article)}")
            time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", help="Regenerate one record")
    parser.add_argument("--batch", type=int, default=5, help="Number of records to process")
    args = parser.parse_args()
    MatrixComposer().run(target_slug=args.slug, batch_size=args.batch)
