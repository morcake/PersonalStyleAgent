import os
import json
from typing import Dict, List, Optional, Union
from utils.search import search_clothing_items, ClothingSearch
from config.config import STATIC_FOLDER

class ClothingRecommendationAgent:
    def __init__(self):
        # 初始化搜索组件
        self.clothing_search = ClothingSearch()

    def recommend_by_style(self, style: str, num_results: int = 10) -> List[Dict]:
        """根据风格推荐服装"""
        try:
            # 调用搜索组件按风格搜索
            recommendations = self.clothing_search.search_by_style(style, num_results)
            print(f"根据风格 '{style}' 推荐了 {len(recommendations)} 件服装")
            return recommendations
        except Exception as e:
            print(f"按风格推荐时出错: {e}")
            return []

    def recommend_by_category(self, category: str, num_results: int = 10) -> List[Dict]:
        """根据类别推荐服装"""
        try:
            # 调用搜索组件按类别搜索
            recommendations = self.clothing_search.search_by_category(category, num_results)
            print(f"根据类别 '{category}' 推荐了 {len(recommendations)} 件服装")
            return recommendations
        except Exception as e:
            print(f"按类别推荐时出错: {e}")
            return []

    def recommend_by_price_range(self, min_price: float, max_price: float, num_results: int = 10) -> List[Dict]:
        """根据价格范围推荐服装"""
        try:
            # 调用搜索组件按价格范围搜索
            recommendations = self.clothing_search.search_by_price_range(min_price, max_price, num_results)
            print(f"根据价格范围 '{min_price}-{max_price}' 推荐了 {len(recommendations)} 件服装")
            return recommendations
        except Exception as e:
            print(f"按价格范围推荐时出错: {e}")
            return []

    def recommend_by_preference(self, user_preference: Dict, num_results: int = 10) -> List[Dict]:
        """根据用户偏好推荐服装"""
        try:
            # 从用户偏好中提取关键词
            keywords = []
            
            # 提取风格
            if "style" in user_preference:
                keywords.append(user_preference["style"])
            
            # 提取颜色
            if "color" in user_preference:
                keywords.append(user_preference["color"])
            
            # 提取类别
            if "category" in user_preference:
                keywords.append(user_preference["category"])
            
            # 提取材质
            if "material" in user_preference:
                keywords.append(user_preference["material"])
            
            # 构建搜索查询
            query = " ".join(keywords) if keywords else "时尚服装 新款"
            
            # 进行搜索
            recommendations = search_clothing_items(query, num_results)
            
            # 如果设置了价格范围，进一步筛选
            if "min_price" in user_preference and "max_price" in user_preference:
                # 注意：这里只是一个示例，实际应用中需要更复杂的价格筛选逻辑
                pass
            
            print(f"根据用户偏好推荐了 {len(recommendations)} 件服装")
            return recommendations
        except Exception as e:
            print(f"按用户偏好推荐时出错: {e}")
            return []

    def get_detailed_product_info(self, product_url: str) -> Dict:
        """获取商品详细信息"""
        try:
            # 调用搜索组件获取商品详细信息
            product_info = self.clothing_search.get_product_details(product_url)
            print(f"获取商品详细信息成功")
            return product_info
        except Exception as e:
            print(f"获取商品详细信息时出错: {e}")
            return {
                "title": "",
                "price": "",
                "description": "",
                "url": product_url,
                "images": [],
                "sizes": [],
                "colors": []
            }

    def filter_recommendations(self, recommendations: List[Dict], filters: Dict) -> List[Dict]:
        """筛选推荐结果"""
        try:
            filtered_results = recommendations
            
            # 按评分筛选
            if "min_rating" in filters:
                # 注意：这里只是一个示例，实际应用中需要有评分数据才能筛选
                pass
            
            # 按价格筛选
            if "min_price" in filters and "max_price" in filters:
                # 注意：这里只是一个示例，实际应用中需要有价格数据才能筛选
                pass
            
            # 按品牌筛选
            if "brands" in filters:
                # 注意：这里只是一个示例，实际应用中需要有品牌数据才能筛选
                pass
            
            print(f"筛选后剩余 {len(filtered_results)} 件服装")
            return filtered_results
        except Exception as e:
            print(f"筛选推荐结果时出错: {e}")
            return recommendations

    def sort_recommendations(self, recommendations: List[Dict], sort_by: str = "relevance", 
                            ascending: bool = False) -> List[Dict]:
        """排序推荐结果"""
        try:
            # 复制推荐结果以避免修改原始列表
            sorted_results = recommendations.copy()
            
            # 根据指定的字段排序
            if sort_by == "price":
                # 注意：这里只是一个示例，实际应用中需要有价格数据才能排序
                pass
            elif sort_by == "rating":
                # 注意：这里只是一个示例，实际应用中需要有评分数据才能排序
                pass
            elif sort_by == "newest":
                # 注意：这里只是一个示例，实际应用中需要有日期数据才能排序
                pass
            
            print(f"推荐结果已按 '{sort_by}' 排序")
            return sorted_results
        except Exception as e:
            print(f"排序推荐结果时出错: {e}")
            return recommendations

    def generate_outfit_recommendation(self, user_preference: Dict, num_outfits: int = 3) -> List[Dict]:
        """生成整套服装搭配推荐"""
        try:
            outfits = []
            
            for i in range(num_outfits):
                outfit = {
                    "id": i,
                    "name": f"搭配方案 {i+1}",
                    "items": [],
                    "description": ""
                }
                
                # 为简化实现，这里只生成一个示例搭配
                # 在实际应用中，应该根据用户偏好和时尚搭配规则生成合理的搭配
                outfit["items"] = [
                    {
                        "type": "upper_body",
                        "description": "白色棉质T恤",
                        "image_url": "",
                        "product_url": ""
                    },
                    {
                        "type": "lower_body",
                        "description": "蓝色牛仔裤",
                        "image_url": "",
                        "product_url": ""
                    },
                    {
                        "type": "shoes",
                        "description": "白色运动鞋",
                        "image_url": "",
                        "product_url": ""
                    }
                ]
                
                outfit["description"] = "简约休闲风格，适合日常穿着"
                
                outfits.append(outfit)
            
            print(f"生成了 {len(outfits)} 套服装搭配推荐")
            return outfits
        except Exception as e:
            print(f"生成服装搭配推荐时出错: {e}")
            return []

    def save_recommendations(self, recommendations: List[Dict], output_path: str) -> bool:
        """保存推荐结果到文件"""
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 保存结果为JSON文件
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(recommendations, f, ensure_ascii=False, indent=2)
            
            print(f"推荐结果已保存到: {output_path}")
            return True
        except Exception as e:
            print(f"保存推荐结果时出错: {e}")
            return False

    def load_recommendations(self, recommendations_path: str) -> List[Dict]:
        """从文件加载推荐结果"""
        try:
            # 检查文件是否存在
            if not os.path.exists(recommendations_path):
                print(f"推荐结果文件不存在: {recommendations_path}")
                return []
            
            # 加载JSON文件
            with open(recommendations_path, "r", encoding="utf-8") as f:
                recommendations = json.load(f)
            
            return recommendations
        except Exception as e:
            print(f"加载推荐结果时出错: {e}")
            return []