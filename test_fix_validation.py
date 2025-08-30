#!/usr/bin/env python3
"""
测试文件：验证'int object is not subscriptable'错误修复
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.text2garment import description_to_garment

print("===== 验证'int object is not subscriptable'错误修复 =====")
print()

# 测试数据
test_garment_description = {
    'category': 'upper_body',
    'prompt': '简约风格的白色T恤'
}

print(f"测试数据: {test_garment_description}")
print()

# 测试修复后的功能
try:
    print("调用修复后的description_to_garment函数...")
    result = description_to_garment(test_garment_description)
    print("测试成功！没有出现'int object is not subscriptable'错误")
    print()
    print("结果信息:")
    print(f"- 类别: {result.get('category')}")
    print(f"- 提示词: {result.get('prompt')}")
    print(f"- 生成的服装数量: {len(result.get('garments', []))}")
    
    # 检查是否生成了有效的服装图像
    if result.get('garments') and len(result.get('garments')) > 0:
        print("\n生成的服装图像示例:")
        for i, garment in enumerate(result.get('garments')[:2]):  # 只显示前2个
            print(f"  服装 {i+1}:")
            print(f"    ID: {garment.get('id')}")
            print(f"    路径: {garment.get('path')}")
            print(f"    分数: {garment.get('score')}")
            print(f"    相对路径: {garment.get('relative_path')}")
    else:
        print("\n注意: 没有生成服装图像，但这不是本次修复的问题范围")
        print("      这可能是因为图像下载或评估过程中出现了其他问题")
        
except Exception as e:
    print(f"测试失败: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print()
print("===== 测试完成 =====")