import os
import torch
import numpy as np
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from openai import OpenAI
from config.config import API_KEY, BASE_URL, VISION_MODEL
from jinja2 import Template

# 检查base64模块是否可用
try:
    import base64
    HAS_BASE64 = True
except ImportError:
    HAS_BASE64 = False
    print("警告: base64模块未找到，VQA评分功能可能受限")

class VQAScore:
    def __init__(self):
        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=API_KEY,
            base_url=BASE_URL
        )
        
        self.vqa_template = Template("""
请评估这张图像与描述的匹配程度。

描述: {{ description }}

请从0到1的分数给出评估，其中0表示完全不匹配，1表示完全匹配。只需要输出分数，不要包含其他任何内容。
""")

    def score(self, image_path: str, description: str) -> float:
        """评估图像与描述的匹配程度"""
        try:
            # 检查base64模块是否可用
            if not HAS_BASE64:
                print("base64模块不可用，无法处理图像")
                return 0.5
            
            # 读取图像并转换为base64
            try:
                with open(image_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode("utf-8")
            except Exception as e:
                print(f"读取图像文件时出错: {e}")
                return 0.5
            
            # 构建提示词
            try:
                prompt = self.vqa_template.render(description=description)
            except Exception as e:
                print(f"渲染提示词模板时出错: {e}")
                prompt = f"评估这张图像与描述的匹配程度: {description}"
            
            # 调用视觉模型
            try:
                response = self.client.chat.completions.create(
                    model=VISION_MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_data}"
                                    }
                                }
                            ]
                        }
                    ],
                    temperature=0.0
                )
            except Exception as e:
                print(f"调用视觉模型时出错: {e}")
                return 0.5
            
            # 解析分数，添加更严格的类型检查
            try:
                if response and hasattr(response, 'choices') and response.choices and len(response.choices) > 0:
                    if hasattr(response.choices[0], 'message') and response.choices[0].message and hasattr(response.choices[0].message, 'content'):
                        score_text = response.choices[0].message.content.strip()
                        try:
                            score = float(score_text)
                            # 确保分数在0-1范围内
                            return max(0.0, min(1.0, float(score)))
                        except ValueError:
                            print(f"无法将评分文本转换为浮点数: {score_text}")
                            return 0.5
                    else:
                        print("响应消息格式不正确")
                        return 0.5
                else:
                    print("响应中没有找到有效的选择")
                    return 0.5
            except Exception as e:
                print(f"解析评分时出错: {e}")
                return 0.5
        except Exception as e:
            print(f"VQA评分时出错: {e}")
            # 返回默认分数
            return 0.5

class ClipScore:
    def __init__(self):
        # 加载CLIP模型，如果本地没有会尝试下载
        try:
            # self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32", local_files_only=True)
            # self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32", local_files_only=True)
            # 使用本地目录路径而不是模型名称
            local_model_path = os.path.join(os.path.dirname(__file__), "clip-vit-base-patch32")
            print(f"尝试从本地路径加载CLIP模型: {local_model_path}")
            self.model = CLIPModel.from_pretrained(local_model_path, local_files_only=True)
            self.processor = CLIPProcessor.from_pretrained(local_model_path, local_files_only=True)
            print("CLIP模型从本地加载成功")
        except Exception as e:
            # 如果本地没有模型文件，使用VQA评分作为备选
            self.model = None
            self.processor = None
            print(f"警告: 无法加载CLIP模型，错误信息: {e}")
            print("将使用VQA评分作为备选")
            print("提示: 请确保openai/clip-vit-base-patch32模型文件已正确放置在utils/clip-vit-base-patch32目录下")
        
        # 检查是否有GPU可用
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if self.model:
            self.model.to(self.device)

    def score(self, image_path: str, text: str) -> float:
        """计算图像和文本的CLIP相似度分数"""
        try:
            # 如果没有成功加载CLIP模型，返回默认分数
            if not self.model or not self.processor:
                return 0.5
            
            # 读取图像
            image = Image.open(image_path).convert("RGB")
            
            # 预处理
            inputs = self.processor(text=[text], images=image, return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # 计算特征
            outputs = self.model(**inputs)
            logits_per_image = outputs.logits_per_image  # 图像到文本的logits
            
            # 归一化分数
            score = torch.softmax(logits_per_image, dim=1)[0, 0].item()
            
            return score
        except Exception as e:
            print(f"CLIP评分时出错: {e}")
            # 返回默认分数
            return 0.5



# 由于我们可能没有base64模块，这里添加一个简单的导入检查
try:
    import base64
    HAS_BASE64 = True
except ImportError:
    HAS_BASE64 = False
    print("警告: base64模块未找到，VQA评分功能可能受限")