import os
from datetime import datetime
from supabase import create_client, Client

BASE_URL = "https://soeasyhub.com"

class MatrixDeployer:
    def __init__(self):
        url = os.environ.get('SUPABASE_URL')
        key = os.environ.get('SUPABASE_KEY')
        if not url or not key:
            raise ValueError("Missing SUPABASE environment variables.")
        self.supabase: Client = create_client(url, key)
        
        # Detection of root directory for sitemap saving
        self.project_root = "." if os.path.exists("template.html") else "soeasyhub-v2"

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
        print(f"   ✅ [SEO] {len(slugs)} URLs added to sitemap.")

if __name__ == "__main__":
    MatrixDeployer().generate_sitemap()
