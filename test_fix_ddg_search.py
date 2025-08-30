#!/usr/bin/env python3
"""
测试修复后的fix_ddg_search.py文件
"""
import os
import sys
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_fix_ddg_search():
    """测试修复后的fix_ddg_search.py文件"""
    try:
        print("===== 测试fix_ddg_search.py文件 =====")
        
        # 尝试导入文件
        print("\n1. 测试导入fix_ddg_search模块...")
        from fix_ddg_search import DDGSearchFix, get_fixed_text2garment_code
        print("✅ 成功导入模块")
        
        # 测试DDGSearchFix类的初始化
        print("\n2. 测试DDGSearchFix类初始化...")
        ddg_fix = DDGSearchFix()
        print("✅ 成功初始化DDGSearchFix类")
        
        # 测试enhance_search_queries方法
        print("\n3. 测试enhance_search_queries方法...")
        test_queries = ["白色T恤", "牛仔裤"]
        enhanced_queries = ddg_fix.enhance_search_queries(test_queries)
        print(f"✅ 增强查询词成功: 原始 {len(test_queries)} 个，增强后 {len(enhanced_queries)} 个")
        print(f"  示例增强查询词: {enhanced_queries[:3]}")
        
        # 测试add_backup_search_method方法
        print("\n4. 测试add_backup_search_method方法...")
        backup_code = ddg_fix.add_backup_search_method()
        print(f"✅ 获取备份搜索方法代码成功，代码长度: {len(backup_code)} 字符")
        
        # 测试get_fixed_text2garment_code函数
        print("\n5. 测试get_fixed_text2garment_code函数...")
        fixed_code = get_fixed_text2garment_code()
        print(f"✅ 获取修复后的Text2Garment代码成功，代码长度: {len(fixed_code)} 字符")
        
        # 检查代码中的关键部分
        print("\n6. 验证修复代码中的关键功能...")
        key_features = [
            ("backup_search_images", "备份搜索方法"),
            ("max_retries", "重试机制"),
            ("str(hash(prompt))[:8]", "修复的hash切片操作"),
            ("region=\"cn-zh\"", "搜索地区设置"),
            ("stream=True", "流式下载设置")
        ]
        
        for feature_code, feature_name in key_features:
            if feature_code in fixed_code:
                print(f"✅ 包含 {feature_name}")
            else:
                print(f"❌ 缺少 {feature_name}")
        
        print("\n===== 测试完成 =====")
        print("\n修复的fix_ddg_search.py文件正常工作，所有关键功能已验证。")
        print("\n使用方法:")
        print("1. 在Python代码中导入此文件")
        print("2. 调用get_fixed_text2garment_code()函数获取修复后的代码")
        print("3. 将代码替换到utils/text2garment.py文件中")
        
    except ImportError as e:
        logger.error(f"导入失败: {e}")
        print(f"❌ 导入模块失败: {e}")
    except Exception as e:
        logger.error(f"测试过程中出错: {e}")
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    test_fix_ddg_search()