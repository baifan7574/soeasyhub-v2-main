import os
import json
from datetime import datetime
from supabase import create_client, Client

# ================= Matrix Deployer v2.2 (The Fleet Admiral) =================
BASE_URL = "https://soeasyhub.com"

class MatrixDeployer:
    def __init__(self):
        self.config = self._load_config()
        self.supabase: Client = create_client(self.config['url'], self.config['key'])
        # Detection of root directory for sitemap saving
        if os.path.exists("template.html"):
            self.project_root = "."
        elif os.path.exists("soeasyhub-v2/template.html"):
            self.project_root = "soeasyhub-v2"
        else:
            self.project_root = "."

    def _load_config(self):
        config = {
            'url': os.getenv('SUPABASE_URL'),
            'key': os.getenv('SUPABASE_KEY')
        }
        if config['url'] and config['key']: return config

        token_paths = ['.agent/Token..txt', '../.agent/Token..txt', '../../.agent/Token..txt']
        for tp in token_paths:
            if os.path.exists(tp):
                with open(tp, 'r', encoding='utf-8') as f:
                    for line in f:
                        if "Project URL:" in line: config['url'] = line.split("URL:")[1].strip()
                        if "Secret keys:" in line: config['key'] = line.split("keys:")[1].strip()
                return config
        return config

    def generate_sitemap(self):
        print("🌐 [SEO Matrix] Building sitemap.xml...")
        res = self.supabase.table("grich_keywords_pool").select("slug").not_.is_("final_article", "null").execute()
        slugs = [r['slug'] for r in res.data]

        now = datetime.now().strftime("%Y-%m-%d")
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        xml += f'  <url><loc>{BASE_URL}/</loc><lastmod>{now}</lastmod><priority>1.0</priority></url>\n'
        for slug in slugs:
            xml += f'  <url><loc>{BASE_URL}/p/{slug}</loc><lastmod>{now}</lastmod><priority>0.8</priority></url>\n'
        xml += '</urlset>'
        
        sitemap_path = os.path.join(self.project_root, "sitemap.xml")
        with open(sitemap_path, "w", encoding="utf-8") as f:
            f.write(xml)
        print(f"   ✅ [SEO] {len(slugs)} URLs added to sitemap at {sitemap_path}")

if __name__ == "__main__":
    MatrixDeployer().generate_sitemap()
