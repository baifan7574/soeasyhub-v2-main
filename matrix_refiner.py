import os
import json
import time
import pdfplumber
from openai import OpenAI
from supabase import create_client, Client

STORAGE_BUCKET = "raw-handbooks"

class MatrixRefiner:
    def __init__(self):
        url = os.environ.get('SUPABASE_URL')
        key = os.environ.get('SUPABASE_KEY')
        ds_key = os.environ.get('DEEPSEEK_API_KEY')
        if not url or not key or not ds_key:
            raise ValueError("Missing Environment Variables (SUPABASE or DEEPSEEK).")
        
        self.supabase: Client = create_client(url, key)
        self.client = OpenAI(api_key=ds_key, base_url="https://api.deepseek.com")
        print("🏭 Refinery Online.")

    def fetch_unrefined_records(self):
        try:
            res = self.supabase.table("grich_keywords_pool")\
                .select("*")\
                .eq("is_downloaded", True)\
                .is_("content_json", "null")\
                .limit(10)\
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

    def extract_text(self, pdf_path):
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages[:5]: # Extract first 5 pages for efficiency
                    text += page.extract_text() or ""
                return text if text.strip() else None
        except: return None

    def refine(self, text):
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "system", "content": "Extract application_fee, processing_time, requirements, steps, evidence into JSON."},
                          {"role": "user", "content": text}]
            )
            content = response.choices[0].message.content
            if "```json" in content: content = content.replace("```json", "").replace("```", "")
            return content.strip()
        except: return None

    def run(self):
        records = self.fetch_unrefined_records()
        for r in records:
            print(f"🔨 Refining: {r['slug']}")
            path = self.download_pdf(r['slug'])
            if path:
                text = self.extract_text(path)
                if text:
                    res = self.refine(text)
                    if res:
                        self.supabase.table("grich_keywords_pool").update({
                            "content_json": json.loads(res),
                            "is_refined": True
                        }).eq("id", r['id']).execute()
                        print("   ✅ Refinement Success.")
                os.remove(path)

if __name__ == "__main__":
    MatrixRefiner().run()
