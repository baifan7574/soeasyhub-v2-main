from openai import OpenAI
import os

# 1. 配置你的 DeepSeek API (使用你之前提供的 Key)
client = OpenAI(api_key="sk-79789aa8ba3d433d8458eb0f6db3a462", base_url="https://api.deepseek.com")

# 2. 核心数据 (这些就是脚本三提炼出的“金砖”)
refined_facts = {
    "target_state": "Texas",
    "fee": "$45 (Non-refundable)", #
    "time_limit": "12 months to complete", #
    "law": "Texas Occupations Code Chapter 1305", #
    "no_ssn_path": "Occupational License Application Claiming To Have No Social Security Number form", #
    "reciprocity_rule": "Must have passed an equivalent exam and held license for 1 year" #
}

def generate_professional_report():
    print("🧠 正在调用 DeepSeek 进行专家级内容撰写...")
    
    # 这里是让报告不再“糙”的关键：复杂的 Prompt 指令
    prompt = f"""
    你现在是一名专注美国职业准入的【资深法律顾问】。请基于以下真实政策数据，撰写一份交付给付费客户的《德州电工互认审计报告》。
    
    【核心事实数据】：
    - 目标州: {refined_facts['target_state']}
    - 法律依据: {refined_facts['law']}
    - 费用: {refined_facts['fee']}
    - 有效期: {refined_facts['time_limit']}
    - 核心要求: {refined_facts['reciprocity_rule']}
    - 关键表格: {refined_facts['no_ssn_path']}

    【撰写要求】：
    1. 风格：极度专业、严谨、客观，体现出 $29.9 的咨询价值。
    2. 结构：包含【风险对齐】、【执行路径图】、【材料准备清单】。
    3. 深度：不要只列出数字，要解释这些数字背后的后果（例如：如果交错费用会损失钱财）。
    4. 格式：使用清晰的 Markdown 标题和列表。
    """

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一名严谨的美国执照法律顾问。"},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )
    
    report_content = response.choices[0].message.content
    
    # 保存结果
    with open("Premium_Texas_Electrician_Report.md", "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print(f"✅ 专家级报告已生成：Premium_Texas_Electrician_Report.md")

if __name__ == "__main__":
    generate_professional_report()