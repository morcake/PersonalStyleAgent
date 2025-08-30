#!/usr/bin/env python3
"""
测试脚本：验证DDG搜索"No results found"问题的修复效果
"""
import sys
import os
import logging
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入修复工具
from fix_ddg_search import DDGSearchFix

# 临时导入text2garment模块进行测试
try:
    from utils.text2garment import Text2Garment, description_to_garment
    print("成功导入原始text2garment模块")
except ImportError as e:
    print(f"导入原始模块失败: {e}")
    print("请确保先应用修复方案")
    sys.exit(1)

def create_test_output_dir():
    """创建测试输出目录"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "test_outputs", timestamp)
    os.makedirs(test_dir, exist_ok=True)
    return test_dir

def test_enhanced_queries():
    """测试增强的搜索查询词生成"""
    print("\n===== 测试增强的搜索查询词 =====")
    
    # 测试用例
    test_cases = [
        ("简约风格的白色T恤", "upper_body"),
        ("牛仔裤", "lower_body"),
        ("夏季连衣裙", "dresses"),
        ("运动鞋", "shoes")
    ]
    
    for prompt, category in test_cases:
        print(f"\n测试提示词: '{prompt}' (类别: {category})")
        
        # 创建原始查询词
        original_queries = []
        if category == "upper_body":
            original_queries = [f"{prompt}", f"{prompt} 高清图片", f"{prompt} 时尚照片", f"{prompt} 模特实拍", f"{prompt} 上衣"]
        elif category == "lower_body":
            original_queries = [f"{prompt}", f"{prompt} 高清图片", f"{prompt} 时尚照片", f"{prompt} 模特实拍", f"{prompt} 下装"]
        elif category == "dresses":
            original_queries = [f"{prompt}", f"{prompt} 高清图片", f"{prompt} 时尚照片", f"{prompt} 模特实拍", f"{prompt} 连衣裙"]
        elif category == "shoes":
            original_queries = [f"{prompt}", f"{prompt} 高清图片", f"{prompt} 时尚照片", f"{prompt} 模特实拍", f"{prompt} 鞋子"]
        
        # 增强查询词
        enhanced_queries = DDGSearchFix.enhance_search_queries(original_queries)
        
        print(f"原始查询词数量: {len(original_queries)}")
        print(f"增强后查询词数量: {len(enhanced_queries)}")
        print(f"新增查询词数量: {len(enhanced_queries) - len(original_queries)}")
        
        # 打印部分增强后的查询词示例
        print("增强后的查询词示例:")
        for i, query in enumerate(enhanced_queries[:5]):  # 只显示前5个
            print(f"  {i+1}. {query}")

def test_text2garment_search():
    """测试Text2Garment的搜索功能"""
    print("\n===== 测试Text2Garment搜索功能 =====")
    
    # 初始化Text2Garment实例
    text2garment = Text2Garment()
    
    # 测试用例
    test_cases = [
        {"category": "upper_body", "prompt": "简约风格的白色T恤"},
        {"category": "lower_body", "prompt": "修身牛仔裤"}
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n测试用例 {i+1}/{len(test_cases)}: {test_case}")
        
        # 创建测试输出目录
        test_dir = create_test_output_dir()
        print(f"测试输出目录: {test_dir}")
        
        try:
            # 构建查询词
            queries = text2garment.make_queries(
                test_case["prompt"], 
                test_case["category"]
            )
            print(f"构建的查询词数量: {len(queries)}")
            
            # 执行搜索
            print("执行图像搜索...")
            downloaded_images = text2garment.get_text2garment(queries, test_dir, num_images=5)
            
            print(f"成功下载的图像数量: {len(downloaded_images)}")
            
            if downloaded_images:
                print("下载的图像路径:")
                for img_path in downloaded_images:
                    print(f"  - {img_path}")
            else:
                print("警告: 没有下载到任何图像")
                
        except Exception as e:
            print(f"测试失败: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

def test_full_description_to_garment():
    """测试完整的description_to_garment函数"""
    print("\n===== 测试完整的description_to_garment函数 =====")
    
    # 测试用例
    test_case = {"category": "upper_body", "prompt": "简约风格的白色T恤"}
    print(f"测试用例: {test_case}")
    
    try:
        print("执行description_to_garment函数...")
        result = description_to_garment(test_case)
        
        print(f"函数执行结果: {type(result)}")
        if isinstance(result, dict):
            print(f"结果包含的键: {list(result.keys())}")
            print(f"生成的服装数量: {len(result.get('garments', []))}")
            
            if result.get('garments'):
                print("生成的服装详情:")
                for i, garment in enumerate(result['garments']):
                    print(f"  服装 {i+1}:")
                    print(f"    ID: {garment.get('id')}")
                    print(f"    路径: {garment.get('path')}")
                    print(f"    分数: {garment.get('score')}")
                    print(f"    相对路径: {garment.get('relative_path')}")
    except Exception as e:
        print(f"测试失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

def apply_fix_and_test():
    """应用修复并进行测试"""
    print("\n===== 应用修复并进行测试 =====")
    
    # 获取修复后的代码
    fixed_code = DDGSearchFix.get_fixed_text2garment_code()
    
    # 备份原始文件
    original_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils", "text2garment.py")
    backup_file_path = original_file_path + ".backup"
    
    try:
        # 读取原始文件内容
        with open(original_file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # 备份原始文件
        with open(backup_file_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"已备份原始文件到: {backup_file_path}")
        
        # 应用修复
        with open(original_file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_code)
        print(f"已应用修复到: {original_file_path}")
        
        # 重新导入模块以加载修复后的代码
        print("重新导入模块以加载修复后的代码...")
        import importlib
        import utils.text2garment
        importlib.reload(utils.text2garment)
        from utils.text2garment import Text2Garment, description_to_garment
        
        print("修复应用成功！现在执行测试...")
        
        # 执行测试
        test_text2garment_search()
        test_full_description_to_garment()
        
    except Exception as e:
        print(f"应用修复时出错: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        
        # 如果出错，尝试恢复原始文件
        try:
            if os.path.exists(backup_file_path):
                with open(backup_file_path, 'r', encoding='utf-8') as f:
                    backup_content = f.read()
                with open(original_file_path, 'w', encoding='utf-8') as f:
                    f.write(backup_content)
                print(f"已恢复原始文件: {original_file_path}")
        except Exception as restore_err:
            print(f"恢复原始文件时出错: {restore_err}")

def main():
    """主函数"""
    print("===== DDG搜索问题修复测试工具 =====")
    print()
    print("请选择测试选项:")
    print("1. 仅测试增强的搜索查询词")
    print("2. 测试原始Text2Garment的搜索功能")
    print("3. 测试完整的description_to_garment函数")
    print("4. 应用修复并进行完整测试")
    print("0. 退出")
    
    while True:
        try:
            choice = input("\n请输入选项编号: ")
            if choice == "1":
                test_enhanced_queries()
            elif choice == "2":
                test_text2garment_search()
            elif choice == "3":
                test_full_description_to_garment()
            elif choice == "4":
                print("警告: 此选项将修改utils/text2garment.py文件")
                confirm = input("确定要继续吗？(y/n): ")
                if confirm.lower() == 'y':
                    apply_fix_and_test()
                else:
                    print("已取消操作")
            elif choice == "0":
                print("退出程序")
                break
            else:
                print("无效的选项，请重新输入")
        except KeyboardInterrupt:
            print("\n用户中断操作")
            break
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    main()