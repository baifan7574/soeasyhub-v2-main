import os
import json
import time
import argparse
from openai import OpenAI
from supabase import create_client, Client

# PDF Rendering Imports
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

class MatrixReporter:
    def __init__(self):
        url = os.environ.get('SUPABASE_URL')
        key = os.environ.get('SUPABASE_KEY')
        groq_key = os.environ.get('GROQ_API_KEY')
        if not url or not key or not groq_key:
            raise ValueError("Missing SUPABASE or GROQ environment variables.")
        
        self.supabase: Client = create_client(url, key)
        self.client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
        self.model = "llama-3.3-70b-versatile"
        print("🛡️ [Lead Auditor Engaged]")

    def fetch_refined_data(self, slug):
        res = self.supabase.table("grich_keywords_pool").select("*").eq("slug", slug).execute()
        return res.data[0] if res.data else None

    def fetch_unreported_records(self, limit=10):
        res = self.supabase.table("grich_keywords_pool")\
            .select("*")\
            .eq("is_refined", True)\
            .is_("pdf_url", "null")\
            .limit(limit)\
            .execute()
        return res.data

    def generate_audit_logic(self, record, retries=3):
        keyword, data = record['keyword'], record['content_json']
        prompt = f"Summarize licensing logic for {keyword} into bullet points: {json.dumps(data)}"
        for attempt in range(retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": "Professional Auditor."},
                              {"role": "user", "content": prompt}],
                    timeout=30
                )
                return response.choices[0].message.content
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "rate" in err_str.lower():
                    wait = 15 * (attempt + 1)
                    print(f"   ⏳ Rate limited. Waiting {wait}s... (attempt {attempt+1}/{retries})")
                    time.sleep(wait)
                elif attempt < retries - 1:
                    print(f"   ⚠️ AI Error (attempt {attempt+1}/{retries}): {e}. Retrying in 5s...")
                    time.sleep(5)
                else:
                    print(f"   ❌ AI Generation Failed after {retries} attempts: {e}")
                    return None

    def upload_to_cloud(self, local_path, slug, record_id=None, retries=2):
        file_name = f"Audit_{slug}.pdf"
        for attempt in range(retries):
            try:
                with open(local_path, "rb") as f:
                    self.supabase.storage.from_("audit-reports").upload(
                        file_name, f, {"content-type": "application/pdf", "x-upsert": "true"}
                    )
                print(f"   ✨ [Cloud] Uploaded as {file_name}")
                sb_url = os.environ.get('SUPABASE_URL', '')
                cloud_url = f"{sb_url}/storage/v1/object/public/audit-reports/{file_name}"
                if record_id:
                    self.supabase.table("grich_keywords_pool").update({"pdf_url": cloud_url}).eq("id", record_id).execute()
                    print(f"   📝 [DB] pdf_url saved.")
                return True
            except Exception as e:
                if attempt < retries - 1:
                    print(f"   ⚠️ Upload Error (attempt {attempt+1}/{retries}): {e}. Retrying in 3s...")
                    time.sleep(3)
                else:
                    print(f"   ❌ Cloud Upload Failed after {retries} attempts: {e}")
                    return False

    def render_pdf(self, audit_text, slug, keyword, record_id=None):
        filename = f"tmp_Audit_{slug}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = [Paragraph(f"2026 OFFICIAL AUDIT: {keyword}", styles['Title']), Paragraph(audit_text, styles['Normal'])]
        doc.build(story)
        
        success = self.upload_to_cloud(filename, slug, record_id)
        if os.path.exists(filename):
            os.remove(filename)
        return success

    def process_all(self, limit=5):
        records = self.fetch_unreported_records(limit)
        total = len(records)
        if not records:
            print("💤 No unreported records found. All PDFs may already be generated!")
            return
        
        print(f"\n📋 Found {total} records without PDF. Starting batch generation...\n")
        
        success_count = 0
        fail_count = 0
        
        for i, r in enumerate(records, 1):
            print(f"[{i}/{total}] 📄 Auditing: {r['slug']}")
            logic = self.generate_audit_logic(r)
            if logic:
                ok = self.render_pdf(logic, r['slug'], r['keyword'], r['id'])
                if ok:
                    success_count += 1
                else:
                    fail_count += 1
            else:
                fail_count += 1
            
            # Rate limit protection: pause every 5 records
            if i % 5 == 0 and i < total:
                print(f"   ⏸️ Batch checkpoint: {success_count} success, {fail_count} failed. Pausing 3s...")
                time.sleep(3)
        
        print(f"\n{'='*50}")
        print(f"📊 BATCH COMPLETE: {success_count}/{total} PDFs generated successfully.")
        print(f"   ✅ Success: {success_count}")
        print(f"   ❌ Failed: {fail_count}")
        print(f"{'='*50}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", help="Single slug")
    parser.add_argument("--batch", type=int, default=1, help="Batch size")
    args = parser.parse_args()
    reporter = MatrixReporter()
    if args.slug:
        r = reporter.fetch_refined_data(args.slug)
        if r:
            logic = reporter.generate_audit_logic(r)
            if logic: reporter.render_pdf(logic, r['slug'], r['keyword'], r['id'])
    else:
        reporter.process_all(limit=args.batch)

