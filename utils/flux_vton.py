import os
import json
import torch
import numpy as np
from PIL import Image
from typing import Dict, List, Optional, Union
from diffusers import FluxPipeline
from .image_process import image_process
from .metrics import ClipScore
from .human_mask import human_mask_instance
from config.config import STATIC_FOLDER, MAX_FLUX_VTON_ITERATIONS, VTON_CLIP_SCORE_HIGH_THRESHOLD, VTON_CLIP_SCORE_LOW_THRESHOLD
from jinja2 import Template

class FluxVTON:
    def __init__(self):
        self.image_processor = image_process()
        self.clip_scorer = ClipScore()
        self.human_mask = human_mask_instance
        
        # 初始化Flux管道
        self.pipeline = None
        try:
            # 首先尝试加载本地模型（如果存在）
            # local_model_path = os.path.join(os.path.dirname(__file__), "black-forest-labs", "FLUX.1-schnell")
            local_model_path = os.path.join(os.path.dirname(__file__), "FLUX.1-schnell")
            if os.path.exists(local_model_path):
                print(f"尝试从本地路径加载Flux模型: {local_model_path}")
                self.pipeline = FluxPipeline.from_pretrained(local_model_path, torch_dtype=torch.float16, local_files_only=True)
                self.pipeline.enable_model_cpu_offload()
                print("Flux模型从本地加载成功")
            else:
                # 如果本地没有，尝试从Hugging Face加载（会自动使用HF_ENDPOINT设置）
                print("尝试从Hugging Face加载Flux模型")
                self.pipeline = FluxPipeline.from_pretrained("black-forest-labs/FLUX.1-schnell", torch_dtype=torch.float16)
                self.pipeline.enable_model_cpu_offload()
                print("Flux模型从Hugging Face加载成功")
        except Exception as e:
            print(f"初始化Flux管道时出错: {e}")
            print("虚拟试穿功能将使用简化模式运行")
            self.pipeline = None
        
        # 加载提示词模板
        self.prompts_flux_true = Template("""
{{ gender }} model wearing {{ garment_description }}, high quality, detailed, realistic, 4k, studio lighting
""")
        
        self.prompts_flux_false = Template("""
{{ garment_description }} on {{ gender }} model, high quality, detailed, realistic, 4k, studio lighting, perfect fit
""")

    def get_addition_negative_flux_prompt(self) -> str:
        """获取虚拟试穿的负面提示词"""
        return "模糊，低质量，变形，不对称，颜色失真，裁剪不当，不符合人体结构，服装与人体不匹配"

    def contact_picture(self, image1_path: str, image2_path: str, output_path: str) -> str:
        """拼接两张图像"""
        try:
            # 打开图像
            image1 = Image.open(image1_path).convert("RGBA")
            image2 = Image.open(image2_path).convert("RGBA")
            
            # 调整图像大小
            width = max(image1.width, image2.width)
            height = image1.height + image2.height
            
            # 创建新图像
            result = Image.new("RGBA", (width, height), (255, 255, 255, 255))
            
            # 粘贴图像
            result.paste(image1, ((width - image1.width) // 2, 0))
            result.paste(image2, ((width - image2.width) // 2, image1.height))
            
            # 保存结果
            result.save(output_path, "PNG")
            
            return output_path
        except Exception as e:
            print(f"拼接图像时出错: {e}")
            return image1_path

    def edit_vton_once(self, garment_image_path: str, human_image_path: str, prompt: str, 
                       output_path: str, gender: str = "female") -> str:
        """单次虚拟试穿编辑"""
        try:
            # 如果Flux管道未初始化，返回原始图像
            if self.pipeline is None:
                print("Flux管道未初始化，无法进行虚拟试穿")
                return garment_image_path
            
            # 读取图像
            garment_image = Image.open(garment_image_path).convert("RGB")
            human_image = Image.open(human_image_path).convert("RGB")
            
            # 检查服装图像是否包含模特
            has_model = self.human_mask.detect_human(garment_image_path)
            
            # 根据是否包含模特选择提示词模板
            if has_model:
                vton_prompt = self.prompts_flux_true.render(garment_description=prompt, gender=gender)
            else:
                vton_prompt = self.prompts_flux_false.render(garment_description=prompt, gender=gender)
            
            # 生成虚拟试穿结果
            negative_prompt = self.get_addition_negative_flux_prompt()
            
            # 这里是一个简化的实现，实际的虚拟试穿需要更复杂的处理
            # 包括人体解析、服装分割、姿态估计等
            
            # 由于Flux模型可能需要特定的输入格式，这里只是一个示例
            try:
                # 为了演示，我们直接保存原始图像作为结果
                # 在实际应用中，应该使用Flux模型进行真正的虚拟试穿
                output_image = human_image.copy()
                output_image.save(output_path)
            except Exception as e:
                print(f"生成虚拟试穿图像时出错: {e}")
                # 如果出错，返回原始图像
                human_image.save(output_path)
            
            return output_path
        except Exception as e:
            print(f"虚拟试穿时出错: {e}")
            return garment_image_path

    def pick_vton_once(self, garment_image_path: str, human_image_path: str, prompt: str, 
                      output_dir: str, category: str, gender: str = "female", 
                      num_variations: int = 3) -> List[Dict]:
        """单次试穿与评分筛选"""
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        vton_results = []
        
        # 进行多次试穿以生成变体
        for i in range(num_variations):
            output_path = os.path.join(output_dir, f"vton_{i}.png")
            
            # 进行虚拟试穿
            vton_image_path = self.edit_vton_once(
                garment_image_path=garment_image_path,
                human_image_path=human_image_path,
                prompt=prompt,
                output_path=output_path,
                gender=gender
            )
            
            # 计算CLIP分数
            score = self.clip_scorer.score(vton_image_path, prompt)
            
            # 记录结果
            vton_result = {
                "path": vton_image_path,
                "score": score,
                "prompt": prompt
            }
            
            vton_results.append(vton_result)
        
        # 获取类别对应的评分阈值
        high_threshold = VTON_CLIP_SCORE_HIGH_THRESHOLD.get(category, 0.8)
        low_threshold = VTON_CLIP_SCORE_LOW_THRESHOLD.get(category, 0.7)
        
        # 筛选高评分结果
        high_score_results = [result for result in vton_results if result["score"] >= high_threshold]
        
        # 如果没有足够的高评分结果，使用低评分阈值
        if len(high_score_results) < 1:
            high_score_results = [result for result in vton_results if result["score"] >= low_threshold]
        
        # 如果仍然没有足够的结果，选择评分最高的
        if len(high_score_results) < 1 and vton_results:
            vton_results.sort(key=lambda x: x["score"], reverse=True)
            high_score_results = [vton_results[0]]
        
        return high_score_results

    def run_vton(self, garment_info: Dict, human_image_path: str, gender: str = "female") -> Dict:
        """虚拟试穿主函数"""
        # 获取服装信息
        category = garment_info.get("category", "upper_body")
        prompt = garment_info.get("prompt", "简约风格的白色T恤")
        garments = garment_info.get("garments", [])
        
        # 创建输出目录
        output_dir = os.path.join(STATIC_FOLDER, "vton", f"{category}_{hash(prompt)[:8]}")
        os.makedirs(output_dir, exist_ok=True)
        
        # 初始化结果
        result = {
            "category": category,
            "prompt": prompt,
            "vton_results": []
        }
        
        # 为每件服装进行虚拟试穿
        for garment in garments:
            garment_image_path = garment.get("path")
            if not garment_image_path or not os.path.exists(garment_image_path):
                continue
            
            # 创建服装专属输出目录
            garment_output_dir = os.path.join(output_dir, f"garment_{garment.get('id', 0)}")
            os.makedirs(garment_output_dir, exist_ok=True)
            
            # 进行多轮迭代优化
            best_result = None
            current_iteration = 0
            
            while current_iteration < MAX_FLUX_VTON_ITERATIONS:
                print(f"虚拟试穿迭代 {current_iteration + 1}/{MAX_FLUX_VTON_ITERATIONS}...")
                
                # 进行单次试穿
                vton_results = self.pick_vton_once(
                    garment_image_path=garment_image_path,
                    human_image_path=human_image_path,
                    prompt=prompt,
                    output_dir=garment_output_dir,
                    category=category,
                    gender=gender
                )
                
                # 更新最佳结果
                if vton_results:
                    # 选择评分最高的结果
                    vton_results.sort(key=lambda x: x["score"], reverse=True)
                    current_best = vton_results[0]
                    
                    if best_result is None or current_best["score"] > best_result["score"]:
                        best_result = current_best
                    
                    # 如果达到高评分阈值，可以提前结束迭代
                    if current_best["score"] >= VTON_CLIP_SCORE_HIGH_THRESHOLD.get(category, 0.8):
                        break
                
                current_iteration += 1
            
            # 如果有最佳结果，添加到返回结果中
            if best_result:
                result["vton_results"].append({
                    "garment_id": garment.get("id", 0),
                    "vton_path": best_result["path"],
                    "score": best_result["score"],
                    "relative_path": os.path.relpath(best_result["path"], STATIC_FOLDER)
                })
        
        return result

# 创建全局实例
flux_vton_instance = FluxVTON()

# 导出函数
def run_vton(garment_info: Dict, human_image_path: str, gender: str = "female") -> Dict:
    """虚拟试穿主函数"""
    return flux_vton_instance.run_vton(garment_info, human_image_path, gender)