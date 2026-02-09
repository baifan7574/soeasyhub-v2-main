import pdfplumber
from openai import OpenAI
import os

# 1. 自动化工厂配置 (已填入你的 DeepSeek API Key)
API_KEY = "sk-79789aa8ba3d433d8458eb0f6db3a462"
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

def extract_text_from_pdf(file_path):
    """机器动作：从 PDF 中粉碎并提取文字内容"""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                content = page.extract_text()
                if content:
                    text += content + "\n"
        return text
    except Exception as e:
        return f"读取文件 {file_path} 失败: {str(e)}"

def refinery_ai_process(raw_content):
    """机器动作：调用 DeepSeek 进行深度精炼，生成付费报告内容"""
    # 这里的 Prompt 经过优化，专门针对你的 pSEO 商业模式设计
    prompt = f"""
    你现在是德州执照准入专家（Texas Licensing Expert）。
    请基于以下提供的 1305 法案和申请表原始文本，为一名准备跨州执业的电工生成一份【深度避坑报告】。
    
    要求：
    1. 提取【金钱成本】：明确申请费及其不可退还性。
    2. 提取【硬性门槛】：必须满足的互认条件（例如：必须过考、持证满一年等）。
    3. 挖掘【隐形坑点】：文档中提到的会导致申请被终止或拒绝的细节（如：12个月时限、证明信要求）。
    4. 提供【行动清单】：用户接下来的第一步、第二步、第三步。
    5. 标注【出处】：每一条关键结论后面请括号标注来源于哪个文档。

    --- 原始文档开始 ---
    {raw_content}
    --- 原始文档结束 ---
    """
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个严谨的商业情报分析师，擅长将枯燥法律文档转化为高价值执行方案。"},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI 精炼失败: {str(e)}"

if __name__ == "__main__":
    # 定义工厂的原材料
    raw_files = [
        "OC.1305.pdf", 
        "Master-Electrician-License-by-Reciprocity-Application-ELC-LIC-008-E.pdf"
    ]
    
    print("--- 🏭 全球职业准入 pSEO 自动化工厂：精炼机启动 ---")
    
    combined_text = ""
    for file_name in raw_files:
        if os.path.exists(file_name):
            print(f"📦 正在读取原材料: {file_name}...")
            combined_text += f"\n[文件源: {file_name}]\n"
            combined_text += extract_text_from_pdf(file_name)
        else:
            print(f"❌ 错误：未找到文件 {file_name}，请检查文件名或路径。")

    if combined_text:
        print("🧠 正在连接 DeepSeek 进行 AI 精炼提纯...")
        product_report = refinery_ai_process(combined_text)
        
        # 将生成的“精华”存入 Markdown，这就是你未来的产品数据库
        output_file = "Texas_Electrician_Refined_Report.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(product_report)
        
        print(f"\n✅ 精炼完成！")
        print(f"📄 你的第一份商业产品已生成：{output_file}")
        print("--- 厂长，请检查报告内容。如果你满意，这就是我们要填入 pSEO 网页的黄金数据 ---")
    else:
        print("📭 没有提取到任何有效文字，请检查 PDF 是否为扫描件（图片）。")