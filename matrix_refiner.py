import os
import json
import time
import pdfplumber
import requests
from openai import OpenAI
from supabase import create_client, Client

# ================= Configuration =================
TOKEN_FILE = os.path.join(".agent", "Token..txt")  # Fallback for local development
STORAGE_BUCKET = "raw-handbooks"

# Environment variable names for cloud deployment
ENV_SUPABASE_URL = "SUPABASE_URL"
ENV_SUPABASE_KEY = "SUPABASE_KEY"
ENV_DEEPSEEK_API_KEY = "DEEPSEEK_API_KEY"
ENV_GROQ_API_KEY = "GROQ_API_KEY"
ENV_ZHIPU_API_KEY = "ZHIPU_API_KEY"

class MatrixRefiner:
    def __init__(self):
        self.config = self._load_config()
        self.supabase: Client = create_client(self.config['url'], self.config['key'])
        
        self.zhipu_key = self.config.get('zhipu_key')
        self.ds_key = self.config.get('ds_key')
        
        
        # Priority: DeepSeek (Cost effective) > Zhipu (Vision capable)
        # If you need Vision, swap the order or use a flag.
        if self.ds_key:
            # Prefer DeepSeek for text refining to save cost/avoid Zhipu balance issues
            self.client = OpenAI(api_key=self.ds_key, base_url="https://api.deepseek.com")
            self.model = "deepseek-chat"
            print("🏭 Refinery Online (DeepSeek Engine).")
        elif self.zhipu_key:
            # Fallback to ZhipuAI
            self.client = OpenAI(api_key=self.zhipu_key, base_url="https://open.bigmodel.cn/api/paas/v4/")
            self.model = "glm-4v-flash"
            print("🏭 Refinery Online (GLM-4V-Flash Engine).")
        else:
            raise ValueError("❌ Missing API Key. Please set DEEPSEEK_API_KEY or ZHIPU_API_KEY.")

    def _load_config(self):
        config = {}
        
        # Priority 1: Read from environment variables (cloud deployment)
        supabase_url = os.environ.get(ENV_SUPABASE_URL)
        supabase_key = os.environ.get(ENV_SUPABASE_KEY)
        deepseek_key = os.environ.get(ENV_DEEPSEEK_API_KEY)
        zhipu_key = os.environ.get(ENV_ZHIPU_API_KEY)
        
        if supabase_url and supabase_key:
            config['url'] = supabase_url
            config['key'] = supabase_key
            if zhipu_key:
                config['zhipu_key'] = zhipu_key
            elif deepseek_key:
                config['ds_key'] = deepseek_key
            print("✅ Config loaded from environment variables.")
            return config
        
        # Priority 2: Fallback to local Token file (development)
        token_path = None
        if os.path.exists(TOKEN_FILE):
            token_path = TOKEN_FILE
        else:
            # Try alternative relative path
            alt_path = os.path.join("..", ".agent", "Token..txt")
            if os.path.exists(alt_path):
                token_path = alt_path
        
        if not token_path:
            raise FileNotFoundError(
                f"Critical: {TOKEN_FILE} not found and environment variables {ENV_SUPABASE_URL}/{ENV_SUPABASE_KEY} not set."
            )
        
        with open(token_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                if "Project URL:" in line:
                    config['url'] = line.split("Project URL:")[1].strip()
                if "Secret keys:" in line:
                    config['key'] = line.split("Secret keys:")[1].strip()
                if "ZHIPUAPI:" in line:
                    config['zhipu_key'] = line.split("ZHIPUAPI:")[1].strip()
                if "DSAPI:" in line:
                    config['ds_key'] = line.split("DSAPI:")[1].strip()
        
        if 'url' not in config or 'key' not in config:
            raise ValueError("Configuration incomplete. Check Token..txt or environment variables.")
        
        print("⚠️  Config loaded from local Token file (development mode).")
        return config

    def fetch_unrefined_records(self):
        """Fetch records that are downloaded but have no content_json"""
        print("📊 Fetching unrefined records...")
        try:
            # Also exclude failed refinements to avoid dead loop
            # Check if is_refined is False? Schema has is_refined default false.
            # We filter: is_downloaded=True AND content_json is NULL
            res = self.supabase.table("grich_keywords_pool")\
                .select("*")\
                .eq("is_downloaded", True)\
                .is_("content_json", "null")\
                .limit(30)\
                .execute()
            return res.data
        except Exception as e:
            print(f"❌ Fetch Error: {e}")
            return []

    def download_pdf(self, slug):
        file_name = f"{slug}.pdf"
        local_path = f"tmp_{file_name}"
        try:
            data = self.supabase.storage.from_(STORAGE_BUCKET).download(file_name)
            with open(local_path, "wb") as f:
                f.write(data)
            return local_path
        except Exception as e:
            print(f"   ❌ Download failed: {e}")
            return None

    def extract_high_value_text(self, pdf_path):
        keywords = ["fee", "cost", "price", "requirement", "checklist", "application", "process", "reciprocity", "endorsement", "exam", "grade"]
        
        extracted_text = ""
        total_pages = 0
        read_pages = 0
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    text_lower = text.lower()
                    if i < 3 or any(k in text_lower for k in keywords):
                        extracted_text += f"\n--- Page {i+1} ---\n{text}"
                        read_pages += 1
                    
            print(f"   📄 Extracted {read_pages}/{total_pages} pages.")
            if not extracted_text.strip():
                 return None
            return extracted_text
        except Exception as e:
            print(f"   ❌ PDF Extraction Error: {e}")
            return None

    def refine_with_ai(self, raw_text):
        prompt = """
        You are a Professional License Compliance Analyst.
        Extract structured data from the text.
        Output strictly in JSON format with these keys:
        - "application_fee": (string, specific dollar amount)
        - "processing_time": (string)
        - "requirements": (array of strings)
        - "steps": (array of strings)
        - "evidence": (string, direct quote supporting the fee/logic)
        
        Output only JSON.
        
        --- Content ---
        """ + raw_text[:20000]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that outputs strict JSON."},
                    {"role": "user", "content": prompt},
                ],
                stream=False
            )
            content = response.choices[0].message.content
            if "```json" in content:
                content = content.replace("```json", "").replace("```", "")
            return content.strip()
        except Exception as e:
            error_msg = str(e)
            if "1113" in error_msg or "balance" in error_msg.lower():
                print(f"   ❌ Insufficient Balance for {self.model}. Please check your account.")
                if self.model == "glm-4v" and self.ds_key:
                    print("   🔄 Attempting fallback to DeepSeek...")
                    try:
                        fallback_client = OpenAI(api_key=self.ds_key, base_url="https://api.deepseek.com")
                        response = fallback_client.chat.completions.create(
                            model="deepseek-chat",
                            messages=[
                                {"role": "system", "content": "You are a helpful assistant that outputs strict JSON."},
                                {"role": "user", "content": prompt},
                            ],
                            stream=False
                        )
                        content = response.choices[0].message.content
                        if "```json" in content:
                            content = content.replace("```json", "").replace("```", "")
                        return content.strip()
                    except Exception as fallback_e:
                        print(f"   ❌ Fallback failed: {fallback_e}")
            
            print(f"   ❌ AI API Error ({self.model}): {e}")
            return None

    def update_db(self, record_id, json_data):
        try:
            parsed = json.loads(json_data)
            self.supabase.table("grich_keywords_pool").update({
                "content_json": parsed,
                "is_refined": True
            }).eq("id", record_id).execute()
            print("   ✅ Database Updated.")
        except json.JSONDecodeError:
            print("   ❌ Failed to parse JSON.")
            # Mark as refined but with error so we don't loop
            self.supabase.table("grich_keywords_pool").update({
                "content_json": {"error": "json_parse_failed"},
                "is_refined": True
            }).eq("id", record_id).execute()

    def mark_failed_refine(self, record_id, reason):
        # Update content_json with error to stop loop
        print(f"   ⚠️ Marking as failed: {reason}")
        self.supabase.table("grich_keywords_pool").update({
            "content_json": {"error": reason},
            "is_refined": True # Mark refined so we don't retry same bad file
        }).eq("id", record_id).execute()

    def run_batch(self):
        records = self.fetch_unrefined_records()
        if not records:
            print("💤 No unrefined records found.")
            return

        print(f"🚀 Processing {len(records)} records...")
        failures = []
        
        for record in records:
            slug = record['slug']
            rid = record['id']
            print(f"\n🔨 Refining: {slug}")
            
            # 1. Download
            pdf_path = self.download_pdf(slug)
            if not pdf_path: 
                self.mark_failed_refine(rid, "storage_download_failed")
                failures.append(slug)
                continue
            
            # 2. Extract
            text = self.extract_high_value_text(pdf_path)
            if not text:
                print("   ⚠️ Empty text or scan.")
                self.mark_failed_refine(rid, "empty_text_or_scan")
                failures.append(slug)
                if os.path.exists(pdf_path): os.remove(pdf_path)
                continue
            
            # 3. Refine
            json_result = self.refine_with_ai(text)
            
            # 4. Update
            if json_result:
                self.update_db(rid, json_result)
            else:
                self.mark_failed_refine(rid, "ai_api_failed")
                failures.append(slug)
            
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            
            time.sleep(1)
            
        if failures:
            print("\n⚠️ Failure Report (Saved to DB as errors):")
            for f in failures:
                print(f"   - {f}")

if __name__ == "__main__":
    refiner = MatrixRefiner()
    refiner.run_batch()
