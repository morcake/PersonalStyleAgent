import unittest
import os
import json
from unittest.mock import patch, MagicMock
from typing import Union, Dict, List

# 导入被测类
from app import PersonalStyleAgentApp

class TestPersonalStyleAgentFix(unittest.TestCase):
    
    def setUp(self):
        """测试前的设置"""
        # 创建应用实例
        self.app = PersonalStyleAgentApp()
        
        # 模拟StyleAgent，避免实际调用外部服务
        self.mock_style_agent = MagicMock()
        self.app.style_agent = self.mock_style_agent
        
        # 模拟成功的服装生成结果
        self.valid_garment_result = {
            "category": "upper_body",
            "prompt": "休闲风格的白色T恤",
            "garments": [
                {"id": 0, "path": "/path/to/image1.jpg", "score": 0.9, "relative_path": "garments/image1.jpg"},
                {"id": 1, "path": "/path/to/image2.jpg", "score": 0.85, "relative_path": "garments/image2.jpg"},
                {"id": 2, "path": "/path/to/image3.jpg", "score": 0.8, "relative_path": "garments/image3.jpg"}
            ]
        }
        
        # 模拟空结果
        self.empty_garment_result = {
            "category": "upper_body",
            "prompt": "休闲风格的白色T恤",
            "garments": []
        }
        
        # 模拟非字典结果
        self.non_dict_result = "error"
        
        # 模拟非列表garments
        self.non_list_garments = {
            "category": "upper_body",
            "prompt": "休闲风格的白色T恤",
            "garments": "not a list"
        }
    
    def test_generate_clothing_with_string_description(self):
        """测试使用字符串描述生成服装图像"""
        # 设置mock返回值
        self.mock_style_agent.generate_clothing_images.return_value = self.valid_garment_result
        
        # 调用被测方法
        result = self.app.generate_clothing("休闲风格的白色T恤")
        
        # 验证结果
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], "/path/to/image1.jpg")
        self.assertEqual(result[1], "/path/to/image2.jpg")
        self.assertEqual(result[2], "/path/to/image3.jpg")
        
        # 验证调用参数
        self.mock_style_agent.generate_clothing_images.assert_called_once_with({
            "category": "upper_body",
            "prompt": "休闲风格的白色T恤"
        })
    
    def test_generate_clothing_with_dict_description(self):
        """测试使用字典描述生成服装图像"""
        # 设置mock返回值
        self.mock_style_agent.generate_clothing_images.return_value = self.valid_garment_result
        
        # 调用被测方法
        description = {
            "category": "lower_body",
            "prompt": "牛仔裤"
        }
        result = self.app.generate_clothing(description)
        
        # 验证结果
        self.assertEqual(len(result), 3)
        
        # 验证调用参数
        self.mock_style_agent.generate_clothing_images.assert_called_once_with(description)
    
    def test_generate_clothing_with_empty_result(self):
        """测试生成空结果的情况"""
        # 设置mock返回值
        self.mock_style_agent.generate_clothing_images.return_value = self.empty_garment_result
        
        # 调用被测方法
        result = self.app.generate_clothing("休闲风格的白色T恤")
        
        # 验证结果
        self.assertEqual(len(result), 0)
    
    def test_generate_clothing_with_non_dict_result(self):
        """测试generate_clothing_images返回非字典类型的情况"""
        # 设置mock返回值
        self.mock_style_agent.generate_clothing_images.return_value = self.non_dict_result
        
        # 调用被测方法
        result = self.app.generate_clothing("休闲风格的白色T恤")
        
        # 验证结果
        self.assertEqual(len(result), 0)
        # 验证状态更新
        self.assertEqual(self.app.generated_clothing_images, {
            "category": "upper_body",
            "prompt": "休闲风格的白色T恤",
            "garments": []
        })
    
    def test_generate_clothing_with_non_list_garments(self):
        """测试garments字段不是列表的情况"""
        # 设置mock返回值
        self.mock_style_agent.generate_clothing_images.return_value = self.non_list_garments
        
        # 调用被测方法
        result = self.app.generate_clothing("休闲风格的白色T恤")
        
        # 验证结果
        self.assertEqual(len(result), 0)
    
    def test_select_clothing_with_valid_index(self):
        """测试使用有效索引选择服装"""
        # 设置生成的服装图像
        self.app.generated_clothing_images = self.valid_garment_result
        
        # 调用被测方法
        result = self.app.select_clothing(1)
        
        # 验证结果
        self.assertEqual(result, self.valid_garment_result["garments"][1])
        self.assertEqual(self.app.selected_clothing, self.valid_garment_result["garments"][1])
    
    def test_select_clothing_with_invalid_index(self):
        """测试使用无效索引选择服装"""
        # 设置生成的服装图像
        self.app.generated_clothing_images = self.valid_garment_result
        
        # 调用被测方法
        result = self.app.select_clothing(10)
        
        # 验证结果
        self.assertEqual(result, {"error": "无效的服装索引"})
    
    def test_select_clothing_with_empty_garments(self):
        """测试没有可用服装的情况"""
        # 设置生成的服装图像
        self.app.generated_clothing_images = self.empty_garment_result
        
        # 调用被测方法
        result = self.app.select_clothing(0)
        
        # 验证结果
        self.assertEqual(result, {"error": "无效的服装索引"})
    
    def test_select_clothing_with_non_dict_generated_clothing(self):
        """测试generated_clothing_images不是字典的情况"""
        # 设置生成的服装图像为非字典类型
        self.app.generated_clothing_images = "not a dict"
        
        # 调用被测方法
        result = self.app.select_clothing(0)
        
        # 验证结果
        self.assertEqual(result, {"error": "没有可用的服装图像"})
    
    def test_generate_clothing_without_description(self):
        """测试不提供描述的情况"""
        # 设置当前风格分析结果
        self.app.current_style_analysis = {
            "clothing_description": "时尚连衣裙"
        }
        
        # 设置mock返回值
        self.mock_style_agent.generate_clothing_images.return_value = self.valid_garment_result
        
        # 调用被测方法
        result = self.app.generate_clothing()
        
        # 验证结果
        self.assertEqual(len(result), 3)

# 快速功能测试函数
def run_quick_test():
    print("==== 快速功能测试 ====")
    
    try:
        # 初始化应用
        app = PersonalStyleAgentApp()
        print("应用初始化成功")
        
        # 模拟StyleAgent
        mock_style_agent = MagicMock()
        
        # 设置mock返回值为有效的服装结果
        valid_result = {
            "category": "upper_body",
            "prompt": "休闲风格的白色T恤",
            "garments": [
                {"id": 0, "path": "/path/to/image1.jpg", "score": 0.9, "relative_path": "garments/image1.jpg"},
                {"id": 1, "path": "/path/to/image2.jpg", "score": 0.85, "relative_path": "garments/image2.jpg"}
            ]
        }
        mock_style_agent.generate_clothing_images.return_value = valid_result
        
        # 替换app中的style_agent
        app.style_agent = mock_style_agent
        
        # 测试generate_clothing方法
        print("测试generate_clothing方法...")
        result = app.generate_clothing("休闲风格的白色T恤")
        print(f"generate_clothing结果: {result}")
        print(f"generated_clothing_images: {app.generated_clothing_images}")
        
        # 测试select_clothing方法
        print("测试select_clothing方法...")
        selected = app.select_clothing(0)
        print(f"select_clothing结果: {selected}")
        print(f"selected_clothing: {app.selected_clothing}")
        
        # 测试无效索引
        print("测试无效索引...")
        invalid_selected = app.select_clothing(10)
        print(f"无效索引结果: {invalid_selected}")
        
        print("==== 快速测试完成 ====")
        return True
    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        print("==== 快速测试失败 ====")
        return False

if __name__ == "__main__":
    print("运行单元测试...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    print("\n运行快速功能测试...")
    run_quick_test()