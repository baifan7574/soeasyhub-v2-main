"""SoEasyHub v2 Matrix Refinery - PDF Content Processor"""
import pdfplumber
from openai import OpenAI
import os

# Read from environment variables
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "MISSING_KEY_PLEASE_SET_ENV")
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

def refine_content(text):
    """机器动作：使用 AI 提炼和优化内容"""
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的内容提炼专家。请对输入的文本进行以下处理：\n1. 提取关键信息和重要数据\n2. 去除冗余和重复内容\n3. 优化语言表达\n4. 保持专业性和准确性"},
                {"role": "user", "content": f"请对以下内容进行提炼和优化:\n\n{text}"}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"内容提炼失败: {str(e)}"

def main():
    """主程序入口"""
    # 示例：处理当前目录下的所有 PDF 文件
    for file in os.listdir('.'):
        if file.endswith('.pdf'):
            print(f"\n处理文件: {file}")
            # 1. 提取文本
            text = extract_text_from_pdf(file)
            if text.startswith('读取文件'):
                print(text)
                continue
            
            # 2. 提炼内容
            print("正在提炼内容...")
            refined = refine_content(text)
            if refined.startswith('内容提炼失败'):
                print(refined)
                continue
                
            # 3. 保存结果
            output_file = f"refined_{file[:-4]}.txt"
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(refined)
                print(f"结果已保存到: {output_file}")
            except Exception as e:
                print(f"保存失败: {str(e)}")

if __name__ == "__main__":
    main()