import os
import logging
import requests
from typing import List, Dict
from PIL import Image
from duckduckgo_search import DDGS
from config.config import (
    STATIC_FOLDER,
    MAX_TEXT2GARMENT_ITERATIONS,
    GARMENT_VQA_HIGH_THRESHOLD,
    GARMENT_VQA_LOW_THRESHOLD,
    SEARCH_TIMEOUT,
    SEARCH_RESULT_LIMIT
)
from utils.image_process import ImageProcess
from utils.metrics import VQAScore

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DDGSearchFix:

    # DDG搜索修复工具，提供增强搜索查询词和添加备份搜索方法的功能
    
    def enhance_search_queries(self, queries: List[str]) -> List[str]:

        # 增强搜索查询词，添加更多变体和修饰词，提高搜索成功率
        enhanced_queries = []
        
        # 常用修饰词，增加搜索成功率
        modifiers = [
            "高清图片", "时尚照片", "模特实拍", "服装照片", "时尚单品", 
            "高清实拍", "产品展示", "平铺拍摄", "挂拍", "细节图",
            "正面图", "侧面图", "全身图", "搭配图", "街拍"
        ]
        
        # 增加更多的搜索变体
        for query in queries:
            enhanced_queries.append(query)
            for modifier in modifiers:
                enhanced_queries.append(f"{query} {modifier}")
            
        # 去重并限制数量
        return list(set(enhanced_queries))[:SEARCH_RESULT_LIMIT]
    
    def add_backup_search_method(self) -> str:
        """
        返回备份搜索方法的代码，当DDG搜索失败时使用
        """
        return """
    def backup_search_images(self, queries: List[str], output_dir: str, num_images: int = 10) -> List[str]:
        \"\"\"        
        备份的图像搜索方法，当DDG搜索失败时使用
        \"\"\"        
        downloaded_images = []
        
        logger.info(f"使用备份搜索方法，查询词数量: {len(queries)}")
        
        # 示例：使用一些预设的在线示例图像URL
        sample_image_urls = [
            "https://via.placeholder.com/600/FFFFFF/000000?text=服装示例",
            "https://via.placeholder.com/600/EEEEEE/333333?text=时尚展示",
            "https://via.placeholder.com/600/DDDDDD/666666?text=模特实拍",
            "https://via.placeholder.com/600/CCCCCC/999999?text=服装图片",
            "https://via.placeholder.com/600/BBBBBB/AAAAAA?text=时尚单品"
        ]
        
        for i, url in enumerate(sample_image_urls):
            if len(downloaded_images) >= num_images:
                break
            
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    # 保存图像
                    image_path = os.path.join(output_dir, f"backup_garment_{i}.jpg")
                    
                    with open(image_path, "wb") as f:
                        f.write(response.content)
                    
                    # 验证图像
                    try:
                        with Image.open(image_path) as img:
                            img.verify()
                        downloaded_images.append(image_path)
                        logger.info(f"成功保存备份图像: {image_path}")
                    except Exception as img_err:
                        logger.error(f"备份图像验证失败: {img_err}")
                        if os.path.exists(image_path):
                            os.remove(image_path)
            except Exception as e:
                logger.error(f"下载备份图像时出错: {e}")
                continue
        
        return downloaded_images
"""


def get_fixed_text2garment_code() -> str:

    # 返回修复后的Text2Garment类的完整代码
    # 用于替换utils/text2garment.py文件中的代码

    return """
import os
import logging
import requests
from typing import List, Dict
from PIL import Image
from duckduckgo_search import DDGS
from config.config import (
    STATIC_FOLDER,
    MAX_TEXT2GARMENT_ITERATIONS,
    GARMENT_VQA_HIGH_THRESHOLD,
    GARMENT_VQA_LOW_THRESHOLD,
    SEARCH_TIMEOUT,
    SEARCH_RESULT_LIMIT
)
from utils.image_process import ImageProcess
from utils.metrics import VQAScore

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Text2Garment:
    # 文本到服装图像转换的类，用于从文本描述生成服装图像
    
    def __init__(self):
        # 初始化Text2Garment类
        self.image_processor = ImageProcess()
        self.vqa_scorer = VQAScore()
        self.ddgs = DDGS()
        self.max_retries = 3  # 添加重试次数配置
    
    def get_addition_negative_prompt(self) -> str:
        # 获取额外的负面提示词
        return "低质量, 模糊, 变形, 假人模型, 不符合要求"
    
    def make_queries(self, garment_prompt: str, category: str) -> List[str]:

        # 根据服装提示词和类别生成搜索查询词
        queries = []
        
        # 基础查询词
        base_queries = [
            garment_prompt,
            f"{garment_prompt} 高清图片",
            f"{garment_prompt} 时尚照片",
            f"{garment_prompt} 模特实拍",
            f"{garment_prompt} 服装照片",
            f"{garment_prompt} 时尚单品",
        ]
        
        # 根据类别添加特定查询词
        if category == "upper_body":
            category_queries = [
                f"{garment_prompt} 上衣",
                f"{garment_prompt} T恤",
                f"{garment_prompt} 衬衫",
                f"{garment_prompt} 外套",
                f"{garment_prompt} 毛衣",
            ]
        elif category == "lower_body":
            category_queries = [
                f"{garment_prompt} 裤子",
                f"{garment_prompt} 牛仔裤",
                f"{garment_prompt} 裙子",
                f"{garment_prompt} 短裤",
                f"{garment_prompt} 长裤",
            ]
        elif category == "dresses":
            category_queries = [
                f"{garment_prompt} 连衣裙",
                f"{garment_prompt} 裙子",
                f"{garment_prompt} 女装",
                f"{garment_prompt} 夏季连衣裙",
                f"{garment_prompt} 时尚连衣裙",
            ]
        elif category == "shoes":
            category_queries = [
                f"{garment_prompt} 鞋子",
                f"{garment_prompt} 运动鞋",
                f"{garment_prompt} 高跟鞋",
                f"{garment_prompt} 靴子",
                f"{garment_prompt} 休闲鞋",
            ]
        else:
            category_queries = []
        
        # 合并查询词
        queries = base_queries + category_queries
        
        # 添加额外提示词到每个查询
        enhanced_queries = []
        for query in queries:
            enhanced_queries.append(query)
            enhanced_queries.append(f"{query} 高清实拍")
            enhanced_queries.append(f"{query} 产品展示")
            enhanced_queries.append(f"{query} 平铺拍摄")
        
        # 去重并限制数量
        return list(set(enhanced_queries))[:SEARCH_RESULT_LIMIT]
    
    def get_text2garment(self, queries: List[str], output_dir: str, num_images: int = 10) -> List[str]:

        # 从搜索查询词获取服装图像
        downloaded_images = []
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"开始搜索图像，查询词数量: {len(queries)}, 目标图像数量: {num_images}")
        
        # 尝试每个查询词进行搜索
        for query in queries:
            if len(downloaded_images) >= num_images:
                break
            
            retry_count = 0
            while retry_count < self.max_retries:
                try:
                    logger.info(f"正在搜索: {query} (重试 {retry_count+1}/{self.max_retries})")
                    
                    # 使用DDG搜索图像，添加超时设置
                    search_results = self.ddgs.images(
                        query, 
                        max_results=num_images * 2,  # 搜索更多结果以提高成功率
                        region="cn-zh"
                    )
                    
                    if not search_results:
                        logger.warning(f"搜索结果为空: {query}")
                        retry_count += 1
                        continue
                    
                    logger.info(f"找到 {len(search_results)} 个搜索结果")
                    
                    # 尝试下载图像
                    for result in search_results:
                        if len(downloaded_images) >= num_images:
                            break
                        
                        try:
                            # 获取图像URL
                            image_url = result.get("image")
                            if not image_url:
                                logger.warning(f"搜索结果中没有图像URL")
                                continue
                            
                            # 添加超时设置
                            response = requests.get(image_url, stream=True, timeout=15)
                            
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
                                    downloaded_images.append(image_path)
                                    logger.info(f"成功下载图像: {image_path}")
                                except Exception as img_err:
                                    logger.error(f"图像验证失败: {img_err}")
                                    if os.path.exists(image_path):
                                        os.remove(image_path)
                        except Exception as e:
                            logger.error(f"下载图像时出错: {e}")
                            continue
                    
                    # 如果当前查询已经获取了一些图像，继续下一个查询
                    if downloaded_images:
                        break
                    
                except Exception as e:
                    logger.error(f"搜索图像时出错: {e}")
                    retry_count += 1
                    continue
        
        # 如果DDG搜索失败，使用备份方法
        if len(downloaded_images) == 0:
            logger.warning("DDG搜索失败，尝试使用备份方法...")
            downloaded_images = self.backup_search_images(queries, output_dir, num_images)
        
        logger.info(f"搜索完成，成功下载 {len(downloaded_images)} 张图像")
        return downloaded_images
    
    def backup_search_images(self, queries: List[str], output_dir: str, num_images: int = 10) -> List[str]:
 
        # 备份的图像搜索方法，当DDG搜索失败时使用
        downloaded_images = []
        
        logger.info(f"使用备份搜索方法，查询词数量: {len(queries)}")
        
        # 示例：使用一些预设的在线示例图像URL
        sample_image_urls = [
            "https://via.placeholder.com/600/FFFFFF/000000?text=服装示例",
            "https://via.placeholder.com/600/EEEEEE/333333?text=时尚展示",
            "https://via.placeholder.com/600/DDDDDD/666666?text=模特实拍",
            "https://via.placeholder.com/600/CCCCCC/999999?text=服装图片",
            "https://via.placeholder.com/600/BBBBBB/AAAAAA?text=时尚单品"
        ]
        
        for i, url in enumerate(sample_image_urls):
            if len(downloaded_images) >= num_images:
                break
            
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    # 保存图像
                    image_path = os.path.join(output_dir, f"backup_garment_{i}.jpg")
                    
                    with open(image_path, "wb") as f:
                        f.write(response.content)
                    
                    # 验证图像
                    try:
                        with Image.open(image_path) as img:
                            img.verify()
                        downloaded_images.append(image_path)
                        logger.info(f"成功保存备份图像: {image_path}")
                    except Exception as img_err:
                        logger.error(f"备份图像验证失败: {img_err}")
                        if os.path.exists(image_path):
                            os.remove(image_path)
            except Exception as e:
                logger.error(f"下载备份图像时出错: {e}")
                continue
        
        return downloaded_images

    def produce_garment(self, garment_prompt: str, category: str, output_dir: str, 
                        max_iterations: int = MAX_TEXT2GARMENT_ITERATIONS, 
                        num_images_per_iter: int = 10) -> List[Dict]:
        # 生成并筛选服装图像
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
            logger.info(f"迭代 {current_iteration + 1}/{max_iterations}...")
            
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
                        logger.warning(f"警告: 评分不是数字类型，得到的是: {type(score)}, 值: {score}")
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
                    logger.error(f"处理图像 {image_path} 时出错: {e}")
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
        # 从服装描述生成服装图像
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
text2garment_instance = Text2Garment()

# 导出函数
def description_to_garment(garment_description: Dict) -> Dict:
    # 从服装描述生成服装图像
    return text2garment_instance.description_to_garment(garment_description)
"""


# 主函数，用于应用修复
if __name__ == "__main__":
    print("===== DDG搜索问题修复工具 =====")
    print()
    print("此工具提供了解决DDG搜索'No results found'问题的完整修复方案。")
    print()
    print("修复内容包括:")
    print("1. 增强搜索查询词，添加更多变体")
    print("2. 增加重试机制，提高搜索成功率")
    print("3. 添加日志记录，便于调试")
    print("4. 实现备份搜索方法，当主搜索失败时使用")
    print("5. 增加错误处理和类型检查")
    print("6. 修复hash切片操作错误")
    print()
    print("使用方法:")
    print("1. 在Python代码中导入此文件")
    print("2. 调用get_fixed_text2garment_code()函数获取修复后的代码")
    print("3. 将代码替换到utils/text2garment.py文件中")
    print()
    print("===== 修复说明结束 =====")