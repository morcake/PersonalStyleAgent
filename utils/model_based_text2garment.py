import os
import torch
import numpy as np
from PIL import Image
from typing import Dict, List, Optional, Union
from diffusers import FluxPipeline
from .image_process import image_process
from .metrics import VQAScore
from config.config import STATIC_FOLDER, MAX_TEXT2GARMENT_ITERATIONS, GARMENT_VQA_HIGH_THRESHOLD, GARMENT_VQA_LOW_THRESHOLD
from jinja2 import Template
import logging
import os

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# CLIP模型的最大token限制
CLIP_MAX_TOKENS = 77

class Text2GarmentGenerator:
    def __init__(self):
        self.image_processor = image_process()
        self.vqa_scorer = VQAScore()
        self.pipeline = None
        
        # 初始化Flux管道用于直接生成服装图像
        try:
            # 首先尝试加载本地模型
            local_model_path = os.path.join(os.path.dirname(__file__), "FLUX.1-schnell")
            if os.path.exists(local_model_path):
                logger.info(f"尝试从本地路径加载Flux模型: {local_model_path}")
                self.pipeline = FluxPipeline.from_pretrained(local_model_path, torch_dtype=torch.float16, local_files_only=True)
            else:
                # 尝试从Hugging Face加载（使用镜像）
                logger.info("尝试从Hugging Face加载Flux模型")
                self.pipeline = FluxPipeline.from_pretrained("black-forest-labs/FLUX.1-schnell", torch_dtype=torch.float16)
                
            # 启用模型CPU卸载以节省内存
            if self.pipeline:
                self.pipeline.enable_model_cpu_offload()
                logger.info("Flux模型加载成功，已启用CPU卸载")
        except Exception as e:
            logger.error(f"初始化Flux管道时出错: {e}")
            self.pipeline = None
        
        # 加载提示词模板
        self.garment_prompt_template = Template("""
        {{ garment_description }}, high quality fashion photography, detailed, realistic, 4k, studio lighting, professional, clean background
        """)
        
        self.negative_prompt = """low quality, blurry, distorted, asymmetrical, color distortion, bad crop, poor composition, unrealistic, pixelated, artifact, text, watermark"""
    
    def _truncate_prompt(self, prompt: str, max_tokens: int = CLIP_MAX_TOKENS) -> str:
        """限制提示词长度，确保不超过CLIP模型的最大token限制"""
        # 对于中文和英文混合的情况，我们采取保守的策略
        # 中文每个字算一个token，英文按空格分割单词
        # 这是一个简化的处理方式，实际应用中可以使用更复杂的tokenizer
        
        if len(prompt) <= max_tokens:
            return prompt
        
        logger.warning(f"提示词过长({len(prompt)}>77)，正在截断")
        
        # 简单的中英文混合截断
        truncated = prompt[:max_tokens]
        logger.info(f"截断后的提示词: {truncated}")
        
        return truncated
    
    def generate_garment_image(self, prompt: str, output_path: str, width: int = 768, height: int = 1024) -> str:
        """使用Flux模型直接生成服装图像"""
        try:
            # 如果模型未初始化，返回None
            if self.pipeline is None:
                logger.warning("Flux模型未初始化，无法生成图像")
                return None
            
            # 渲染提示词
            rendered_prompt = self.garment_prompt_template.render(garment_description=prompt)
            
            # 截断提示词以避免超过CLIP模型的限制
            truncated_prompt = self._truncate_prompt(rendered_prompt)
            logger.info(f"生成图像的提示词: {truncated_prompt}")
            
            # 生成图像
            image = self.pipeline(
                prompt=truncated_prompt,
                negative_prompt=self.negative_prompt,
                width=width,
                height=height,
                guidance_scale=3.0,
                num_inference_steps=28
            ).images[0]
            
            # 保存图像
            image.save(output_path)
            logger.info(f"成功生成图像并保存至: {output_path}")
            
            return output_path
        except Exception as e:
            logger.error(f"生成图像时出错: {e}")
            return None
    
    def produce_garment(self, garment_prompt: str, category: str, output_dir: str, 
                        max_iterations: int = MAX_TEXT2GARMENT_ITERATIONS, 
                        num_images_per_iter: int = 3) -> List[Dict]:
        """生成并筛选服装图像"""
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 初始化变量
        all_images = []
        high_score_images = []
        current_iteration = 0
        
        # 获取类别对应的评分阈值
        high_threshold = GARMENT_VQA_HIGH_THRESHOLD.get(category, 0.75)
        low_threshold = GARMENT_VQA_LOW_THRESHOLD.get(category, 0.65)
        
        # 进行迭代生成和评估
        while current_iteration < max_iterations and len(high_score_images) < 3:
            logger.info(f"迭代 {current_iteration + 1}/{max_iterations}...")
            
            # 生成多个图像变体
            for i in range(num_images_per_iter):
                # 构建输出路径
                image_path = os.path.join(output_dir, f"garment_{current_iteration}_{i}.png")
                
                # 生成图像
                generated_path = self.generate_garment_image(garment_prompt, image_path)
                
                if generated_path and os.path.exists(generated_path):
                    try:
                        # 计算VQA分数
                        score = self.vqa_scorer.score(generated_path, garment_prompt)
                        
                        # 确保score是一个浮点数
                        if not isinstance(score, (int, float)):
                            logger.warning(f"警告: 评分不是数字类型，得到的是: {type(score)}, 值: {score}")
                            score = 0.5  # 默认分数
                        
                        # 记录图像信息
                        image_info = {
                            "path": generated_path,
                            "score": float(score),  # 确保是浮点数
                            "prompt": garment_prompt,
                            "category": category
                        }
                        
                        all_images.append(image_info)
                        
                        # 根据分数分类
                        if score >= high_threshold:
                            high_score_images.append(image_info)
                    except Exception as e:
                        logger.error(f"处理图像 {generated_path} 时出错: {e}")
                        continue
            
            current_iteration += 1
        
        # 如果没有足够的高评分图像，使用低评分阈值
        if len(high_score_images) < 3:
            # 按分数排序
            try:
                all_images.sort(key=lambda x: x["score"], reverse=True)
                # 选择前3张图像
                high_score_images = all_images[:3]
            except Exception as e:
                logger.error(f"排序图像时出错: {e}")
                # 如果排序失败，返回所有可用图像
                high_score_images = all_images
        
        # 如果仍然没有足够的图像，返回所有找到的图像
        if len(high_score_images) == 0:
            high_score_images = all_images
        
        # 确保返回的列表只包含有效的图像字典
        valid_images = []
        for img in high_score_images:
            if isinstance(img, dict) and "path" in img:
                valid_images.append(img)
            else:
                logger.warning(f"警告: 跳过无效的图像信息: {img}")
        
        # 返回筛选后的图像
        return valid_images
    
    def description_to_garment(self, garment_description: Dict) -> Dict:
        """从服装描述生成服装图像"""
        # 获取类别和提示词
        category = garment_description.get("category", "upper_body")
        prompt = garment_description.get("prompt", "简约风格的白色T恤")
        
        # 创建输出目录
        output_dir = os.path.join(STATIC_FOLDER, "garments", f"{category}_{str(hash(prompt))[:8]}")
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成服装图像
        garment_images = self.produce_garment(prompt, category, output_dir)
        
        # 准备返回结果
        result = {
            "category": category,
            "prompt": prompt,
            "garments": []
        }
        
        # 添加服装图像信息
        for i, garment in enumerate(garment_images):
            try:
                # 确保garment是字典类型且包含必要的键
                if isinstance(garment, dict) and "path" in garment and "score" in garment:
                    result["garments"].append({
                        "id": i,
                        "path": garment["path"],
                        "score": garment["score"],
                        "relative_path": os.path.relpath(garment["path"], STATIC_FOLDER)
                    })
                else:
                    logger.warning(f"警告: 跳过无效的服装图像数据: {garment}")
                    continue
            except Exception as e:
                logger.error(f"处理服装图像信息时出错: {e}")
                continue
        
        return result

# 创建全局实例
text2garment_generator_instance = Text2GarmentGenerator()

# 导出函数
def description_to_garment(garment_description: Dict) -> Dict:
    """从服装描述生成服装图像"""
    return text2garment_generator_instance.description_to_garment(garment_description)