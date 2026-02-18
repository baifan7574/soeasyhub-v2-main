import os
import json
import time
import argparse
import random
from openai import OpenAI
from supabase import create_client, Client
import markdown

# ================= Matrix Composer (The Composer) - HOLY BIBLE EDITION v2.1 =================
# Status: Final Revision (Aligns with SKILL.md)
# Features: HTML-Only Output, Persona Rotation, Anti-N/A Logic, Double CTA, Internal Siloing.
# ============================================================================================

TOKEN_FILE = os.path.join(os.path.dirname(__file__), ".agent", "Token..txt")  # Fallback for local development

# Environment variable names for cloud deployment
ENV_SUPABASE_URL = "SUPABASE_URL"
ENV_SUPABASE_KEY = "SUPABASE_KEY"
ENV_DEEPSEEK_API_KEY = "DEEPSEEK_API_KEY"
ENV_GROQ_API_KEY = "GROQ_API_KEY"
ENV_ZHIPU_API_KEY = "ZHIPU_API_KEY"

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
        
        if self.config.get('zhipu_key'):
            print("✍️ [ZhipuAI Turbo] Engine: GLM-4V")
            self.client = OpenAI(api_key=self.config['zhipu_key'], base_url="https://open.bigmodel.cn/api/paas/v4/", max_retries=3)
            self.model = "glm-4v"
        elif self.config.get('groq_key'):
             print("✍️ [Monetization Master] Engine: Groq Llama-3.3")
             self.client = OpenAI(api_key=self.config['groq_key'], base_url="https://api.groq.com/openai/v1", max_retries=3)
             self.model = "llama-3.3-70b-versatile"
        elif self.config.get('ds_key'):
             print("✍️ [Content Heavyweight] Engine: DeepSeek-V3")
             self.client = OpenAI(api_key=self.config['ds_key'], base_url="https://api.deepseek.com", max_retries=3)
             self.model = "deepseek-chat"
        else:
            raise ValueError("❌ Missing API Keys. Please set ZHIPU_API_KEY, GROQ_API_KEY or DEEPSEEK_API_KEY.")

    def _load_config(self):
        config = {}
        
        # Priority 1: Read from environment variables (cloud deployment)
        supabase_url = os.environ.get(ENV_SUPABASE_URL)
        supabase_key = os.environ.get(ENV_SUPABASE_KEY)
        deepseek_key = os.environ.get(ENV_DEEPSEEK_API_KEY)
        groq_key = os.environ.get(ENV_GROQ_API_KEY)
        zhipu_key = os.environ.get(ENV_ZHIPU_API_KEY)
        
        if supabase_url and supabase_key:
            config['url'] = supabase_url
            config['key'] = supabase_key
            if zhipu_key:
                config['zhipu_key'] = zhipu_key
            elif groq_key:
                config['groq_key'] = groq_key
            elif deepseek_key:
                config['ds_key'] = deepseek_key
            print("✅ Config loaded from environment variables.")
            return config
        
        # Priority 2: Fallback to local Token file (development)
        search_paths = [
            TOKEN_FILE,
            os.path.join(".agent", "Token..txt"),
            os.path.join("..", ".agent", "Token..txt")
        ]
        
        token_path = None
        for p in search_paths:
            if os.path.exists(p):
                token_path = p
                break
        
        if not token_path:
            raise FileNotFoundError(
                f"Critical: Token..txt not found and environment variables {ENV_SUPABASE_URL}/{ENV_SUPABASE_KEY} not set."
            )
        
        with open(token_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                if "Project URL:" in line:
                    config['url'] = line.split("URL:")[1].strip()
                if "Secret keys:" in line:
                    config['key'] = line.split("keys:")[1].strip()
                if "ZHIPUAPI:" in line:
                    config['zhipu_key'] = line.split("ZHIPUAPI:")[1].strip()
                if "DSAPI:" in line:
                    config['ds_key'] = line.split("DSAPI:")[1].strip()
                if "groqapi" in line:
                    config['groq_key'] = line.split(":")[1].strip()
        
        if 'url' not in config or 'key' not in config:
            raise ValueError("Configuration incomplete. Check Token..txt or environment variables.")
        
        print("⚠️  Config loaded from local Token file (development mode).")
        return config

    def fetch_records(self, target_slug=None, limit=5, force=False):
        query = self.supabase.table("grich_keywords_pool").select("*")
        if target_slug:
            res = query.eq("slug", target_slug).execute()
        else:
            if force:
                # When force is True, fetch all records with content_json regardless of final_article status
                res = query.not_.is_("content_json", "null").order("last_mined_at", desc=True).limit(limit).execute()
            else:
                # Fetch records that have refined content but no final article yet
                res = query.not_.is_("content_json", "null").is_("final_article", "null").order("last_mined_at", desc=True).limit(limit).execute()
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
            <h3 style="color: #c2410c; margin-top: 0;">🚀 Skip the Labyrinth: Get Your 2026 {keyword} Fast-Track Bible</h3>
            <p style="color: #7c2d12;">Includes supplement templates, back-door contact lists, and our proven 21-point rejection-proof checklist.</p>
            <a href="{{{{PDF_LINK}}}}" style="display: inline-block; background: #f97316; color: white; padding: 18px 45px; border-radius: 8px; font-weight: bold; text-decoration: none; font-size: 1.2rem; box-shadow: 0 10px 15px -3px rgba(249, 115, 22, 0.3);">Unlock Audit Report ($29.9)</a>
            <p style="font-size: 0.8rem; color: #9a3412; margin-top: 15px;">🔒 100% Policy-Aligned | Instant Access | Save Months of Uncertainty</p>
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
            print(f"   🧠 [Persona: {current_persona}] Writing {keyword} (HTML Injection)...")
            
            engines = []
            if self.config.get('groq_key'): engines.append(('Groq', self.config['groq_key'], "https://api.groq.com/openai/v1", "llama-3.3-70b-versatile"))
            if self.config.get('ds_key'): engines.append(('DeepSeek', self.config['ds_key'], "https://api.deepseek.com", "deepseek-chat"))
            
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
                        print(f"   ❌ {engine_name} Error: {engine_err}")
                        continue
                time.sleep(10)
            
            return None
        except Exception as e:
            print(f"   ❌ Critical Composer Error: {e}")
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
                
                print(f"   🔧 Markdown->HTML转换完成: {len(content)} -> {len(html_content)} 字符")
                return html_content
        except Exception as e:
            print(f"   ⚠️ Markdown转换失败: {e}, 使用原始内容")
        
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
            print("💤 No tasks.")
            return

        print(f"🚀 [Batch Injection] Starting {len(records)} articles...")
        for record in records:
            print(f"\n✍️ [Working] {record['slug']}")
            article = self.compose_article(record)
            if article:
                # 强制HTML转换：确保没有任何Markdown残留
                article = self._ensure_html(article)
                
                self.supabase.table("grich_keywords_pool").update({
                    "final_article": article
                }).eq("id", record['id']).execute()
                print(f"   ✅ [Inject Success] Chars: {len(article)}")
            else:
                print(f"   ⚠️ [Skipped] Failed to compose {record['slug']}")
            time.sleep(2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", help="Regenerate one record")
    parser.add_argument("--batch", type=int, default=5, help="Number of records to process")
    parser.add_argument('--force', action='store_true', help='Force overwrite existing content')
    args = parser.parse_args()
    
    composer = MatrixComposer()
    composer.run(target_slug=args.slug, batch_size=args.batch, force=args.force)
