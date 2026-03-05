import os
import json
import time
import argparse
import random
from openai import OpenAI
from supabase import create_client, Client
import markdown
from matrix_config import config

# ================= Matrix Composer (The Composer) - HOLY BIBLE EDITION v2.1 =================
# Status: Final Revision (Aligns with SKILL.md)
# Features: HTML-Only Output, Persona Rotation, Anti-N/A Logic, Double CTA, Internal Siloing.
# ============================================================================================

class MatrixComposer:
    def __init__(self):
        if not config.is_valid():
             raise ValueError("Configuration incomplete. Check Token..txt or environment variables.")

        self.supabase: Client = create_client(config.supabase_url, config.supabase_key)
        
        # Persona Pool for Randomization (Anti-De-indexing)
        self.personas = [
            "Senior Regulatory Consultant (25 years experience)",
            "Professional Peer & Active Licensing Advocate",
            "State Board Policy Auditor",
            "Specialized Compliance Immigration Expert",
            "Independent Licensing Industry Observer"
        ]
        
        self.groq_key = config.groq_key
        self.ds_key = config.deepseek_key

        if self.groq_key:
             config.log("[Monetization Master] Engine: Groq Llama-3.3")
             self.client = OpenAI(api_key=self.groq_key, base_url="https://api.groq.com/openai/v1", max_retries=3)
             self.model = "llama-3.3-70b-versatile"
        elif self.ds_key:
             config.log("[Content Heavyweight] Engine: DeepSeek-V3")
             self.client = OpenAI(api_key=self.ds_key, base_url="https://api.deepseek.com", max_retries=3)
             self.model = "deepseek-chat"
        else:
            raise ValueError("[Error] Missing API Keys.")

    def fetch_records(self, target_slug=None, limit=5, force=False):
        query = self.supabase.table("grich_keywords_pool").select("*")
        if target_slug:
            res = query.eq("slug", target_slug).execute()
        else:
            if force:
                # 强制模式：覆盖已有文章，仍然需要 content_json
                res = query.not_.is_("content_json", "null")\
                           .order("id", desc=True)\
                           .limit(limit).execute()
            else:
                # 遵循 SKILL.md 逻辑：选择已精炼且未生成文章的记录
                # 1. 已精炼（is_refined = True）或 content_json NOT NULL
                # 2. 文章为空（final_article IS NULL）
                # 3. 按 id 升序（先进先出）
                # 4. 限制数量
                try:
                    # 先尝试使用 is_refined 字段
                    res = query.eq("is_refined", True)\
                               .is_("final_article", "null")\
                               .order("id", desc=False)\
                               .limit(limit).execute()
                    if len(res.data) == 0:
                        # 回退：content_json NOT NULL 且 final_article IS NULL
                        res = query.not_.is_("content_json", "null")\
                                   .is_("final_article", "null")\
                                   .order("id", desc=False)\
                                   .limit(limit).execute()
                except Exception:
                    # 如果字段不存在，使用 content_json NOT NULL 且 final_article IS NULL
                    res = query.not_.is_("content_json", "null")\
                               .is_("final_article", "null")\
                               .order("id", desc=False)\
                               .limit(limit).execute()
        return res.data

    def compose_article(self, record):
        keyword = record['keyword']
        data = record['content_json']
        current_persona = random.choice(self.personas)
        
        # Hard Data Extraction
        fee = data.get('application_fee', '')
        time_est = data.get('processing_time', '')
        reqs = "\n".join([f"- {r}" for r in data.get('requirements', [])]) if isinstance(data.get('requirements'), list) else str(data.get('requirements', ''))
        steps = "\n".join([f"{i+1}. {s}" for i, s in enumerate(data.get('steps', []))]) if isinstance(data.get('steps'), list) else str(data.get('steps', ''))
        evidence = data.get('evidence', 'Official state guidelines')

        # CTA Component (HTML Only)
        BUY_BUTTON = f"""
        <div class="monetization-box" style="background: #fff7ed; border: 2px dashed #f97316; padding: 35px; border-radius: 12px; margin: 45px 0; text-align: center;">
            <h3 style="color: #c2410c; margin-top: 0;"> Skip the Labyrinth: Get Your 2026 {keyword} Fast-Track Bible</h3>
            <p style="color: #7c2d12;">Includes supplement templates, back-door contact lists, and our proven 21-point rejection-proof checklist.</p>
            <a href="{{{{PDF_LINK}}}}" style="display: inline-block; background: #f97316; color: white; padding: 18px 45px; border-radius: 8px; font-weight: bold; text-decoration: none; font-size: 1.2rem; box-shadow: 0 10px 15px -3px rgba(249, 115, 22, 0.3);">Unlock Audit Report ($29.9)</a>
            <p style="font-size: 0.8rem; color: #9a3412; margin-top: 15px;"> 100% Policy-Aligned | Instant Access | Save Months of Uncertainty</p>
        </div>
        """

        prompt = f"""
        PERSONA: {current_persona}.
        TOPIC: {keyword}.
        LANGUAGE: Strictly English.
        GOAL: High-Conversion SEO Landing Page (1200+ words).
        FORMAT: Output STRICTLY in clean HTML. No Markdown symbols (no ##, no **, no |).

        --- DATA ARSENAL (Single Source of Truth) ---
        - Fee: "{fee if fee else 'USE 2026 INDUSTRY ESTIMATE'}"
        - Timeline: "{time_est if time_est else 'USE 2026 INDUSTRY ESTIMATE'}"
        - Requirements: {reqs}
        - Steps: {steps}
        - Evidence Original: "{evidence}"

        --- HOLY BIBLE RULES ---
        1. HTML ONLY: Use <h1>, <h2>, <p>, <ul>, <li>, <strong>, and <table> for all content. 
        2. NO "UNKNOWN": Under no circumstances use "Not Mentioned" or "Unknown". If a field is missing, use your "2026 Industry Benchmark Simulator" to give a realistic range (e.g., "$150-$450") and add the disclaimer: "Based on 2026 industry average benchmarks for similar state boards."
        3. DOUBLE CTA: You MUST insert the provided HTML CTA block exactly twice: once at the 30% mark (after the financial pain point) and once before the conclusion.
        4. DATA ANCHORING: Boldly highlight the fee using <strong>.
        5. INTERNAL SILO: At the very end, generate an "Explore Related Pathways" section with 2-3 HTML links like <a href="/p/related-slug">Title</a>.
        6. NO CODE BLOCKS: Do not wrap the HTML in ```html blocks. Just provide the raw HTML string.

        --- HTML CTA COMPONENT (INSERT TWICE) ---
        {BUY_BUTTON}

        --- STRUCTURE ---
        - <h1> Headline
        - Executive Comparison <table>
        - Financial Stakes (Discussion of Fee)
        - Eligibility Labyrinth
        - Operational Roadmap (Step-by-Step)
        - Common Point of Rejections (The "Ghost" Requirements)
        - Industry Disclaimer Case Study
        - Conclusion & Final CTA
        """

        try:
            config.log(f"   [Persona: {current_persona}] Writing {keyword} (HTML Injection)...")
            
            engines = []
            if self.groq_key: engines.append(('Groq', self.groq_key, "https://api.groq.com/openai/v1", "llama-3.3-70b-versatile"))
            if self.ds_key: engines.append(('DeepSeek', self.ds_key, "https://api.deepseek.com", "deepseek-chat"))
            
            # 增加检查，防止没有可用引擎
            if not engines:
                config.log("   [Error] No available AI engines configured.", level="ERROR")
                return None
            
            random.shuffle(engines)
            
            for attempt in range(2): 
                for engine_name, api_key, base_url, model_name in engines:
                    try:
                        temp_client = OpenAI(api_key=api_key, base_url=base_url)
                        response = temp_client.chat.completions.create(
                            model=model_name,
                            messages=[
                                {"role": "system", "content": "You are a world-class SEO technical writer and compliance expert. You output raw HTML only. No Markdown."},
                                {"role": "user", "content": prompt},
                            ],
                            timeout=300
                        )
                        content = response.choices[0].message.content
                        # Clean potential code blocks
                        if "```html" in content: content = content.replace("```html", "").replace("```", "")
                        elif "```" in content: content = content.replace("```", "")
                        return content.strip()
                    except Exception as engine_err:
                        config.log(f"   [Error] {engine_name} Error: {engine_err}", level="ERROR")
                        continue
                time.sleep(10)
            
            return None
        except Exception as e:
            config.log(f"   [Error] Critical Composer Error: {e}", level="ERROR")
            return None

    def _ensure_html(self, content):
        """强制将任何Markdown内容转换为HTML，防止前端显示##乱码"""
        if not content:
            return content
        
        # 如果内容已经主要是HTML（有标签），但可能包含Markdown片段
        # 使用markdown库进行转换
        try:
            # markdown库可以安全地处理纯HTML和混合内容
            html_content = markdown.markdown(content, extensions=['extra'])
            
            # 检查转换是否有效（不是空或仅包含空白）
            if html_content and html_content.strip():
                # 确保转换后的HTML没有残留的Markdown标记
                if "## " in html_content or "**" in html_content or "|---" in html_content:
                    # 二次清理：基本替换作为后备
                    html_content = html_content.replace("## ", "<h2>").replace("**", "<strong>")
                
                config.log(f"   [Info] Markdown->HTML transformation: {len(content)} -> {len(html_content)} chars")
                return html_content
        except Exception as e:
            config.log(f"   [Warn] Markdown transformation failed: {e}, using original content", level="WARN")
        
        # 后备方案：基本清理
        cleaned = content
        if "## " in cleaned:
            cleaned = cleaned.replace("## ", "<h2>")
        if "**" in cleaned:
            cleaned = cleaned.replace("**", "<strong>")
        if "|---" in cleaned:
            # 移除Markdown表格标记
            lines = cleaned.split('\n')
            cleaned = '\n'.join([line for line in lines if not line.strip().startswith('|---')])
        
        return cleaned

    def run(self, target_slug=None, batch_size=5, force=False):
        records = self.fetch_records(target_slug, limit=batch_size, force=force)
        if not records:
            config.log("[Info] No tasks.")
            return

        if force:
            config.log("[Info] [Force Mode] Will overwrite existing final_article entries.")
        
        config.log(f"[Info] [Batch Injection] Starting {len(records)} articles...")
        
        # --- STATE MANAGEMENT START ---
        state_dir = os.path.join(".agent", "state")
        os.makedirs(state_dir, exist_ok=True)
        state_file = os.path.join(state_dir, "composer_state.json")
        
        processed_slugs = []
        if os.path.exists(state_file) and not target_slug and not force:
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    processed_slugs = state.get("processed_today", [])
                    config.log(f"[State] Loaded {len(processed_slugs)} processed slugs from artifact.")
            except Exception as e:
                config.log(f"[Warn] Failed to load state: {e}", level="WARN")
        # --- STATE MANAGEMENT END ---

        for record in records:
            slug = record['slug']
            if slug in processed_slugs and not target_slug and not force:
                 config.log(f"[Info] [Skip] {slug} already processed in current batch (Artifact state).")
                 continue
                 
            config.log(f"\n[Working] {slug}")
            article = self.compose_article(record)
            if article:
                # 强制HTML转换：确保没有任何Markdown残留
                article = self._ensure_html(article)
                
                # Retry logic for Supabase update
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        self.supabase.table("grich_keywords_pool").update({
                            "final_article": article
                        }).eq("id", record['id']).execute()
                        config.log(f"   [Inject Success] Chars: {len(article)}")
                        
                        # Update state
                        processed_slugs.append(slug)
                        with open(state_file, 'w') as f:
                             json.dump({"processed_today": processed_slugs, "last_updated": time.time()}, f)
                        break # Success, exit retry loop
                    except Exception as e:
                        config.log(f"   [Error] Supabase update failed (Attempt {attempt+1}/{max_retries}): {e}", level="ERROR")
                        if attempt < max_retries - 1:
                            time.sleep(5)
                        else:
                            config.log(f"   [Error] Final failure updating {slug}", level="ERROR")
            else:
                config.log(f"   [Warn] [Skipped] Failed to compose {slug}", level="WARN")
            time.sleep(2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", help="Regenerate one record")
    parser.add_argument("--batch", type=int, default=5, help="Number of records to process")
    parser.add_argument('--force', action='store_true', help='Force overwrite existing content')
    args = parser.parse_args()
    
    composer = MatrixComposer()
    composer.run(target_slug=args.slug, batch_size=args.batch, force=args.force)
