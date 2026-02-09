import os
import json
import time
import argparse
import random
import re
from datetime import datetime
from openai import OpenAI
from supabase import create_client, Client

# PDF Rendering Imports
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.units import inch

# ================= Matrix Reporter (Script 5) =================

class MatrixReporter:
    def __init__(self):
        self.config = self._load_config()
        self.supabase: Client = create_client(self.config['url'], self.config['key'])
        
        self.groq_key = self.config.get('groq_key')
        if not self.groq_key:
            raise ValueError("❌ Missing GROQ_API_KEY.")
            
        self.client = OpenAI(api_key=self.groq_key, base_url="https://api.groq.com/openai/v1")
        self.model = "llama-3.3-70b-versatile"
        print("🛡️ [Lead Auditor Engaged]")

    def _load_config(self):
        config = {
            'url': os.getenv('SUPABASE_URL'),
            'key': os.getenv('SUPABASE_KEY'),
            'groq_key': os.getenv('GROQ_API_KEY')
        }
        if config['url'] and config['key'] and config['groq_key']: return config

        token_paths = ['.agent/Token..txt', '../.agent/Token..txt', '../../.agent/Token..txt']
        for tp in token_paths:
            if os.path.exists(tp):
                with open(tp, 'r', encoding='utf-8') as f:
                    for line in f:
                        if "Project URL:" in line: config['url'] = line.split("URL:")[1].strip()
                        if "Secret keys:" in line: config['key'] = line.split("keys:")[1].strip()
                        if "groqapi" in line: config['groq_key'] = line.split(":")[1].strip()
                return config
        return config

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

    def generate_audit_logic(self, record):
        keyword, data = record['keyword'], record['content_json']
        prompt = f"""AUDIT LOGIC FOR {keyword}: {json.dumps(data)}
        Return strict JSON only for PDF report generation."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": "Professional Auditor. JSON output."},
                          {"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"   ❌ AI Generation Failed: {e}")
            return None

    def upload_to_cloud(self, local_path, slug):
        file_name = os.path.basename(local_path)
        try:
            with open(local_path, "rb") as f:
                self.supabase.storage.from_("audit-reports").upload(
                    file_name, f, {"content-type": "application/pdf", "x-upsert": "true"}
                )
            return f"{self.config['url']}/storage/v1/object/public/audit-reports/{file_name}"
        except Exception as e:
            print(f"   ❌ Cloud Upload Failed: {e}")
            return None

    def render_pdf(self, report_data, slug, keyword, record_id):
        filename = f"Audit_{slug}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = [Paragraph(f"AUDIT REPORT: {keyword}", styles['Title']), Paragraph(json.dumps(report_data), styles['Normal'])]
        doc.build(story)
        
        url = self.upload_to_cloud(filename, slug)
        if url:
            self.supabase.table("grich_keywords_pool").update({"pdf_url": url}).eq("id", record_id).execute()
            print(f"   ✨ [Success] {url}")
            os.remove(filename)

    def process_all(self, limit=5):
        records = self.fetch_unreported_records(limit)
        if not records: return print("💤 No work.")
        for r in records:
            logic = self.generate_audit_logic(r)
            if logic: self.render_pdf(logic, r['slug'], r['keyword'], r['id'])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", help="Single slug")
    parser.add_argument("--batch", type=int, default=5, help="Batch size")
    args = parser.parse_args()
    reporter = MatrixReporter()
    if args.slug:
        r = reporter.fetch_refined_data(args.slug)
        if r:
            logic = reporter.generate_audit_logic(r)
            if logic: reporter.render_pdf(logic, r['slug'], r['keyword'], r['id'])
    else:
        reporter.process_all(limit=args.batch)
