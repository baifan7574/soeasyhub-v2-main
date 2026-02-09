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

# ================= Matrix Reporter (The Lead Auditor) - PRODUCTION GRADE =================
# Mission: Automatic Batch Generation of Premium PDF Audit Reports.
# Standards: Holy Bible SKILL.md v2.0 (Legal, Financial, SOP, Insider Insights).

TOKEN_FILE = os.path.join(".agent", "Token..txt")

class MatrixReporter:
    def __init__(self):
        self.config = self._load_config()
        self.supabase: Client = create_client(self.config['url'], self.config['key'])
        
        if self.config.get('groq_key'):
             print("🛡️ [Lead Auditor Engaged] Production Engine: Groq Llama-3.3")
             self.client = OpenAI(api_key=self.config['groq_key'], base_url="https://api.groq.com/openai/v1")
             self.model = "llama-3.3-70b-versatile"
        else:
            raise ValueError("❌ Missing Groq API Key.")

    def _load_config(self):
        config = {
            'url': os.getenv('SUPABASE_URL'),
            'key': os.getenv('SUPABASE_KEY'),
            'groq_key': os.getenv('GROQ_API_KEY')
        }
        
        # Fallback to Token..txt for local dev
        if not config['url'] or not config['key']:
            try:
                with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
                    for line in f:
                        if "Project URL:" in line: config['url'] = line.split("URL:")[1].strip()
                        if "Secret keys:" in line: config['key'] = line.split("keys:")[1].strip()
                        if "groqapi" in line: config['groq_key'] = line.split(":")[1].strip()
            except:
                pass
        
        if not config['url'] or not config['key']:
            raise ValueError("❌ Missing Supabase Credentials (Env or Token file).")
        return config

    def fetch_refined_data(self, slug):
        res = self.supabase.table("grich_keywords_pool").select("*").eq("slug", slug).execute()
        return res.data[0] if res.data else None

    def fetch_unreported_records(self, limit=10):
        # Fetching records that are refined but have NO pdf_url yet (The "Fill the Shelf" logic)
        res = self.supabase.table("grich_keywords_pool")\
            .select("*")\
            .eq("is_refined", True)\
            .is_("pdf_url", "null")\
            .limit(limit)\
            .execute()
        return res.data

    def generate_audit_logic(self, record):
        """Invoke AI to generate the high-value audit content based on DB JSON."""
        keyword = record['keyword']
        data = record['content_json']
        fetch_date = record.get('created_at', str(datetime.now().date()))[:10]
        
        fee = data.get('application_fee', 'Board Discretion Price')
        timeline = data.get('processing_time', 'Estimate Pending')
        evidence = data.get('evidence', 'Review State Regulatory Standards.')
        reqs = "\n".join(data.get('requirements', []))
        steps = "\n".join(data.get('steps', []))

        # We ask AI to return a specific JSON that the PDF engine can consume
        prompt = f"""
        ACT AS: Lead Compliance Auditor.
        MISSION: Generate data for the 2026 OFFICIAL AUDIT for: {keyword}.
        
        --- INPUT DATA ---
        - Base Fee: {fee}
        - Timeline: {timeline}
        - Requirements Raw: {reqs}
        - Evidence Pool: "{evidence}"
        
        --- CONSTRAINTS ---
        1. NO FLUFF.
        2. INSIDER TIPS: Include 1 unique "Hard Truth" about {keyword} (e.g. backlogs, specific phone tips).
        3. RED LINES: Define 3 binary pass/fail disqualifiers.
        4. CITATIONS: Each Red Line must cite UNQIUE evidence text.
        5. OUTPUT FORMAT: Strictly JSON with keys:
           "header_no": (random string)
           "disclaimer_points": (list of 3 points)
           "red_lines": (list of [Factor, Status, Reference])
           "budget_items": (list of [Item, Cost, Risk])
           "insider_insights": (string)
           "fast_track": (string or null)
           "sop": (list of [Phase, Action, Checklist])
        """

        try:
            print(f"   🧠 [Brain Phase] Auditing: {keyword}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional auditor. Output strict JSON only."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"   ❌ AI Generation Failed: {e}")
            return None

    def upload_to_cloud(self, local_path, slug):
        """Upload to audit-reports bucket and return public URL."""
        file_name = os.path.basename(local_path)
        try:
            with open(local_path, "rb") as f:
                self.supabase.storage.from_("audit-reports").upload(
                    file_name, f, {"content-type": "application/pdf", "x-upsert": "true"}
                )
            
            # Construct Public URL
            public_url = f"{self.config['url']}/storage/v1/object/public/audit-reports/{file_name}"
            return public_url
        except Exception as e:
            print(f"   ❌ Cloud Upload Failed: {e}")
            return None

    def render_pdf(self, report_data, slug, keyword, record_id):
        """Convert the AI-generated logic into a physical PDF file and SYNC TO CLOUD."""
        parts = keyword.split()
        state = "State"
        profession = "Profession"
        if len(parts) > 1:
            state = parts[-1].capitalize() if "california" not in keyword.lower() else "California"
            profession = parts[0].capitalize()

        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"Audit_{state}_{profession}_{slug}_{date_str}.pdf"
        filepath = os.path.join(filename)

        doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=50, bottomMargin=40)
        styles = getSampleStyleSheet()
        
        # Add custom styles
        try:
            styles.add(ParagraphStyle(name='AuditHeader', fontName='Helvetica-Bold', fontSize=9, textColor=colors.grey))
            styles.add(ParagraphStyle(name='AuditTitle', fontName='Helvetica-Bold', fontSize=22, leading=28, spaceBefore=25, spaceAfter=20, textColor=colors.navy))
            styles.add(ParagraphStyle(name='AuditSection', fontName='Helvetica-Bold', fontSize=13, spaceBefore=20, spaceAfter=10, textColor=colors.darkblue))
            styles.add(ParagraphStyle(name='AuditBody', fontName='Helvetica', fontSize=10, leading=14))
            styles.add(ParagraphStyle(name='SafeHarbor', fontName='Helvetica-Bold', fontSize=8, textColor=colors.red, borderPadding=10, leading=10))
        except: pass

        story = []

        # Header
        header_text = f"AUDIT #{report_data.get('header_no', 'GR-2026')}  |  STRICTLY CONFIDENTIAL  |  SEALED: {datetime.now().strftime('%Y-%m-%d')}"
        story.append(Paragraph(header_text, styles['AuditHeader']))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.grey, spaceBefore=4, spaceAfter=15))

        # Disclaimer Box
        points = "<br/>• ".join(report_data.get('disclaimer_points', []))
        disclaimer_text = f"<b>LEGAL SAFE HARBOR & DISCLAIMER MATRIX</b><br/>• {points}"
        story.append(Table([[Paragraph(disclaimer_text, styles['AuditBody'])]], colWidths=[6.5*inch], 
                         style=TableStyle([
                             ('BOX', (0,0), (-1,-1), 2, colors.red), 
                             ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke),
                             ('LEFTPADDING', (0,0), (-1,-1), 12),
                             ('RIGHTPADDING', (0,0), (-1,-1), 12),
                             ('TOPPADDING', (0,0), (-1,-1), 10),
                             ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                         ])))
        story.append(Spacer(1, 0.4*inch))

        # Title
        story.append(Paragraph(f"FINAL COMPLIANCE AUDIT: {keyword.upper()}", styles['AuditTitle']))
        story.append(Spacer(1, 0.1*inch))

        # SOP
        story.append(Paragraph(">> 3-MINUTE SOP: FAST-TRACK PATHWAY <<", styles['AuditSection']))
        raw_sop = [["PHASE", "REQUIRED ACTION", "STATUS"]] + report_data.get('sop', [])
        sop_rows = [[Paragraph(str(cell), styles['AuditBody']) for cell in row] for row in raw_sop]
        t_sop = Table(sop_rows, colWidths=[1.2*inch, 3.8*inch, 1.5*inch])
        t_sop.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.darkgreen), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke), ('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('FONTSIZE', (0,0), (-1,-1), 8), ('VALIGN', (0,0), (-1,-1), 'TOP')]))
        story.append(t_sop)

        # Financials
        story.append(Paragraph("COMPREHENSIVE FINANCIAL PROJECTION", styles['AuditSection']))
        raw_fin = [["Expense Item", "Cost", "Risk Level"]] + report_data.get('budget_items', [])
        fin_rows = [[Paragraph(str(cell), styles['AuditBody']) for cell in row] for row in raw_fin]
        t_fin = Table(fin_rows, colWidths=[2.5*inch, 1.5*inch, 2.5*inch])
        t_fin.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.navy), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke), ('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('FONTSIZE', (0,0), (-1,-1), 8), ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey), ('VALIGN', (0,0), (-1,-1), 'TOP')]))
        story.append(t_fin)

        # Insights
        story.append(Paragraph("CRITICAL AUDITOR INSIGHTS", styles['AuditSection']))
        story.append(Paragraph(report_data.get('insider_insights', ''), styles['AuditBody']))

        # Seal
        story.append(Spacer(1, 0.8*inch))
        story.append(HRFlowable(width="30%", thickness=1, color=colors.black, hAlign='RIGHT'))
        seal_text = "<b>OFFICIAL AUDITOR SEAL</b><br/>STAMP-PRO-PRODUCTION<br/>GRICH COMPLIANCE NETWORK"
        story.append(Paragraph(seal_text, ParagraphStyle(name='Seal', alignment=2, fontSize=8, leading=10)))

        doc.build(story)
        print(f"   ✅ [Local] PDF Produced: {filepath}")

        # --- CLOUD SYNC LOGIC ---
        print(f"   ☁️ [Cloud] Syncing {slug} to Supabase Storage...")
        cloud_url = self.upload_to_cloud(filepath, slug)
        if cloud_url:
            self.supabase.table("grich_keywords_pool").update({"pdf_url": cloud_url}).eq("id", record_id).execute()
            print(f"   ✨ [Success] Public Link: {cloud_url}")
            # --- LOCAL CLEANUP ---
            os.remove(filepath)
            print("   🗑️ [Cleanup] Local binary removed.")
        return cloud_url

    def process_all(self, limit=5):
        records = self.fetch_unreported_records(limit)
        if not records:
            print("💤 No refined data ready for audit.")
            return

        print(f"🚀 [Batch Injection] Processing {len(records)} audits...")
        for r in records:
            logic = self.generate_audit_logic(r)
            if logic:
                self.render_pdf(logic, r['slug'], r['keyword'], r['id'])
            time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", help="Process single slug")
    parser.add_argument("--batch", type=int, help="Process batch of N records")
    args = parser.parse_args()

    reporter = MatrixReporter()
    if args.slug:
        record = reporter.fetch_refined_data(args.slug)
        if record:
            logic = reporter.generate_audit_logic(record)
            if logic:
                reporter.render_pdf(logic, record['slug'], record['keyword'], record['id'])
    elif args.batch:
        reporter.process_all(limit=args.batch)
    else:
        # Default test run
        print("💡 No arguments provided. Running default batch of 1.")
        reporter.process_all(limit=1)
