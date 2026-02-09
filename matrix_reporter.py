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
        # We fetch records that are refined but might not have been audited yet.
        # Since we removed pdf_url column, we just filter by is_refined=True
        # We can use a different marker or just run specifically for one slug.
        res = self.supabase.table("grich_keywords_pool")\
            .select("*")\
            .eq("is_refined", True)\
            .limit(limit)\
            .execute()
        return res.data

    def generate_audit_logic(self, record):
        keyword, data = record['keyword'], record['content_json']
        prompt = f"Summarize licensing logic for {keyword} into bullet points: {json.dumps(data)}"
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": "Professional Auditor."},
                          {"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"   ❌ AI Generation Failed: {e}")
            return None

    def upload_to_cloud(self, local_path, slug):
        # The worker.js expects: Audit_{slug}.pdf
        file_name = f"Audit_{slug}.pdf"
        try:
            with open(local_path, "rb") as f:
                self.supabase.storage.from_("audit-reports").upload(
                    file_name, f, {"content-type": "application/pdf", "x-upsert": "true"}
                )
            print(f"   ✨ [Cloud] Uploaded as {file_name}")
            return True
        except Exception as e:
            print(f"   ❌ Cloud Upload Failed: {e}")
            return False

    def render_pdf(self, audit_text, slug, keyword):
        filename = f"tmp_Audit_{slug}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = [Paragraph(f"2026 OFFICIAL AUDIT: {keyword}", styles['Title']), Paragraph(audit_text, styles['Normal'])]
        doc.build(story)
        
        success = self.upload_to_cloud(filename, slug)
        if os.path.exists(filename):
            os.remove(filename)
        return success

    def process_all(self, limit=5):
        records = self.fetch_unreported_records(limit)
        if not records: return print("💤 No work.")
        for r in records:
            print(f"📄 Auditing: {r['slug']}")
            logic = self.generate_audit_logic(r)
            if logic: self.render_pdf(logic, r['slug'], r['keyword'])

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
            if logic: reporter.render_pdf(logic, r['slug'], r['keyword'])
    else:
        reporter.process_all(limit=args.batch)
