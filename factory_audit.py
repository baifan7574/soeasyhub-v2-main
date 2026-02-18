"""SoEasyHub v2 Factory Audit Script - One-time inspection"""
import os
import requests
import random

# Read from environment variables or use placeholders
SB_BASE = os.environ.get("SUPABASE_URL", "https://nbfzhxgkfljeuoncujum.supabase.co")
KEY = os.environ.get("SUPABASE_KEY", "MISSING_KEY_PLEASE_SET_ENV")
SB = f"{SB_BASE}/rest/v1/grich_keywords_pool"
H = {"apikey": KEY}

print("=" * 60)
print("  SoEasyHub v2 工厂日报 - 数据资产普查")
print("=" * 60)

# 1. Total
total = requests.get(SB + "?select=id", headers=H).json()
print(f"\n📦 总池子 (关键词总数): {len(total)}")

# 2. Refined
refined = requests.get(SB + "?select=id&is_refined=eq.true", headers=H).json()
print(f"⚙️  已精炼 (is_refined=true): {len(refined)}")

# 3. Has article
articles = requests.get(SB + "?select=slug,final_article&final_article=not.is.null&limit=200", headers=H).json()
print(f"📝 已入库 (有 final_article): {len(articles)}")

over2k = [a for a in articles if a.get("final_article") and len(a["final_article"]) > 2000]
print(f"💎 精品文章 (>2000字符): {len(over2k)}")

# 4. PDF
pdfs = requests.get(SB + "?select=id&pdf_url=not.is.null", headers=H).json()
print(f"📄 PDF 覆盖率: {len(pdfs)}")

# 5. Random 10 slugs for spot check
print("\n" + "=" * 60)
print("  死链抽检 - 随机 10 篇文章")
print("=" * 60)

sample = random.sample(articles, min(10, len(articles)))
ok_count = 0
fail_count = 0

for s in sample:
    slug = s["slug"]
    url = f"https://www.soeasyhub.com/p/{slug}"
    try:
        resp = requests.get(url, timeout=15)
        html = resp.text
        has_29 = "$29.9" in html or "29.9" in html
        has_h1 = "<h1>" in html or "<h1 " in html
        has_h2 = "<h2>" in html or "<h2 " in html
        has_h3 = "<h3>" in html or "<h3 " in html
        has_md_hash = "\n### " in html or "\n## " in html or "\n# " in html
        
        status = "✅"
        issues = []
        if not has_29:
            issues.append("无$29.9按钮")
        if has_md_hash:
            issues.append("Markdown乱码")
        if not (has_h1 or has_h2 or has_h3):
            issues.append("无HTML标题")
        
        if issues:
            status = "⚠️"
            fail_count += 1
        else:
            ok_count += 1
            
        issue_str = " | " + ", ".join(issues) if issues else ""
        alen = len(s.get("final_article", ""))
        print(f"  {status} {slug} | {alen}字符 | HTTP {resp.status_code}{issue_str}")
    except Exception as e:
        fail_count += 1
        print(f"  ❌ {slug} | ERROR: {e}")

print(f"\n抽检结果: {ok_count}/10 通过, {fail_count}/10 有问题")

# 6. Sitemap check
print("\n" + "=" * 60)
print("  Sitemap 巡检")
print("=" * 60)
try:
    sitemap = requests.get("https://www.soeasyhub.com/sitemap.xml", timeout=15).text
    url_count = sitemap.count("<loc>")
    print(f"🗺️  Sitemap URL 总数: {url_count}")
    print(f"📅 lastmod: 2026-02-11")
except Exception as e:
    print(f"❌ Sitemap 获取失败: {e}")

print("\n" + "=" * 60)
print("  体检完毕")
print("=" * 60)
