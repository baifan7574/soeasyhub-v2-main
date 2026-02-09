import os
import json
import time
import argparse
import random
from openai import OpenAI
from supabase import create_client, Client

# ================= Matrix Composer (The Composer) - HOLY BIBLE EDITION =================
# Status: Final Revision (Aligns with SKILL.md)
# Features: Persona Rotation, Anti-N/A Logic, Double CTA, Internal Siloing.

TOKEN_FILE = os.path.join(os.path.dirname(__file__), "..", ".agent", "Token..txt")

class MatrixComposer:
    def __init__(self):
        self.config = self._load_config()
        self.supabase: Client = create_client(self.config['url'], self.config['key'])
        
        # Persona Pool for Randomization (Anti-De-indexing)
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
            raise ValueError("❌ Missing API Keys.")

    def _load_config(self):
        config = {}
        with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if "Project URL:" in line: config['url'] = line.split("URL:")[1].strip()
                if "Secret keys:" in line: config['key'] = line.split("keys:")[1].strip()
                if "DSAPI:" in line: config['ds_key'] = line.split("DSAPI:")[1].strip()
                if "groqapi" in line: config['groq_key'] = line.split(":")[1].strip()
        return config

    def fetch_records(self, target_slug=None, limit=5):
        query = self.supabase.table("grich_keywords_pool").select("*")
        if target_slug:
            res = query.eq("slug", target_slug).execute()
        else:
            # Fetch records that have refined content but no final article yet
            res = query.not_.is_("content_json", "null").is_("final_article", "null").limit(limit).execute()
        return res.data

    def compose_article(self, record):
        # ... (keep existing logic)
        keyword = record['keyword']
        data = record['content_json']
        current_persona = random.choice(self.personas)
        
        # Hard Data Extraction
        fee = data.get('application_fee', '')
        time_est = data.get('processing_time', '')
        reqs = "\n".join([f"- {r}" for r in data.get('requirements', [])])
        steps = "\n".join([f"{i+1}. {s}" for i, s in enumerate(data.get('steps', []))])
        evidence = data.get('evidence', 'Official state guidelines')

        # CTA Component
        BUY_BUTTON = """
        <div class="monetization-box" style="background: #fff7ed; border: 2px dashed #f97316; padding: 35px; border-radius: 12px; margin: 45px 0; text-align: center;">
            <h3 style="color: #c2410c; margin-top: 0;">🚀 Skip the Labyrinth: Get Your 2026 {keyword} Fast-Track Bible</h3>
            <p style="color: #7c2d12;">Includes supplement templates, back-door contact lists, and our proven 21-point rejection-proof checklist.</p>
            <a href="{{PDF_LINK}}" style="display: inline-block; background: #f97316; color: white; padding: 18px 45px; border-radius: 8px; font-weight: bold; text-decoration: none; font-size: 1.2rem; box-shadow: 0 10px 15px -3px rgba(249, 115, 22, 0.3);">Unlock Audit Report ($29.9)</a>
            <p style="font-size: 0.8rem; color: #9a3412; margin-top: 15px;">🔒 100% Policy-Aligned | Instant Access | Save Months of Uncertainty</p>
        </div>
        """

        prompt = f"""
        PERSONA: {current_persona}.
        TOPIC: {keyword}.
        LANGUAGE: Strictly English.
        GOAL: High-Conversion SEO Landing Page (1200+ words).

        --- DATA ARSENAL ---
        - Fee: "{fee if fee else 'USE INDUSTRY ESTIMATE'}"
        - Timeline: "{time_est if time_est else 'USE INDUSTRY ESTIMATE'}"
        - Requirements: {reqs}
        - Steps: {steps}
        - Evidence Link: "{evidence}"

        --- HOLY BIBLE RULES ---
        1. NO "UNKNOWN": Under no circumstances use "Not Mentioned" or "Unknown". If a field is missing, use your "2026 Industry Benchmark Simulator" to give a realistic range (e.g., "$150-$450") and add the disclaimer: "Based on 2026 industry average benchmarks for similar state boards."
        2. DOUBLE CTA: You MUST insert the provided HTML CTA block twice: once at the 30% mark (after the financial pain point) and once before the conclusion.
        3. DATA ANCHORING: Boldly highlight the fee. Contrast it with the cost of failure.
        4. INTERNAL SILO: At the very end, generate an "Explore Related Pathways" section linking to 2-3 similar professions or states (e.g., "Related: [How to transfer a New York RN license to {keyword.split()[-1]}]").
        5. SCHEMA FAQ: End with 3-5 Schema.org optimized Q&A pairs.

        --- HTML CTA COMPONENT ---
        {BUY_BUTTON.format(keyword=keyword)}

        --- STRUCTURE ---
        - H1 Headline (Expert Level)
        - Executive Comparison Matrix
        - The Financial Stakes (Discussion of Fee)
        - The Eligibility Labyrinth
        - Operational Roadmap (Step-by-Step)
        - Common Point of Rejections (The "Ghost" Requirements)
        - Industry Disclaimer Case Study
        - Conclusion & Final CTA
        """

        try:
            print(f"   🧠 [Persona: {current_persona}] Writing {keyword}...")
            
            # --- Robust Retry Logic with Multi-Engine Support ---
            engines = []
            if self.config.get('groq_key'): engines.append(('Groq', self.config['groq_key'], "https://api.groq.com/openai/v1", "llama-3.3-70b-versatile"))
            if self.config.get('ds_key'): engines.append(('DeepSeek', self.config['ds_key'], "https://api.deepseek.com", "deepseek-chat"))
            
            # Shuffle so we don't always hit the same one first
            random.shuffle(engines)
            
            for attempt in range(3): # 3 retries total
                for engine_name, api_key, base_url, model_name in engines:
                    try:
                        temp_client = OpenAI(api_key=api_key, base_url=base_url)
                        response = temp_client.chat.completions.create(
                            model=model_name,
                            messages=[
                                {"role": "system", "content": "You are a world-class SEO technical writer and compliance expert. You never write 'Not Mentioned'. Always provide value-added estimations."},
                                {"role": "user", "content": prompt},
                            ],
                            timeout=300
                        )
                        return response.choices[0].message.content
                    except Exception as engine_err:
                        err_str = str(engine_err).lower()
                        if "rate_limit" in err_str or "429" in err_str:
                            wait_time = 30 # Default wait
                            if "try again in" in err_str:
                                try:
                                    # Try to extract seconds (e.g., "try again in 13.5s")
                                    parts = err_str.split("try again in ")
                                    wait_time = float(parts[1].split('s')[0]) + 1
                                except: pass
                            
                            print(f"   ⚠️ {engine_name} Rate Limited. Waiting {wait_time}s...")
                            time.sleep(wait_time)
                            continue # Try next engine or retry
                        else:
                            print(f"   ❌ {engine_name} Error: {engine_err}")
                            continue
                
                print(f"   🔄 Attempt {attempt+1} failed for all engines. Sleeping 60s...")
                time.sleep(60)
            
            return None
        except Exception as e:
            print(f"   ❌ Critical Composer Error: {e}")
            return None

    def run(self, target_slug=None, batch_size=5):
        records = self.fetch_records(target_slug, limit=batch_size)
        if not records:
            print("💤 No tasks.")
            return

        print(f"🚀 [Batch Injection] Starting {len(records)} articles...")
        for record in records:
            print(f"\n✍️ [Working] {record['slug']}")
            article = self.compose_article(record)
            if article:
                self.supabase.table("grich_keywords_pool").update({
                    "final_article": article
                }).eq("id", record['id']).execute()
                print(f"   ✅ [Perfect Score] Chars: {len(article)}")
            else:
                print(f"   ⚠️ [Skipped] Failed to compose {record['slug']} after retries.")
            time.sleep(2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", help="Regenerate one record")
    parser.add_argument("--batch", type=int, default=5, help="Number of records to process")
    args = parser.parse_args()
    
    composer = MatrixComposer()
    composer.run(target_slug=args.slug, batch_size=args.batch)
