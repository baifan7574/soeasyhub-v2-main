import os
import subprocess
import json
from datetime import datetime
from supabase import create_client, Client

# ================= Matrix Deployer v2.0 (The Fleet Admiral) =================
# Mission: Orchestrate soeasyhub.com 2.0 Deployment
# Logic: DB Sync -> Sitemap -> PDF Batching -> Git Push -> Cloudflare
# ===========================================================================

TOKEN_FILE = os.path.join(".agent", "Token..txt")  # Fallback for local development
PROJECT_DIR = os.environ.get("PROJECT_DIR", "soeasyhub-v2")  # Allow override via env
BASE_URL = "https://soeasyhub.com"

# Environment variable names for cloud deployment
ENV_SUPABASE_URL = "SUPABASE_URL"
ENV_SUPABASE_KEY = "SUPABASE_KEY"

class MatrixDeployer:
    def __init__(self):
        self.config = self._load_config()
        self.supabase: Client = create_client(self.config['url'], self.config['key'])

    def _load_config(self):
        config = {}
        
        # Priority 1: Read from environment variables (cloud deployment)
        supabase_url = os.environ.get(ENV_SUPABASE_URL)
        supabase_key = os.environ.get(ENV_SUPABASE_KEY)
        
        if supabase_url and supabase_key:
            config['url'] = supabase_url
            config['key'] = supabase_key
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
                    config['url'] = line.split("URL:")[1].strip()
                if "Secret keys:" in line:
                    config['key'] = line.split("keys:")[1].strip()
        
        if 'url' not in config or 'key' not in config:
            raise ValueError("Configuration incomplete. Check Token..txt or environment variables.")
        
        print("⚠️  Config loaded from local Token file (development mode).")
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
        
        with open(os.path.join(PROJECT_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
            f.write(xml)
        print(f"   ✅ [SEO] {len(slugs)} URLs added to sitemap.")

    def run_pre_production_pdffills(self):
        """Invoke Script 5 to ensure all 131 articles have local PDF samples for safety."""
        print("📦 [Asset Matrix] Preparing 131 physical PDF reports...")
        # Since we already generated many, this will just ensure completeness
        # We'll call matrix_reporter in batch mode
        repo_cmd = "python matrix_reporter.py --batch 131"
        try:
            result = subprocess.run(repo_cmd, shell=True, check=True, capture_output=True, text=True)
            print(f"   ✅ [Asset] Physical reports batch generated. Output: {len(result.stdout)} chars")
            if result.stderr:
                print(f"   ⚠️  Warnings: {result.stderr[:200]}...")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ [Asset] PDF generation failed with exit code {e.returncode}")
            print(f"   ❌ Stderr: {e.stderr[:500] if e.stderr else 'No error output'}")
            raise
        except FileNotFoundError:
            print("   ❌ [Asset] matrix_reporter.py not found or Python not available.")
            raise
        except Exception as e:
            print(f"   ❌ [Asset] Unexpected error: {e}")
            raise

    def deploy(self):
        print("🚀 [Fleet Admiral] Initiating Deployment Sequence...")
        self.generate_sitemap()
        # self.run_pre_production_pdffills() # Already basically done or can be run separately
        
        print("\n📝 Committing to GitHub...")
        try:
            # Check if PROJECT_DIR exists
            if not os.path.exists(PROJECT_DIR):
                raise FileNotFoundError(f"Project directory '{PROJECT_DIR}' does not exist.")
            
            # Git add with proper error handling
            add_cmd = f"cd {PROJECT_DIR} && git add ."
            result_add = subprocess.run(add_cmd, shell=True, check=True, capture_output=True, text=True)
            print(f"   ✅ Git add successful: {len(result_add.stdout.strip())} lines output")
            
            # Git commit with proper error handling
            commit_message = f"Matrix Auto-Update: {datetime.now().strftime('%H:%M:%S')}"
            commit_cmd = f"cd {PROJECT_DIR} && git commit -m '{commit_message}'"
            result_commit = subprocess.run(commit_cmd, shell=True, check=True, capture_output=True, text=True)
            print(f"   ✅ Git commit successful: {len(result_commit.stdout.strip())} lines output")
            
            # Optionally push (commented out for safety)
            # push_cmd = f"cd {PROJECT_DIR} && git push origin main"
            # result_push = subprocess.run(push_cmd, shell=True, check=True, capture_output=True, text=True)
            # print(f"   ✅ Git push successful: {len(result_push.stdout.strip())} lines output")
            
            print("   ✅ [Version Control] Git operations completed successfully.")
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Git command failed with exit code {e.returncode}")
            print(f"   ❌ Stderr: {e.stderr[:500] if e.stderr else 'No error output'}")
            print(f"   ❌ Stdout: {e.stdout[:500] if e.stdout else 'No output'}")
            raise
        except FileNotFoundError as e:
            print(f"   ❌ {e}")
            raise
        except Exception as e:
            print(f"   ❌ Unexpected error during Git operations: {e}")
            raise

if __name__ == "__main__":
    deployer = MatrixDeployer()
    deployer.deploy()
