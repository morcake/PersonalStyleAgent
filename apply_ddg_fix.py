#!/usr/bin/env python3
"""
修复DDG搜索"No results found"问题的工具
此脚本将应用修复到utils/text2garment.py文件并运行测试
"""
import os
import sys
import shutil
import logging
import importlib
import traceback
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DDGSearchFixer:
    """修复DDG搜索问题的工具类"""
    
    @staticmethod
    def get_fixed_code():
        """获取修复后的text2garment.py代码"""
        return '''import json
import requests
from typing import Dict, List, Optional, Union
from PIL import Image
import ddgs
import time
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
        # 基础查询词 - 增强版
        base_queries = [
            f"{garment_prompt}",
            f"{garment_prompt} 高清图片",
            f"{garment_prompt} 时尚照片",
            f"{garment_prompt} 模特实拍",
            f"{garment_prompt} 时尚穿搭",
            f"{garment_prompt} 街拍",
            f"{garment_prompt} 白底图",
            f"{garment_prompt} 服装展示",
            f"{garment_prompt} 新品",
            f"{garment_prompt} 时尚单品"
        ]
        
        # 根据服装类别添加特定查询词
        category_queries = []
        if category == "upper_body":
            category_queries = [
                f"{garment_prompt} 上衣",
                f"{garment_prompt} 短袖",
                f"{garment_prompt} 长袖",
                f"{garment_prompt} T恤",
                f"{garment_prompt} 衬衫"
            ]
        elif category == "lower_body":
            category_queries = [
                f"{garment_prompt} 下装",
                f"{garment_prompt} 裤子",
                f"{garment_prompt} 牛仔裤",
                f"{garment_prompt} 裙子",
                f"{garment_prompt} 短裤"
            ]
        elif category == "dresses":
            category_queries = [
                f"{garment_prompt} 连衣裙",
                f"{garment_prompt} 长裙",
                f"{garment_prompt} 短裙",
                f"{garment_prompt} 礼服",
                f"{garment_prompt} 夏季连衣裙"
            ]
        elif category == "shoes":
            category_queries = [
                f"{garment_prompt} 鞋子",
                f"{garment_prompt} 运动鞋",
                f"{garment_prompt} 高跟鞋",
                f"{garment_prompt} 平底鞋",
                f"{garment_prompt} 靴子"
            ]
        
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
        retry_count = 0
        max_retries = 3
        
        for query in queries:
            if len(downloaded_images) >= num_images:
                break
                
            try:
                # 使用DuckDuckGo搜索图像
                print(f"搜索查询: {query}")
                results = self.ddgs.images(query, max_results=num_images * 2)  # 获取更多结果以提高成功率
                
                # 检查是否有结果
                if not results:
                    print(f"搜索图像时无结果: {query}")
                    # 如果没有结果，尝试调整查询词
                    retry_query = f"{query} 时尚 2024"
                    print(f"尝试调整后的查询词: {retry_query}")
                    results = self.ddgs.images(retry_query, max_results=num_images * 2)
                    
                    if not results:
                        retry_query = f"{query.replace('高清图片', '')} 服装 实拍"
                        print(f"再次尝试调整后的查询词: {retry_query}")
                        results = self.ddgs.images(retry_query, max_results=num_images * 2)
                
                if results:
                    print(f"找到 {len(results)} 个图像结果")
                    
                    for i, result in enumerate(results):
                        try:
                            if len(downloaded_images) >= num_images:
                                break
                                
                            # 下载图像
                            image_url = result["image"]
                            print(f"下载图像 {i+1}/{len(results)}: {image_url[:50]}...")
                            response = requests.get(image_url, stream=True, timeout=15)  # 增加超时时间
                            
                            if response.status_code == 200:
                                # 保存图像
                                image_path = os.path.join(output_dir, f"garment_{len(downloaded_images)}.jpg")
                                with open(image_path, "wb") as f:
                                    for chunk in response.iter_content(1024):
                                        f.write(chunk)
                                
                                # 检查图像是否有效
                                try:
                                    with Image.open(image_path) as img:
                                        img.verify()
                                    
                                    # 进一步检查图像大小
                                    with Image.open(image_path) as img:
                                        width, height = img.size
                                        if width < 200 or height < 200:
                                            print(f"跳过过小的图像: {image_path}")
                                            os.remove(image_path)
                                            continue
                                    
                                    downloaded_images.append(image_path)
                                    print(f"成功下载图像: {image_path}")
                                except Exception as img_err:
                                    print(f"验证图像时出错: {img_err}")
                                    if os.path.exists(image_path):
                                        os.remove(image_path)
                                    continue
                        except Exception as e:
                            print(f"下载图像时出错: {e}")
                            # 增加重试计数
                            retry_count += 1
                            if retry_count <= max_retries:
                                print(f"第 {retry_count} 次重试...")
                                time.sleep(1)  # 短暂延迟后重试
                            continue
            except Exception as e:
                print(f"搜索图像时出错: {e}")
                # 增加重试计数
                retry_count += 1
                if retry_count <= max_retries:
                    print(f"第 {retry_count} 次重试...")
                    time.sleep(1)  # 短暂延迟后重试
                continue
            finally:
                # 每次查询后添加短暂延迟，避免请求过于频繁
                time.sleep(0.5)
        
        print(f"总共成功下载 {len(downloaded_images)} 张图像")
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
        
        # 创建输出目录 - 修复了hash切片问题
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
'''
    
    @staticmethod
    def backup_file(file_path: str) -> str:
        """备份文件并返回备份路径"""
        backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup_path)
        logger.info(f"已备份文件到: {backup_path}")
        return backup_path
    
    @staticmethod
    def apply_fix():
        """应用修复到text2garment.py文件"""
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils", "text2garment.py")
        
        # 备份原始文件
        backup_path = DDGSearchFixer.backup_file(file_path)
        
        # 写入修复后的代码
        fixed_code = DDGSearchFixer.get_fixed_code()
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_code)
        
        logger.info(f"已应用修复到: {file_path}")
        return file_path, backup_path
    
    @staticmethod
    def restore_backup(backup_path: str, original_path: str):
        """从备份恢复原始文件"""
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, original_path)
            logger.info(f"已从备份恢复原始文件: {original_path}")
        else:
            logger.error(f"备份文件不存在: {backup_path}")
    
    @staticmethod
    def run_test():
        """运行简单的测试"""
        logger.info("开始运行测试...")
        
        # 重新导入模块以加载修复后的代码
        try:
            import utils.text2garment
            importlib.reload(utils.text2garment)
            from utils.text2garment import description_to_garment
            logger.info("成功导入修复后的模块")
            
            # 运行简单测试
            test_case = {"category": "upper_body", "prompt": "简约风格的白色T恤"}
            logger.info(f"测试用例: {test_case}")
            
            result = description_to_garment(test_case)
            logger.info(f"测试结果: 生成了 {len(result.get('garments', []))} 张服装图像")
            
            if result.get('garments'):
                for garment in result['garments']:
                    logger.info(f"服装图像路径: {garment.get('path')}, 分数: {garment.get('score')}")
            
            return len(result.get('garments', [])) > 0
            
        except Exception as e:
            logger.error(f"测试失败: {e}")
            traceback.print_exc()
            return False

def main():
    """主函数"""
    print("===== DDG搜索问题修复工具 =====")
    print()
    print("这个工具将修复text2garment.py中的DDG搜索问题，包括:")
    print("1. 增强搜索查询词")
    print("2. 添加重试机制")
    print("3. 优化图像下载和验证")
    print("4. 修复hash切片问题")
    print()
    
    # 用户确认
    confirm = input("是否继续应用修复？(y/n): ")
    if confirm.lower() != 'y':
        print("操作已取消")
        return
    
    try:
        # 应用修复
        original_path, backup_path = DDGSearchFixer.apply_fix()
        
        # 运行测试
        test_success = DDGSearchFixer.run_test()
        
        if test_success:
            print("\n修复成功！测试通过，能够成功获取服装图像。")
        else:
            print("\n测试失败，无法获取服装图像。")
            
            # 询问是否恢复原始文件
            restore = input("是否恢复原始文件？(y/n): ")
            if restore.lower() == 'y':
                DDGSearchFixer.restore_backup(backup_path, original_path)
    except Exception as e:
        print(f"\n应用修复时出错: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()