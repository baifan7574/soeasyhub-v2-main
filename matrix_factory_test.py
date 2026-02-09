import pandas as pd
import os
import re

# 1. 配置路径
CSV_FILE = 'heavy_mine_20260113.csv'
REPORT_FILE = 'Texas_Electrician_Refined_Report.md'
OUTPUT_DIR = 'dist_pages' # 生成的网页会放在这个文件夹

# 2. 读取精炼后的数据 (模拟脚本3提取的数据字段)
# 注意：为了演示效果，我直接从你刚才生成的报告中提取了核心字段
refined_data = {
    "fee": "$45",
    "refund_policy": "Non-refundable",
    "time_limit": "12 months",
    "law_ref": "Texas Occupations Code Chapter 1305",
    "key_doc": "Letter of Certification (Official)",
    "pay_link": "https://payhip.com/b/your-product-id" # 这里填你的 Payhip 链接
}

# 3. 准备 HTML 模板 (脚本4的核心)
html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{title}}</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: auto; padding: 20px; color: #333; }
        .header { background: #002d72; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
        .content { border: 1px solid #ddd; padding: 30px; border-radius: 0 0 8px 8px; background: #fff; }
        .data-point { background: #f9f9f9; border-left: 5px solid #002d72; padding: 15px; margin: 20px 0; }
        .warning { color: #b91c1c; font-weight: bold; border: 2px dashed #b91c1c; padding: 15px; text-align: center; }
        .cta-box { text-align: center; margin-top: 40px; background: #f0f7ff; padding: 30px; border-radius: 8px; }
        .btn { background: #ff4d4d; color: white; padding: 15px 30px; text-decoration: none; font-weight: bold; border-radius: 5px; font-size: 1.2em; display: inline-block; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{heading}}</h1>
    </div>
    <div class="content">
        <p>If you are planning to transfer your electrical license to Texas, here is the critical policy information you need to know.</p>
        
        <div class="data-point">
            <strong>Application Fee:</strong> {{fee}} ({{refund_policy}})<br>
            <strong>Legal Reference:</strong> {{law_ref}}<br>
            <strong>Timeframe:</strong> You must complete all requirements within {{time_limit}}.
        </div>

        <h3>Critical Requirement:</h3>
        <p>You must provide an official <strong>{{key_doc}}</strong> from your original licensing board. Without this specific document, your application will be rejected.</p>

        <div class="warning">
            ⚠️ WARNING: Do not submit your application if you did not pass an exam for your current license. Fees are NOT refundable.
        </div>

        <div class="cta-box">
            <h2>Need the Full Step-by-Step Guide?</h2>
            <p>Download our 30-page "Texas Electrician Reciprocity Roadmap" including document templates and SSN waiver instructions.</p>
            <a href="{{pay_link}}" class="btn">Get the Full Report ($29.9)</a>
        </div>
    </div>
    <footer style="text-align:center; font-size: 12px; color: #999; margin-top: 20px;">
        &copy; 2026 Global License SEO Factory. Data sourced from TDLR Official Handbooks.
    </footer>
</body>
</html>
"""

def run_mixer():
    if not os.path.exists(CSV_FILE):
        print(f"找不到关键词文件: {CSV_FILE}")
        return

    # 创建输出文件夹
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 读取关键词
    df = pd.read_csv(CSV_FILE)
    # 取前 10 个词进行本地测试
    keywords = df['Long_Tail_Keywords'].head(10).tolist()

    print(f"--- 🏭 脚本 4：本地网页生成测试启动 ---")
    
    for word in keywords:
        # 生成网页文件名 (把空格换成横杠)
        filename = re.sub(r'[^a-z0-9]', '-', word.lower()) + ".html"
        filepath = os.path.join(OUTPUT_DIR, filename)

        # 填充模板
        content = html_template.replace("{{title}}", word)
        content = content.replace("{{heading}}", word.title())
        content = content.replace("{{fee}}", refined_data["fee"])
        content = content.replace("{{refund_policy}}", refined_data["refund_policy"])
        content = content.replace("{{law_ref}}", refined_data["law_ref"])
        content = content.replace("{{time_limit}}", refined_data["time_limit"])
        content = content.replace("{{key_doc}}", refined_data["key_doc"])
        content = content.replace("{{pay_link}}", refined_data["pay_link"])

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"✅ 已生成本地测试页: {filepath}")

    print(f"\n🎉 测试完成！请打开文件夹 '{OUTPUT_DIR}'，双击里面的任何一个 .html 文件查看效果。")

if __name__ == "__main__":
    run_mixer()