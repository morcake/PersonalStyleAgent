import os
import sys
import time
import json
from PIL import Image

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入新创建的模型生成模块
from utils.model_based_text2garment import Text2GarmentGenerator, description_to_garment

# 配置日志
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_model_based_text2garment")

def test_text2garment_generator():
    """测试Text2GarmentGenerator类的核心功能"""
    logger.info("开始测试Text2GarmentGenerator类...")
    
    # 创建Text2GarmentGenerator实例
    generator = Text2GarmentGenerator()
    
    # 测试模型加载状态
    logger.info(f"模型加载状态: {'已加载' if generator.pipeline is not None else '未加载'}")
    
    # 定义测试服装描述
    test_garment_description = """
    简约风格的白色T恤，棉质面料，圆领设计，短袖款式，休闲版型，适合夏季穿着
    """
    
    # 创建临时输出目录
    test_output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_output")
    os.makedirs(test_output_dir, exist_ok=True)
    
    # 测试单一图像生成
    logger.info("测试单一图像生成...")
    test_image_path = os.path.join(test_output_dir, "test_garment_single.png")
    generated_path = generator.generate_garment_image(test_garment_description, test_image_path)
    
    if generated_path and os.path.exists(generated_path):
        logger.info(f"成功生成单一图像并保存至: {generated_path}")
        # 验证图像大小
        with Image.open(generated_path) as img:
            logger.info(f"生成的图像尺寸: {img.size}")
    else:
        logger.warning("未能生成单一图像")
    
    # 测试批量图像生成与筛选
    logger.info("测试批量图像生成与筛选...")
    garment_dict = {
        "category": "upper_body",
        "prompt": test_garment_description
    }
    
    # 测试produce_garment方法
    garment_images = generator.produce_garment(
        garment_prompt=garment_dict["prompt"],
        category=garment_dict["category"],
        output_dir=test_output_dir,
        max_iterations=1,  # 减少迭代次数以加快测试
        num_images_per_iter=3  # 减少每次迭代生成的图像数量
    )
    
    logger.info(f"批量生成了 {len(garment_images)} 张服装图像")
    for i, garment in enumerate(garment_images):
        if isinstance(garment, dict) and "path" in garment and "score" in garment:
            logger.info(f"图像 {i+1}: 路径={garment['path']}, 评分={garment['score']}")
    
    # 测试完整的description_to_garment函数
    logger.info("测试完整的description_to_garment函数...")
    result = generator.description_to_garment(garment_dict)
    
    # 验证结果
    logger.info(f"最终结果: 类别={result.get('category')}, 提示词={result.get('prompt')}")
    logger.info(f"生成的服装图像数量: {len(result.get('garments', []))}")
    
    # 保存结果到文件以便查看
    result_file = os.path.join(test_output_dir, "test_result.json")
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    logger.info(f"结果已保存到: {result_file}")
    
    return result

def test_exported_function():
    """测试导出的description_to_garment函数"""
    logger.info("开始测试导出的description_to_garment函数...")
    
    # 定义测试服装描述
    test_garment_dict = {
        "category": "dresses",
        "prompt": "夏季碎花连衣裙，轻盈面料，高腰设计，A字裙摆，适合度假穿着"
    }
    
    # 调用导出的函数
    result = description_to_garment(test_garment_dict)
    
    # 验证结果
    logger.info(f"函数调用结果: 类别={result.get('category')}, 提示词={result.get('prompt')}")
    logger.info(f"生成的服装图像数量: {len(result.get('garments', []))}")
    
    return result

def main():
    """主测试函数"""
    logger.info("开始测试模型生成服装图像功能...")
    start_time = time.time()
    
    try:
        # 测试类方法
        test_result_class = test_text2garment_generator()
        
        # 测试导出的函数
        test_result_function = test_exported_function()
        
        # 检查结果是否有效
        class_test_success = len(test_result_class.get('garments', [])) > 0
        function_test_success = len(test_result_function.get('garments', [])) > 0
        
        # 总测试结果
        overall_success = class_test_success or function_test_success
        
        logger.info(f"类方法测试{'成功' if class_test_success else '失败'}")
        logger.info(f"导出函数测试{'成功' if function_test_success else '失败'}")
        logger.info(f"总测试结果: {'成功' if overall_success else '失败'}")
        
        # 如果模型未加载，提供提示
        if not class_test_success and not function_test_success:
            logger.warning("\n注意: 测试可能失败，原因可能是:")
            logger.warning("1. Flux模型未能成功加载")
            logger.warning("2. GPU内存不足或CUDA不可用")
            logger.warning("3. 环境依赖未正确安装")
            logger.warning("\n请检查系统配置并确保已安装所有必要的依赖项。")
            
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    end_time = time.time()
    logger.info(f"测试完成，总耗时: {end_time - start_time:.2f} 秒")

if __name__ == "__main__":
    main()