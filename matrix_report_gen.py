"""SoEasyHub v2 Report Generator - Production Grade"""
from openai import OpenAI
import os

# Read from environment variables
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "MISSING_KEY_PLEASE_SET_ENV")
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

# 2. 核心数据 (这些就是脚本三提炼出的"金砖")
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
    
    # 这里是让报告不再"糙"的关键：复杂的 Prompt 指令
    system_prompt = """你是一位专业的执照审计师，擅长撰写合规性报告。请基于提供的数据生成一份专业的审计报告，需要：

1. 严格的事实导向：所有陈述必须基于提供的数据
2. 专业的语言风格：使用正式的审计报告用语
3. 清晰的结构化：分点列举关键发现
4. 合规性强调：突出法律法规要求
5. 风险提示：包含必要的免责声明"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"请基于以下数据生成专业审计报告:\n\n{refined_facts}"}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        report = response.choices[0].message.content
        
        # 保存报告
        with open("professional_audit_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
        print("✅ 报告已生成并保存")
        return report
        
    except Exception as e:
        print(f"❌ 报告生成失败: {str(e)}")
        return None

if __name__ == "__main__":
    generate_professional_report()