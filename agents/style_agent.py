import os
import json
from typing import Dict, List, Optional, Union
from utils.need2text import get_need2text, get_addition_need2text
from utils.model_based_text2garment import description_to_garment
from utils.flux_vton import run_vton
from utils.search import search_clothing_items
from utils.metrics import VQAScore, ClipScore
from config.config import STATIC_FOLDER

class StyleAgent:
    def __init__(self):
        # 初始化各组件
        self.vqa_scorer = VQAScore()
        self.clip_scorer = ClipScore()

    def generate_clothing_description(self, user_need: str) -> Dict:
        """根据用户需求生成服装描述"""
        try:
            # 调用need2text组件生成服装描述
            garment_description = get_need2text(user_need)
            print(f"生成的服装描述: {garment_description}")
            return garment_description
        except Exception as e:
            print(f"生成服装描述时出错: {e}")
            # 返回默认描述
            return {
                "category": "upper_body",
                "prompt": "简约风格的白色T恤，棉质面料，圆领设计，短袖款式"
            }

    def refine_clothing_description(self, user_need: str, negative_feedback: str, original_description: Dict) -> Dict:
        """根据负反馈优化服装描述"""
        try:
            # 调用need2text组件优化服装描述
            original_prompt = original_description.get("prompt", "")
            refined_description = get_addition_need2text(user_need, negative_feedback, original_prompt)
            print(f"优化后的服装描述: {refined_description}")
            return refined_description
        except Exception as e:
            print(f"优化服装描述时出错: {e}")
            # 返回原始描述
            return original_description

    def generate_clothing_images(self, garment_description: Dict) -> Dict:
        """根据服装描述生成服装图像"""
        try:
            # 调用text2garment组件生成服装图像
            garment_images = description_to_garment(garment_description)
            print(f"生成了 {len(garment_images.get('garments', []))} 张服装图像")
            return garment_images
        except Exception as e:
            print(f"生成服装图像时出错: {e}")
            # 返回空结果
            return {
                "category": garment_description.get("category", "upper_body"),
                "prompt": garment_description.get("prompt", ""),
                "garments": []
            }

    def try_on_clothing(self, garment_info: Dict, human_image_path: str, gender: str = "female") -> Dict:
        """进行虚拟试穿"""
        try:
            # 检查人体图像是否存在
            if not os.path.exists(human_image_path):
                print(f"人体图像文件不存在: {human_image_path}")
                return {
                    "category": garment_info.get("category", "upper_body"),
                    "prompt": garment_info.get("prompt", ""),
                    "vton_results": []
                }
            
            # 调用flux_vton组件进行虚拟试穿
            vton_result = run_vton(garment_info, human_image_path, gender)
            print(f"生成了 {len(vton_result.get('vton_results', []))} 个虚拟试穿结果")
            return vton_result
        except Exception as e:
            print(f"虚拟试穿时出错: {e}")
            # 返回空结果
            return {
                "category": garment_info.get("category", "upper_body"),
                "prompt": garment_info.get("prompt", ""),
                "vton_results": []
            }

    def search_clothing_products(self, query: str, num_results: int = 10) -> List[Dict]:
        """搜索服装商品"""
        try:
            # 调用search组件搜索服装商品
            products = search_clothing_items(query, num_results)
            print(f"搜索到 {len(products)} 个服装商品")
            return products
        except Exception as e:
            print(f"搜索服装商品时出错: {e}")
            # 返回空列表
            return []

    def run_pipeline(self, user_need: str, human_image_path: Optional[str] = None, 
                    gender: str = "female", num_products: int = 5) -> Dict:
        """运行完整的StyleAgent流程"""
        try:
            # 1. 生成服装描述
            garment_description = self.generate_clothing_description(user_need)
            
            # 2. 生成服装图像
            garment_images = self.generate_clothing_images(garment_description)
            
            # 3. 进行虚拟试穿（如果提供了人体图像）
            vton_result = {}
            if human_image_path:
                vton_result = self.try_on_clothing(garment_images, human_image_path, gender)
            
            # 4. 搜索相关服装商品
            search_query = garment_description.get("prompt", user_need)
            products = self.search_clothing_products(search_query, num_products)
            
            # 5. 构建最终结果
            result = {
                "status": "success",
                "garment_description": garment_description,
                "garment_images": garment_images,
                "virtual_try_on": vton_result,
                "recommended_products": products,
                "user_need": user_need
            }
            
            return result
        except Exception as e:
            print(f"运行StyleAgent流程时出错: {e}")
            # 返回错误结果
            return {
                "status": "error",
                "message": str(e),
                "user_need": user_need
            }

    def save_result(self, result: Dict, output_path: str) -> bool:
        """保存结果到文件"""
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 保存结果为JSON文件
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"结果已保存到: {output_path}")
            return True
        except Exception as e:
            print(f"保存结果时出错: {e}")
            return False

    def load_result(self, result_path: str) -> Dict:
        """从文件加载结果"""
        try:
            # 检查文件是否存在
            if not os.path.exists(result_path):
                print(f"结果文件不存在: {result_path}")
                return {}
            
            # 加载JSON文件
            with open(result_path, "r", encoding="utf-8") as f:
                result = json.load(f)
            
            return result
        except Exception as e:
            print(f"加载结果时出错: {e}")
            return {}