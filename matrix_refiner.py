import os
import json
import time
import pdfplumber
import requests
from openai import OpenAI
from supabase import create_client, Client
import argparse
from matrix_config import config

# ================= Configuration =================
STORAGE_BUCKET = "raw-handbooks"

class MatrixRefiner:
    def __init__(self, batch_size=30):
        self.batch_size = batch_size
        
        if not config.is_valid():
             raise ValueError("Configuration incomplete. Check Token..txt or environment variables.")

        self.supabase: Client = create_client(config.supabase_url, config.supabase_key)
        
        self.zhipu_key = config.zhipu_key
        self.ds_key = config.deepseek_key
        
        # Priority: DeepSeek (Cost effective) > Zhipu (Vision capable)
        # If you need Vision, swap the order or use a flag.
        if self.ds_key:
            # Prefer DeepSeek for text refining to save cost/avoid Zhipu balance issues
            self.client = OpenAI(api_key=self.ds_key, base_url="https://api.deepseek.com")
            self.model = "deepseek-chat"
            config.log("[Info] Refinery Online (DeepSeek Engine).")
        elif self.zhipu_key:
            # Fallback to ZhipuAI
            self.client = OpenAI(api_key=self.zhipu_key, base_url="https://open.bigmodel.cn/api/paas/v4/")
            self.model = "glm-4v-flash"
            config.log("[Info] Refinery Online (GLM-4V-Flash Engine).")
        else:
            raise ValueError("[Error] Missing API Key. Please set DEEPSEEK_API_KEY or ZHIPU_API_KEY.")

    def fetch_unrefined_records(self):
        """Fetch records that are downloaded but have no content_json"""
        config.log("[Info] Fetching unrefined records...")
        try:
            # Also exclude failed refinements to avoid dead loop
            # Check if is_refined is False? Schema has is_refined default false.
            # We filter: is_downloaded=True AND content_json is NULL
            res = self.supabase.table("grich_keywords_pool")\
                .select("*")\
                .eq("is_downloaded", True)\
                .is_("content_json", "null")\
                .limit(self.batch_size)\
                .execute()
            return res.data
        except Exception as e:
            config.log(f"[Error] Fetch Error: {e}", level="ERROR")
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
            config.log(f"   [Error] Download failed: {e}", level="ERROR")
            return None

    def extract_high_value_text(self, pdf_path):
        keywords = ["fee", "cost", "price", "requirement", "checklist", "application", "process", "reciprocity", "endorsement", "exam", "grade"]
        
        extracted_text = ""
        total_pages = 0
        read_pages = 0
        
        try:
            # Add timeout mechanism or safe open? pdfplumber doesn't have native timeout.
            # We can just be careful.
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                # LIMIT PAGES to avoid huge processing
                max_pages_to_scan = 50 
                
                for i, page in enumerate(pdf.pages):
                    if i >= max_pages_to_scan:
                        config.log(f"   [Warn] Reached max page scan limit ({max_pages_to_scan}). Stopping extraction.", level="WARN")
                        break
                        
                    try:
                         # Sometimes extract_text hangs on complex layout
                        text = page.extract_text() or ""
                    except Exception as e:
                        config.log(f"   [Warn] Page {i+1} extraction failed: {e}", level="WARN")
                        continue
                        
                    text_lower = text.lower()
                    if i < 3 or any(k in text_lower for k in keywords):
                        extracted_text += f"\n--- Page {i+1} ---\n{text}"
                        read_pages += 1
                    
            config.log(f"   [Info] Extracted {read_pages}/{total_pages} pages.")
            if not extracted_text.strip():
                 return None
            return extracted_text
        except Exception as e:
            config.log(f"   [Error] PDF Extraction Error: {e}", level="ERROR")
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
                stream=False,
                timeout=300
            )
            content = response.choices[0].message.content
            if "```json" in content:
                content = content.replace("```json", "").replace("```", "")
            return content.strip()
        except Exception as e:
            error_msg = str(e)
            if "1113" in error_msg or "balance" in error_msg.lower():
                config.log(f"   [Error] Insufficient Balance for {self.model}. Please check your account.", level="ERROR")
                if self.model == "glm-4v" and self.ds_key:
                    config.log("   [Info] Attempting fallback to DeepSeek...")
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
                        config.log(f"   [Error] Fallback failed: {fallback_e}", level="ERROR")
            
            config.log(f"   [Error] AI API Error ({self.model}): {e}", level="ERROR")
            return None

    def update_db(self, record_id, json_data):
        try:
            parsed = json.loads(json_data)
            self.supabase.table("grich_keywords_pool").update({
                "content_json": parsed,
                "is_refined": True
            }).eq("id", record_id).execute()
            config.log("   [Success] Database Updated.")
        except json.JSONDecodeError:
            config.log("   [Error] Failed to parse JSON.", level="ERROR")
            # Mark as refined but with error so we don't loop
            self.supabase.table("grich_keywords_pool").update({
                "content_json": {"error": "json_parse_failed"},
                "is_refined": True
            }).eq("id", record_id).execute()

    def mark_failed_refine(self, record_id, reason):
        # Update content_json with error to stop loop
        config.log(f"   [Warn] Marking as failed: {reason}", level="WARN")
        self.supabase.table("grich_keywords_pool").update({
            "content_json": {"error": reason},
            "is_refined": True # Mark refined so we don't retry same bad file
        }).eq("id", record_id).execute()

    def run_batch(self):
        records = self.fetch_unrefined_records()
        if not records:
            config.log("[Info] No unrefined records found.")
            return

        config.log(f"[Info] Processing {len(records)} records...")
        failures = []
        
        for record in records:
            slug = record['slug']
            rid = record['id']
            config.log(f"\n[Working] Refining: {slug}")
            
            # 1. Download
            pdf_path = self.download_pdf(slug)
            if not pdf_path: 
                self.mark_failed_refine(rid, "storage_download_failed")
                failures.append(slug)
                continue
            
            # 2. Extract
            text = self.extract_high_value_text(pdf_path)
            if not text:
                config.log("   [Warn] Empty text or scan.", level="WARN")
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
            config.log("\n[Warn] Failure Report (Saved to DB as errors):", level="WARN")
            for f in failures:
                config.log(f"   - {f}", level="WARN")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Matrix Refiner")
    parser.add_argument("--batch", type=int, default=30, help="Batch size to process.")
    args = parser.parse_args()
    
    refiner = MatrixRefiner(batch_size=args.batch)
    refiner.run_batch()
