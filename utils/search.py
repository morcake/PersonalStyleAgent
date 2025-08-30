import os
import json
import requests
from typing import Dict, List, Optional, Union
import ddgs
from bs4 import BeautifulSoup
from config.config import SEARCH_TIMEOUT, SEARCH_RESULT_LIMIT, IMAGE_DOWNLOAD_TIMEOUT

class ClothingSearch:
    def __init__(self):
        self.ddgs = ddgs.DDGS()

    def search_clothing_items(self, query: str, num_results: int = 10) -> List[Dict]:
        """搜索服装商品"""
        try:
            # 确保结果数量不超过配置的上限
            actual_num_results = min(num_results, SEARCH_RESULT_LIMIT)
            
            # 使用DuckDuckGo搜索
            results = self.ddgs.text(query, max_results=actual_num_results)
            
            clothing_items = []
            
            for i, result in enumerate(results):
                # 提取商品信息
                item = {
                    "id": i,
                    "title": result.get("title", ""),
                    "description": result.get("body", ""),
                    "url": result.get("href", ""),
                    "source": result.get("source", "")
                }
                
                # 尝试从URL中提取更多信息
                try:
                    # 注意：实际应用中应该限制请求次数和超时时间
                    # 这里只是一个示例，不应该在生产环境中直接使用
                    # response = requests.get(item["url"], timeout=5)
                    # soup = BeautifulSoup(response.text, "html.parser")
                    # # 尝试提取价格、图片等信息
                    # # 这部分需要根据不同网站的HTML结构进行调整
                    # ...
                    pass
                except Exception as e:
                    print(f"解析商品页面时出错: {e}")
                
                clothing_items.append(item)
            
            return clothing_items
        except Exception as e:
            print(f"搜索服装商品时出错: {e}")
            return []

    def search_by_category(self, category: str, num_results: int = 10) -> List[Dict]:
        """按类别搜索服装商品"""
        # 构建类别查询词
        category_map = {
            "upper_body": "时尚上衣 新款",
            "lower_body": "时尚下装 新款",
            "dresses": "时尚连衣裙 新款",
            "shoes": "时尚鞋子 新款",
            "hat": "时尚帽子 新款",
            "glasses": "时尚眼镜 新款",
            "belt": "时尚腰带 新款",
            "scarf": "时尚围巾 新款"
        }
        
        query = category_map.get(category, category)
        return self.search_clothing_items(query, num_results)

    def search_by_style(self, style: str, num_results: int = 10) -> List[Dict]:
        """按风格搜索服装商品"""
        query = f"{style} 风格服装 新款"
        return self.search_clothing_items(query, num_results)

    def search_by_price_range(self, min_price: float, max_price: float, num_results: int = 10) -> List[Dict]:
        """按价格范围搜索服装商品"""
        query = f"服装 价格{min_price}-{max_price}元 新款"
        return self.search_clothing_items(query, num_results)

    def get_product_details(self, product_url: str) -> Dict:
        """获取商品详细信息"""
        try:
            # 发送请求
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(product_url, headers=headers, timeout=IMAGE_DOWNLOAD_TIMEOUT)
            
            # 解析HTML
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 提取商品信息（这部分需要根据不同网站的HTML结构进行调整）
            title = soup.find("h1").text.strip() if soup.find("h1") else ""
            price = soup.find("span", class_="price").text.strip() if soup.find("span", class_="price") else ""
            description = soup.find("div", class_="description").text.strip() if soup.find("div", class_="description") else ""
            
            # 提取图片
            images = []
            for img in soup.find_all("img"):
                img_url = img.get("src", "")
                if img_url.startswith("//"):
                    img_url = "https:" + img_url
                elif not img_url.startswith("http"):
                    # 处理相对路径
                    from urllib.parse import urljoin
                    img_url = urljoin(product_url, img_url)
                images.append(img_url)
            
            # 提取尺码和颜色
            sizes = []
            colors = []
            
            # 构建商品详情
            product_details = {
                "title": title,
                "price": price,
                "description": description,
                "url": product_url,
                "images": images,
                "sizes": sizes,
                "colors": colors
            }
            
            return product_details
        except Exception as e:
            print(f"获取商品详情时出错: {e}")
            return {
                "title": "",
                "price": "",
                "description": "",
                "url": product_url,
                "images": [],
                "sizes": [],
                "colors": []
            }

# 创建全局实例
clothing_search_instance = ClothingSearch()

# 导出函数
def search_clothing_items(query: str, num_results: int = 10) -> List[Dict]:
    """搜索服装商品"""
    return clothing_search_instance.search_clothing_items(query, num_results)