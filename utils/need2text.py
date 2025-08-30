import os
import json
from typing import Dict, Optional, Union
from jinja2 import Template
from openai import OpenAI
from config.config import API_KEY, BASE_URL, LANGUAGE_MODEL

class Need2Text:
    def __init__(self):
        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=API_KEY,
            base_url=BASE_URL
        )
        
        # 初始化提示词模板
        self.prompt_template = Template("""
我现在需要将用户的需求转换为详细的服装描述。请根据用户的需求，生成一个详细的服装描述，包括服装类别和详细的提示词。

用户需求: {{ user_need }}

请按照以下JSON格式输出，不要包含任何多余的内容：
{
    "category": "服装类别",
    "prompt": "详细的服装描述提示词，包括颜色、款式、材质、季节、风格等信息"
}

服装类别可以是：upper_body（上装）、lower_body（下装）、dresses（连衣裙）、shoes（鞋类）、hat（帽子）、glasses（眼镜）、belt（腰带）、scarf（围巾）

示例输出：
{
    "category": "upper_body",
    "prompt": "一件蓝色的棉质T恤，圆领设计，短袖款式，简约风格，适合夏季穿着"
}
""")
        
        self.negative_feedback_template = Template("""
用户对之前生成的服装描述不满意，需要根据负反馈进行调整。请根据用户的原始需求和负反馈，生成一个新的详细服装描述。

原始需求: {{ user_need }}
负反馈: {{ negative_feedback }}
原始描述: {{ original_description }}

请按照以下JSON格式输出，不要包含任何多余的内容：
{
    "category": "服装类别",
    "prompt": "新的详细服装描述提示词，包括颜色、款式、材质、季节、风格等信息"
}

服装类别可以是：upper_body（上装）、lower_body（下装）、dresses（连衣裙）、shoes（鞋类）、hat（帽子）、glasses（眼镜）、belt（腰带）、scarf（围巾）
""")

    def generate_response(self, prompt: str) -> Dict:
        """使用Qwen2.5模型生成回复"""
        try:
            response = self.client.chat.completions.create(
                model=LANGUAGE_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个专业的服装设计师助手，擅长根据用户需求生成详细的服装描述。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            content = response.choices[0].message.content.strip()
            # 解析JSON响应
            return json.loads(content)
        except Exception as e:
            print(f"生成响应时出错: {e}")
            # 返回默认值
            return {
                "category": "upper_body",
                "prompt": "一件简约风格的白色T恤，棉质面料，圆领设计，短袖款式"
            }

    def get_need2text(self, user_need: str) -> Dict:
        """将用户需求转换为服装描述"""
        # 渲染提示词模板
        prompt = self.prompt_template.render(user_need=user_need)
        # 生成响应
        result = self.generate_response(prompt)
        return result

    def get_addition_need2text(self, user_need: str, negative_feedback: str, original_description: str) -> Dict:
        """根据负反馈优化服装描述"""
        # 渲染负反馈提示词模板
        prompt = self.negative_feedback_template.render(
            user_need=user_need,
            negative_feedback=negative_feedback,
            original_description=original_description
        )
        # 生成响应
        result = self.generate_response(prompt)
        return result

# 创建全局实例
need2text_instance = Need2Text()

# 导出函数
def get_need2text(user_need: str) -> Dict:
    """将用户需求转换为服装描述"""
    return need2text_instance.get_need2text(user_need)

def get_addition_need2text(user_need: str, negative_feedback: str, original_description: str) -> Dict:
    """根据负反馈优化服装描述"""
    return need2text_instance.get_addition_need2text(user_need, negative_feedback, original_description)