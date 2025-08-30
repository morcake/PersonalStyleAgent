#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细调试'int object is not subscriptable'错误的脚本
"""
import sys
import os
import traceback
from typing import Dict, List

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入关键模块
from utils.text2garment import Text2Garment, description_to_garment
from utils.metrics import VQAScore
from agents.style_agent import StyleAgent

# 配置调试环境
DEBUG_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "debug_output")
os.makedirs(DEBUG_FOLDER, exist_ok=True)

print("\n===== 开始调试'int object is not subscriptable'错误 =====\n")

# 创建测试数据
test_garment_description = {
    "category": "upper_body",
    "prompt": "简约风格的白色T恤"
}

print(f"测试数据: {test_garment_description}")
print("\n=== 1. 直接测试Text2Garment类 ===")

# 测试Text2Garment类
try:
    text2garment = Text2Garment()
    print("Text2Garment实例创建成功")
    
    # 测试description_to_garment方法
    print("\n调用text2garment.description_to_garment...")
    result = text2garment.description_to_garment(test_garment_description)
    print(f"结果类型: {type(result)}")
    if isinstance(result, dict):
        print(f"  包含的键: {list(result.keys())}")
        garments = result.get("garments", [])
        print(f"  garments类型: {type(garments)}")
        if isinstance(garments, list):
            print(f"  garments长度: {len(garments)}")
            for i, garment in enumerate(garments):
                print(f"  服装 {i+1} 类型: {type(garment)}")
                if isinstance(garment, dict):
                    print(f"    服装 {i+1} 键: {list(garment.keys())}")
                else:
                    print(f"    警告: 服装 {i+1} 不是字典类型")
        else:
            print("  错误: garments不是列表类型")
    else:
        print("  错误: 结果不是字典类型")
except Exception as e:
    print(f"\nText2Garment测试失败: {e}")
    print("\n错误堆栈:")
    traceback.print_exc()

print("\n=== 2. 测试导出的description_to_garment函数 ===")

# 测试导出的description_to_garment函数
try:
    print("调用导出的description_to_garment函数...")
    result = description_to_garment(test_garment_description)
    print(f"结果类型: {type(result)}")
    if isinstance(result, dict):
        print(f"  包含的键: {list(result.keys())}")
        garments = result.get("garments", [])
        print(f"  garments类型: {type(garments)}")
        if isinstance(garments, list):
            print(f"  garments长度: {len(garments)}")
            for i, garment in enumerate(garments):
                print(f"  服装 {i+1} 类型: {type(garment)}")
                if isinstance(garment, dict):
                    print(f"    服装 {i+1} 键: {list(garment.keys())}")
                else:
                    print(f"    警告: 服装 {i+1} 不是字典类型")
        else:
            print("  错误: garments不是列表类型")
    else:
        print("  错误: 结果不是字典类型")
except Exception as e:
    print(f"\ndescription_to_garment测试失败: {e}")
    print("\n错误堆栈:")
    traceback.print_exc()

print("\n=== 3. 测试StyleAgent类 ===")

# 测试StyleAgent类
try:
    style_agent = StyleAgent()
    print("StyleAgent实例创建成功")
    
    # 测试generate_clothing_images方法
    print("\n调用style_agent.generate_clothing_images...")
    result = style_agent.generate_clothing_images(test_garment_description)
    print(f"结果类型: {type(result)}")
    if isinstance(result, dict):
        print(f"  包含的键: {list(result.keys())}")
        garments = result.get("garments", [])
        print(f"  garments类型: {type(garments)}")
        if isinstance(garments, list):
            print(f"  garments长度: {len(garments)}")
            for i, garment in enumerate(garments):
                print(f"  服装 {i+1} 类型: {type(garment)}")
                if isinstance(garment, dict):
                    print(f"    服装 {i+1} 键: {list(garment.keys())}")
                else:
                    print(f"    警告: 服装 {i+1} 不是字典类型")
        else:
            print("  错误: garments不是列表类型")
    else:
        print("  错误: 结果不是字典类型")
except Exception as e:
    print(f"\nStyleAgent测试失败: {e}")
    print("\n错误堆栈:")
    traceback.print_exc()

print("\n=== 4. 单独测试VQAScore类 ===")

# 单独测试VQAScore类
try:
    vqa_scorer = VQAScore()
    print("VQAScore实例创建成功")
    
    # 创建一个临时图像用于测试
    temp_image_path = os.path.join(DEBUG_FOLDER, "test_image.jpg")
    print(f"创建临时测试图像: {temp_image_path}")
    
    # 测试VQAScore的score方法
    print("\n调用vqa_scorer.score方法...")
    # 注意：由于我们没有实际的图像，这里可能会返回默认分数
    try:
        score = vqa_scorer.score(temp_image_path, "测试描述")
        print(f"评分结果类型: {type(score)}")
        print(f"评分结果值: {score}")
    except FileNotFoundError:
        print("无法找到测试图像，使用默认评分")
        # 创建一个模拟的image_path来测试错误处理
        try:
            # 这应该会触发文件不存在的错误处理
            score = vqa_scorer.score("non_existent_image.jpg", "测试描述")
            print(f"评分结果类型: {type(score)}")
            print(f"评分结果值: {score}")
        except Exception as inner_e:
            print(f"VQAScore测试内部错误: {inner_e}")
except Exception as e:
    print(f"\nVQAScore测试失败: {e}")
    print("\n错误堆栈:")
    traceback.print_exc()

print("\n===== 调试完成 =====")
print("\n调试总结:")
print("1. 如果在任何测试阶段出现'int object is not subscriptable'错误，")
print("   请查看错误堆栈以确定具体的错误位置。")
print("2. 特别注意各函数的返回值类型和数据结构是否符合预期。")
print("3. 检查是否有函数返回了整数而不是预期的字典或列表。")