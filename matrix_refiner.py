import os
import json
import time
import pdfplumber
import requests
from openai import OpenAI
from supabase import create_client, Client

# ================= Matrix Refiner (Script 3) =================
STORAGE_BUCKET = "raw-handbooks"

class MatrixRefiner:
    def __init__(self):
        self.config = self._load_config()
        self.supabase: Client = create_client(self.config['url'], self.config['key'])
        
        self.ds_key = self.config.get('ds_key')
        if not self.ds_key:
            raise ValueError("❌ Missing DeepSeek API Key (DSAPI or DEEPSEEK_API_KEY).")
            
        self.client = OpenAI(api_key=self.ds_key, base_url="https://api.deepseek.com")
        print("🏭 Refinery Online.")

    def _load_config(self):
        config = {
            'url': os.getenv('SUPABASE_URL'),
            'key': os.getenv('SUPABASE_KEY'),
            'ds_key': os.getenv('DEEPSEEK_API_KEY') or os.getenv('DSAPI')
        }
        
        if config['url'] and config['key'] and config['ds_key']:
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
                    print(f"✅ Loaded from {tp}")
                    return config
                except: pass
        return config

    def fetch_unrefined_records(self):
        print("📊 Fetching unrefined records...")
        try:
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
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                read_pages = 0
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    text_lower = text.lower()
                    if i < 3 or any(k in text_lower for k in keywords):
                        extracted_text += f"\n--- Page {i+1} ---\n{text}"
                        read_pages += 1
                print(f"   📄 Extracted {read_pages}/{total_pages} pages.")
            return extracted_text if extracted_text.strip() else None
        except Exception as e:
            print(f"   ❌ PDF Extraction Error: {e}")
            return None

    def refine_with_deepseek(self, raw_text):
        prompt = """
        Extract structured data into JSON:
        - "application_fee": (string)
        - "processing_time": (string)
        - "requirements": (array)
        - "steps": (array)
        - "evidence": (string, quote)
        
        Strict JSON only.
        --- Content ---
        """ + raw_text[:20000]
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "JSON assistant."},
                    {"role": "user", "content": prompt},
                ]
            )
            content = response.choices[0].message.content
            if "```json" in content: content = content.replace("```json", "").replace("```", "")
            return content.strip()
        except Exception as e:
            print(f"   ❌ API Error: {e}")
            return None

    def update_db(self, record_id, json_data):
        try:
            parsed = json.loads(json_data)
            self.supabase.table("grich_keywords_pool").update({
                "content_json": parsed,
                "is_refined": True
            }).eq("id", record_id).execute()
            print("   ✅ DB Updated.")
        except:
            self.supabase.table("grich_keywords_pool").update({
                "content_json": {"error": "parse_failed"},
                "is_refined": True
            }).eq("id", record_id).execute()

    def run_batch(self):
        records = self.fetch_unrefined_records()
        if not records: return print("💤 No work.")
        for record in records:
            rid, slug = record['id'], record['slug']
            print(f"🔨 Refining: {slug}")
            pdf_path = self.download_pdf(slug)
            if pdf_path:
                text = self.extract_high_value_text(pdf_path)
                if text:
                    res = self.refine_with_deepseek(text)
                    if res: self.update_db(rid, res)
                os.remove(pdf_path)

if __name__ == "__main__":
    MatrixRefiner().run_batch()
