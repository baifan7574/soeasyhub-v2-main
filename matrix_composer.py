import os
import json
import time
import argparse
import random
import markdown  # Standard Python Markdown library
from openai import OpenAI
from supabase import create_client, Client

class MatrixComposer:
    def __init__(self):
        url = os.environ.get('SUPABASE_URL')
        key = os.environ.get('SUPABASE_KEY')
        # Support multiple AI backends
        ds_key = os.environ.get('DEEPSEEK_API_KEY')
        groq_key = os.environ.get('GROQ_API_KEY')

        if not url or not key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables.")
        
        self.supabase: Client = create_client(url, key)
        
        # Priority: Groq (Llama-3.3) -> DeepSeek -> Error
        if groq_key:
            print("✍️ [Engine] Groq Llama-3.3 (High Speed)")
            self.client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
            self.model = "llama-3.3-70b-versatile"
        elif ds_key:
            print("✍️ [Engine] DeepSeek-V3 (Fallback)")
            self.client = OpenAI(api_key=ds_key, base_url="https://api.deepseek.com")
            self.model = "deepseek-chat"
        else:
            raise ValueError("Missing AI API Key (GROQ_API_KEY or DEEPSEEK_API_KEY).")

        self.personas = [
            "Senior Regulatory Consultant",
            "Professional Peer Mentor",
            "State Board Policy Auditor",
            "Specialized Compliance Expert"
        ]

    def fetch_records(self, target_slug=None, limit=5, force=False):
        """Fetch records that need processing."""
        query = self.supabase.table("grich_keywords_pool").select("*")
        
        if target_slug:
            # High priority single target
            res = query.eq("slug", target_slug).execute()
        elif force:
            # Overwrite mode: fetch even if article exists (for fixing bad content)
            res = query.eq("is_refined", True).limit(limit).execute()
        else:
            # Normal mode: fetch only empty refined records
            res = query.eq("is_refined", True).is_("final_article", "null").limit(limit).execute()
            
        data = res.data if res.data else []
        print(f"DEBUG: Retrieved {len(data)} records to process.")
        return data

    def fetch_internal_links(self, current_slug, limit=3):
        """Skill 3: Internal Link Silo - Fetch related articles."""
        try:
            # Randomly fetch 3 OTHER records that have articles
            res = self.supabase.table("grich_keywords_pool") \
                .select("slug,keyword") \
                .neq("slug", current_slug) \
                .not_.is_("final_article", "null") \
                .limit(10) \
                .execute()
            
            candidates = res.data if res.data else []
            if not candidates: return []
            
            return random.sample(candidates, min(len(candidates), limit))
        except Exception as e:
            print(f"   ⚠️ Link Fetch Error: {e}")
            return []

    def compose(self, record):
        """Core logic: Compose HTML article from JSON data."""
        keyword = record['keyword']
        data = record['content_json'] # Refined data source
        persona = random.choice(self.personas)
        
        # Skill 3: Contextual Data Injection
        # We ensure NO "Unknown" by using Estimated Ranges if needed (AI instruction)
        
        prompt = f"""
        ROLE: You are a {persona} writing a definitive 2026 Licensing Guide.
        TOPIC: {keyword}
        DATA (Single Source of Truth): {json.dumps(data)}

        INSTRUCTIONS:
        1. Write a 1200+ word deep-dive article in pure HTML.
        2. STRUCTURE:
           <h1>{keyword}: 2026 Official Compliance Audit</h1>
           <p>(Intro: Hook the reader with 2026 urgency)</p>
           <h2>1. Fee Breakdown (The "Hidden" Costs)</h2>
           ... (Detailed analysis of fees, steps, requirements) ...
           [BUY_BUTTON_PLACEHOLDER]
           <h2>3. Application SOP (Standard Operating Procedure)</h2>
           ... (Step-by-step guide) ...
           <h2>4. Authoritative Conclusion</h2>
           ...
           [BUY_BUTTON_PLACEHOLDER]

        3. RULES:
           - NO Markdown (no ##, no **). Use <h2>, <strong>, <table> directly.
           - NO "Unknown" or "Not Mentioned". If data is missing in JSON, provide a realistic "Estimated Range" based on 2026 US Industry Standards and label it "Estimated".
           - Tone: Professional, authoritative, yet urgent.
        """

        try:
            print(f"   🧠 Generating content for: {keyword}...")
            start_time = time.time()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a specialized Compliance HTML Writer. Return ONLY raw HTML code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3, # Low temp for factual accuracy
                timeout=120
            )
            raw_content = response.choices[0].message.content
            duration = time.time() - start_time
            print(f"   ⚡ Generation took {duration:.2f}s")
            
            # --- POST-PROCESSING PIPELINE ---

            # 1. Clean wrapper
            content = raw_content.replace("```html", "").replace("```", "").strip()

            # 2. Force Markdown -> HTML Conversion (Safety Net)
            # Even if AI is told to output HTML, we pass it through markdown lib just in case it slipped some MD
            # But wait, if it output actual HTML tags, markdown lib might escape them? 
            # Better strategy: If it looks like Markdown (has ##), convert it. If it looks like HTML, keep it.
            if "<h2>" not in content and "##" in content:
                 print("   ⚠️ Content looks like Markdown. Converting...")
                 content = markdown.markdown(content)
            
            # 3. Inject Internal Links (Skill 3)
            links = self.fetch_internal_links(record['slug'])
            if links:
                link_html = '<div style="background:#f8fafc;padding:25px;border-radius:12px;margin-top:40px;">'
                link_html += '<h3 style="margin-top:0;color:#334155;">Explore Related Pathways</h3><ul style="margin:0;padding-left:20px;">'
                for l in links:
                    link_html += f'<li style="margin-bottom:10px;"><a href="/p/{l["slug"]}" style="color:#f97316;font-weight:600;">{l["keyword"]}</a></li>'
                link_html += '</ul></div>'
                
                # Append to end
                content += link_html

            return content

        except Exception as e:
            print(f"   ❌ AI Generation Error: {e}")
            return None

    def run(self, target_slug=None, batch_size=5, force=False):
        records = self.fetch_records(target_slug, batch_size, force)
        if not records:
            print("💤 No tasks found.")
            return

        print(f"🚀 Starting Matrix Composer (Batch: {len(records)})...")
        for r in records:
            article = self.compose(r)
            if article and len(article) > 500:
                self.supabase.table("grich_keywords_pool").update({
                    "final_article": article,
                    "updated_at": "now()"
                }).eq("id", r['id']).execute()
                print(f"   ✅ Saved: {r['slug']} ({len(article)} chars)")
            else:
                print(f"   ⚠️ Failed to generate valid article for {r['slug']}")
            
            # Respect Rate Limits
            time.sleep(2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", help="Target specific slug")
    parser.add_argument("--batch", type=int, default=1, help="Batch size")
    parser.add_argument("--force", action="store_true", help="Force overwrite")
    args = parser.parse_args()
    
    app = MatrixComposer()
    app.run(target_slug=args.slug, batch_size=args.batch, force=args.force)
