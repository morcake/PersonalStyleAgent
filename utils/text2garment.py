import os
import json
import requests
from typing import Dict, List, Optional, Union
from PIL import Image
import ddgs
from .image_process import image_process
from .metrics import VQAScore
from config.config import STATIC_FOLDER, MAX_TEXT2GARMENT_ITERATIONS, GARMENT_VQA_HIGH_THRESHOLD, GARMENT_VQA_LOW_THRESHOLD

class Text2Garment:
    def __init__(self):
        self.image_processor = image_process()
        self.vqa_scorer = VQAScore()
        self.ddgs = ddgs.DDGS()

    def get_addition_negative_prompt(self) -> str:
        """获取通用的负面提示词"""
        # 这里可以根据需要自定义负面提示词
        return "模糊，低质量，变形，不对称，颜色失真，裁剪不当，不符合人体结构"

    def make_queries(self, garment_prompt: str, category: str, addition_prompt: str = "") -> List[str]:
        """构建搜索查询词"""
        # 基础查询词
        base_queries = [
            f"{garment_prompt}",
            f"{garment_prompt} 高清图片",
            f"{garment_prompt} 时尚照片",
            f"{garment_prompt} 模特实拍"
        ]
        
        # 根据服装类别添加特定查询词
        category_queries = []
        if category == "upper_body":
            category_queries = [f"{garment_prompt} 上衣"]
        elif category == "lower_body":
            category_queries = [f"{garment_prompt} 下装"]
        elif category == "dresses":
            category_queries = [f"{garment_prompt} 连衣裙"]
        elif category == "shoes":
            category_queries = [f"{garment_prompt} 鞋子"]
        
        # 合并所有查询词
        all_queries = base_queries + category_queries
        
        # 如果有额外提示词，添加到每个查询词
        if addition_prompt:
            all_queries = [f"{query} {addition_prompt}" for query in all_queries]
        
        return all_queries

    def get_text2garment(self, queries: List[str], output_dir: str, num_images: int = 10) -> List[str]:
        """通过DDG搜索获取服装图像"""
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        downloaded_images = []
        
        for query in queries:
            try:
                # 使用DuckDuckGo搜索图像
                results = self.ddgs.images(query, max_results=num_images)
                
                for i, result in enumerate(results):
                    try:
                        # 下载图像
                        image_url = result["image"]
                        response = requests.get(image_url, stream=True, timeout=10)
                        
                        if response.status_code == 200:
                            # 保存图像
                            image_path = os.path.join(output_dir, f"garment_{len(downloaded_images)}.jpg")
                            with open(image_path, "wb") as f:
                                for chunk in response.iter_content(1024):
                                    f.write(chunk)
                            
                            # 检查图像是否有效
                            with Image.open(image_path) as img:
                                img.verify()
                            
                            downloaded_images.append(image_path)
                            
                            # 达到所需数量后停止
                            if len(downloaded_images) >= num_images:
                                return downloaded_images
                    except Exception as e:
                        print(f"下载图像时出错: {e}")
                        continue
            except Exception as e:
                print(f"搜索图像时出错: {e}")
                continue
        
        return downloaded_images

    def produce_garment(self, garment_prompt: str, category: str, output_dir: str, 
                        max_iterations: int = MAX_TEXT2GARMENT_ITERATIONS, 
                        num_images_per_iter: int = 10) -> List[Dict]:
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
        
        # 进行迭代搜索和评估
        while current_iteration < max_iterations and len(high_score_images) < 3:
            print(f"迭代 {current_iteration + 1}/{max_iterations}...")
            
            # 构建搜索查询词
            queries = self.make_queries(garment_prompt, category)
            
            # 搜索图像
            image_dir = os.path.join(output_dir, f"iteration_{current_iteration}")
            downloaded_images = self.get_text2garment(queries, image_dir, num_images_per_iter)
            
            # 评估图像
            for image_path in downloaded_images:
                try:
                    # 计算VQA分数
                    score = self.vqa_scorer.score(image_path, garment_prompt)
                    
                    # 确保score是一个浮点数
                    if not isinstance(score, (int, float)):
                        print(f"警告: 评分不是数字类型，得到的是: {type(score)}, 值: {score}")
                        score = 0.5  # 默认分数
                    
                    # 记录图像信息
                    image_info = {
                        "path": image_path,
                        "score": float(score),  # 确保是浮点数
                        "prompt": garment_prompt,
                        "category": category
                    }
                    
                    all_images.append(image_info)
                    
                    # 根据分数分类
                    if score >= high_threshold:
                        high_score_images.append(image_info)
                except Exception as e:
                    print(f"处理图像 {image_path} 时出错: {e}")
                    continue
            
            current_iteration += 1
        
        # 如果没有足够的高评分图像，使用低评分阈值
        if len(high_score_images) < 3:
            # 按分数排序，添加类型检查
            try:
                all_images.sort(key=lambda x: x["score"], reverse=True)
                # 选择前3张图像
                high_score_images = all_images[:3]
            except Exception as e:
                print(f"排序图像时出错: {e}")
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
                print(f"警告: 跳过无效的图像信息: {img}")
        
        # 返回筛选后的图像
        return valid_images

    def description_to_garment(self, garment_description: Dict) -> Dict:
        """从服装描述生成服装图像"""
        # 获取类别和提示词
        category = garment_description.get("category", "upper_body")
        prompt = garment_description.get("prompt", "简约风格的白色T恤")
        
        # 创建输出目录
        output_dir = os.path.join(STATIC_FOLDER, "garments", f"{category}_{str(hash(prompt))[:8]}")
        # 整数不支持切片。需要先将hash值转换为字符串再切片
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
                    print(f"警告: 跳过无效的服装图像数据: {garment}")
                    continue
            except Exception as e:
                print(f"处理服装图像信息时出错: {e}")
                continue
        
        return result

# 创建全局实例
text2garment_instance = Text2Garment()

# 导出函数
def description_to_garment(garment_description: Dict) -> Dict:
    """从服装描述生成服装图像"""
    return text2garment_instance.description_to_garment(garment_description)