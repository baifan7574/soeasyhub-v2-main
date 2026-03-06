import os
import sys

# Ensure we can import matrix_config from current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from matrix_config import config
from supabase import create_client

def main():
    print("=== 精确盘点 (Audit Correct Count) ===")
    
    if not config.is_valid():
        print("[Error] Supabase configuration missing.")
        return

    try:
        sb = create_client(config.supabase_url, config.supabase_key)
        
        print(f"Connected to Supabase: {config.supabase_url[:20]}...")
        
        # 1. Total Count (Exact)
        print("\n正在进行精确统计 (count='exact', head=True)...")
        
        # Total records
        total_res = sb.table("grich_keywords_pool").select("id", count="exact", head=True).execute()
        total_count = total_res.count
        print(f"Total Records (数据库总记录数): {total_count}")
        
        # 2. Breakdown by Status
        print("\n--- 状态细分 (Breakdown) ---")
        
        # Downloaded
        downloaded_res = sb.table("grich_keywords_pool").select("id", count="exact", head=True).eq("is_downloaded", True).execute()
        print(f"   已下载 (is_downloaded=true): {downloaded_res.count}")
        
        # Content JSON
        content_res = sb.table("grich_keywords_pool").select("id", count="exact", head=True).not_.is_("content_json", "null").execute()
        print(f"   有内容数据 (content_json exists): {content_res.count}")
        
        # Final Article
        article_res = sb.table("grich_keywords_pool").select("id", count="exact", head=True).not_.is_("final_article", "null").execute()
        print(f"   已生成文章 (final_article exists): {article_res.count}")
        
        # PDF URL
        pdf_res = sb.table("grich_keywords_pool").select("id", count="exact", head=True).not_.is_("pdf_url", "null").execute()
        print(f"   已生成 PDF (pdf_url exists): {pdf_res.count}")

        print("\n--- 生产流水线状态 (Pipeline Status) ---")
        
        # Ready for Composer (Downloaded, No PDF, Has Content)
        ready_composer_res = sb.table("grich_keywords_pool").select("id", count="exact", head=True)\
            .eq("is_downloaded", True)\
            .is_("pdf_url", "null")\
            .not_.is_("content_json", "null")\
            .execute()
        print(f"   待生成文章 (Ready for Composer): {ready_composer_res.count}")

        # Ready for PDF (Downloaded, No PDF, Has Article)
        ready_pdf_res = sb.table("grich_keywords_pool").select("id", count="exact", head=True)\
            .eq("is_downloaded", True)\
            .is_("pdf_url", "null")\
            .not_.is_("final_article", "null")\
            .execute()
        print(f"   待生成 PDF (Ready for PDF Gen): {ready_pdf_res.count}")
        
        print("\n=== 统计完成 ===")
        
    except Exception as e:
        print(f"[Fatal Error] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
