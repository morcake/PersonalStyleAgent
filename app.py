import os
import gradio as gr
import json
from typing import Dict, List, Optional, Union
from PIL import Image
import time

# 导入自定义模块
from agents.style_agent import StyleAgent
from agents.clothing_recommendation_agent import ClothingRecommendationAgent
from agents.virtual_try_on_agent import VirtualTryOnAgent
from utils.need2text import get_need2text, get_addition_need2text
from utils.text2garment import description_to_garment
from utils.flux_vton import run_vton
from utils.metrics import VQAScore, ClipScore
from utils.image_process import image_process
from utils.search import search_clothing_items
from config.config import STATIC_FOLDER, OUTPUT_FOLDER

# 初始化各个Agent
style_agent = StyleAgent()
clothing_recommendation_agent = ClothingRecommendationAgent()
virtual_try_on_agent = VirtualTryOnAgent()

# 确保输出目录存在
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

class PersonalStyleAgentApp:
    """PersonalStyleAgent应用程序类，负责管理整个应用的状态和流程"""
    def __init__(self):
        # 存储应用状态
        self.current_style_analysis = {}
        self.generated_clothing_images = []
        self.try_on_results = []
        self.recommendations = []
        self.selected_clothing = None
        self.current_step = "style_input"
        
        # 存储用户输入历史
        self.user_input_history = []

    def analyze_style(self, user_input: str) -> str:
        """分析用户风格需求"""
        try:
            # 保存用户输入
            self.user_input_history.append({
                "type": "style_input",
                "content": user_input,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })

            # 生成服装描述
            clothing_description = style_agent.generate_clothing_description(user_input)
            
            # 更新状态
            self.current_style_analysis = {
                "user_input": user_input,
                "clothing_description": clothing_description
            }
            
            # 保存到历史记录
            with open(os.path.join(OUTPUT_FOLDER, "style_analysis.json"), "w", encoding="utf-8") as f:
                json.dump(self.current_style_analysis, f, ensure_ascii=False, indent=2)
            
            # 返回格式化的字符串而不是字典
            return f"用户需求: {user_input}\n\n生成的服装描述:\n{clothing_description}"
        except Exception as e:
            print(f"分析风格需求时出错: {e}")
            return f"分析失败: {str(e)}"

    def generate_clothing(self, clothing_description: Union[str, Dict] = None, num_images: int = 3) -> List:
        """生成服装图像"""
        try:
            # 如果没有提供描述，使用当前分析结果
            if clothing_description is None and self.current_style_analysis:
                clothing_description = self.current_style_analysis.get("clothing_description", "")
                
            if not clothing_description:
                print("没有提供服装描述")
                return []  # 返回空列表而不是错误字典

            # 确保传递给generate_clothing_images的是字典类型
            if isinstance(clothing_description, str):
                # 如果是字符串，创建一个默认的字典结构
                garment_dict = {
                    "category": "upper_body",
                    "prompt": clothing_description
                }
                print(f"将字符串描述转换为字典: {garment_dict}")
            elif isinstance(clothing_description, dict):
                # 如果已经是字典，直接使用
                garment_dict = clothing_description
                print(f"使用已有的字典描述: {garment_dict}")
            else:
                print(f"无效的服装描述类型: {type(clothing_description)}")
                return []

            # 调用StyleAgent生成服装图像
            print("调用style_agent.generate_clothing_images...")
            results = style_agent.generate_clothing_images(garment_dict)
            
            # 检查results的类型
            if not isinstance(results, dict):
                print(f"generate_clothing_images返回了非字典类型: {type(results)}")
                # 创建一个默认的结果结构
                results = {
                    "category": garment_dict.get("category", "upper_body"),
                    "prompt": garment_dict.get("prompt", ""),
                    "garments": []
                }
            
            # 更新状态
            self.generated_clothing_images = results
            self.current_step = "clothing_selection"
            
            # 保存结果
            try:
                with open(os.path.join(OUTPUT_FOLDER, "generated_clothing.json"), "w", encoding="utf-8") as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
            except Exception as json_err:
                print(f"保存结果时出错: {json_err}")
            
            # 提取图像路径列表，转换为Gradio Gallery组件可以处理的格式
            garments = results.get("garments", [])
            
            # 检查garments是否为列表
            if not isinstance(garments, list):
                print(f"garments不是列表类型: {type(garments)}")
                garments = []
            
            # 安全地提取图像路径
            image_paths = []
            for garment in garments:
                if isinstance(garment, dict) and garment.get("path"):
                    image_paths.append(garment.get("path"))
                else:
                    print(f"跳过无效的服装项: {type(garment)}")
            
            print(f"提取了 {len(image_paths)} 个有效图像路径")
            return image_paths
        except Exception as e:
            print(f"生成服装图像时出错: {type(e).__name__}: {e}")
            # 打印错误堆栈，帮助调试
            import traceback
            traceback.print_exc()
            return []  # 返回空列表而不是错误字典

    def select_clothing(self, clothing_index: int) -> Dict:
        """选择生成的服装"""
        try:
            # 检查self.generated_clothing_images是否是字典并包含garments字段
            if isinstance(self.generated_clothing_images, dict) and "garments" in self.generated_clothing_images:
                garments = self.generated_clothing_images["garments"]
                if 0 <= clothing_index < len(garments):
                    self.selected_clothing = garments[clothing_index]
                    self.current_step = "try_on_preparation"
                    return self.selected_clothing
                else:
                    return {"error": "无效的服装索引"}
            else:
                return {"error": "没有可用的服装图像"}
        except Exception as e:
            print(f"选择服装时出错: {e}")
            return {"error": str(e)}

    def try_on_clothing(self, person_image_path: str) -> Dict:
        """执行虚拟试穿"""
        try:
            if not self.selected_clothing or not os.path.exists(person_image_path):
                return {"error": "请先选择服装并上传人物图像"}

            # 获取服装图像路径
            clothing_image_path = self.selected_clothing.get("image_path", "")
            
            if not clothing_image_path or not os.path.exists(clothing_image_path):
                return {"error": "找不到选定的服装图像"}

            # 调用VirtualTryOnAgent执行虚拟试穿
            result = virtual_try_on_agent.try_on_clothing(
                person_image_path=person_image_path,
                clothing_image_path=clothing_image_path,
                clothing_description=self.selected_clothing.get("description", "")
            )
            
            # 如果成功，添加到试穿结果列表
            if result.get("success", False):
                self.try_on_results.append(result)
                self.current_step = "try_on_evaluation"
                
                # 保存结果
                with open(os.path.join(OUTPUT_FOLDER, f"try_on_result_{len(self.try_on_results)}.json"), "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
            
            return result
        except Exception as e:
            print(f"执行虚拟试穿时出错: {e}")
            return {"error": str(e)}

    def get_recommendations(self, style: str = None, num_results: int = 10) -> List[Dict]:
        """获取服装推荐"""
        try:
            # 如果没有提供风格，使用当前分析结果
            if style is None and self.current_style_analysis:
                # 从描述中提取关键词作为风格
                clothing_description = self.current_style_analysis.get("clothing_description", "")
                style = clothing_description.split(",")[0] if clothing_description else "时尚"
                
            # 调用ClothingRecommendationAgent获取推荐
            self.recommendations = clothing_recommendation_agent.recommend_by_style(style, num_results)
            
            # 保存结果
            with open(os.path.join(OUTPUT_FOLDER, "recommendations.json"), "w", encoding="utf-8") as f:
                json.dump(self.recommendations, f, ensure_ascii=False, indent=2)
            
            return self.recommendations
        except Exception as e:
            print(f"获取服装推荐时出错: {e}")
            return [{"error": str(e)}]

    def refine_result(self, feedback: str) -> Dict:
        """根据反馈优化结果"""
        try:
            if not self.try_on_results or not feedback:
                return {"error": "请先完成虚拟试穿并提供反馈"}

            # 获取最新的试穿结果
            latest_try_on = self.try_on_results[-1]
            
            # 调用VirtualTryOnAgent进行优化
            refined_result = virtual_try_on_agent.refine_try_on_result(latest_try_on, feedback)
            
            # 如果成功，添加到试穿结果列表
            if refined_result.get("success", False):
                self.try_on_results.append(refined_result)
                
                # 保存结果
                with open(os.path.join(OUTPUT_FOLDER, f"refined_try_on_result_{len(self.try_on_results)}.json"), "w", encoding="utf-8") as f:
                    json.dump(refined_result, f, ensure_ascii=False, indent=2)
            
            return refined_result
        except Exception as e:
            print(f"优化试穿结果时出错: {e}")
            return {"error": str(e)}

    def reset_session(self) -> tuple:
        """重置会话状态"""
        try:
            # 保存当前会话历史
            session_history = {
                "user_input": self.user_input_history,
                "style_analysis": self.current_style_analysis,
                "generated_clothing": self.generated_clothing_images,
                "try_on_results": self.try_on_results,
                "recommendations": self.recommendations,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 保存到历史记录文件
            history_file = os.path.join(OUTPUT_FOLDER, f"session_history_{int(time.time())}.json")
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(session_history, f, ensure_ascii=False, indent=2)
            
            # 重置状态
            self.current_style_analysis = {}
            self.generated_clothing_images = []
            self.try_on_results = []
            self.recommendations = []
            self.selected_clothing = None
            self.current_step = "style_input"
            self.user_input_history = []
            
            # 返回四个值，分别对应四个输出组件
            return "", [], None, []
        except Exception as e:
            print(f"重置会话时出错: {e}")
            return f"重置失败: {str(e)}", [], None, []

# 初始化应用实例
app_instance = PersonalStyleAgentApp()

# 创建Gradio界面
with gr.Blocks(title="PersonalStyleAgent - 个人风格服装生成与虚拟试穿系统", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# PersonalStyleAgent - 个人风格服装生成与虚拟试穿系统")
    gr.Markdown("欢迎使用PersonalStyleAgent！请输入您的风格需求，我们将为您生成定制的服装图像并提供虚拟试穿体验。")
    
    with gr.Row():
        with gr.Column(scale=1):
            # 风格输入区域
            style_input = gr.Textbox(label="请描述您的服装风格需求", placeholder="例如：我需要一件适合夏季的休闲连衣裙，颜色鲜艳，有花卉图案")
            analyze_btn = gr.Button("分析风格需求")
            
            # 生成服装区域
            num_images = gr.Slider(minimum=1, maximum=10, value=3, step=1, label="生成服装数量")
            generate_btn = gr.Button("生成服装图像")
            
            # 人物图像上传区域
            person_image = gr.Image(type="filepath", label="上传您的照片（用于虚拟试穿）")
            try_on_btn = gr.Button("虚拟试穿")
            
            # 反馈优化区域
            feedback = gr.Textbox(label="试穿效果反馈", placeholder="例如：衣服颜色太暗，图案不够清晰")
            refine_btn = gr.Button("优化试穿结果")
            
            # 服装推荐区域
            recommendation_style = gr.Textbox(label="推荐风格", placeholder="例如：休闲、正式、运动")
            num_recommendations = gr.Slider(minimum=5, maximum=20, value=10, step=1, label="推荐数量")
            recommend_btn = gr.Button("获取服装推荐")
            
            # 系统操作按钮
            reset_btn = gr.Button("重置会话", variant="secondary")
        
        with gr.Column(scale=2):
            # 结果显示区域
            style_analysis_output = gr.Textbox(label="风格分析结果", lines=8, placeholder="风格分析结果将显示在这里...")
            clothing_output = gr.Gallery(label="生成的服装图像", columns=3, rows=2, object_fit="contain")
            try_on_output = gr.Image(label="虚拟试穿结果")
            recommendations_output = gr.Dataframe(label="服装推荐结果", headers=["标题", "价格", "链接"])
            
    # 设置事件处理函数
    analyze_btn.click(
        fn=app_instance.analyze_style,
        inputs=[style_input],
        outputs=[style_analysis_output]
    )
    
    # 修改生成服装的事件处理函数，使用正确的Gradio输入输出方式
    generate_btn.click(
        fn=app_instance.generate_clothing,
        inputs=[],  # 不传递额外参数，使用默认值
        outputs=[clothing_output]
    )
    
    clothing_output.select(
        fn=lambda evt: app_instance.select_clothing(evt.index),
        inputs=[],
        outputs=[]
    )
    
    # 修改虚拟试穿的事件处理函数
    try_on_btn.click(
        fn=lambda img: app_instance.try_on_clothing(img) if img else None,  # 不再返回错误字典
        inputs=[person_image],  # 将图像作为输入
        outputs=[try_on_output]
    )
    
    # 修改优化试穿的事件处理函数
    refine_btn.click(
        fn=lambda fb: app_instance.refine_result(fb) if fb else None,  # 不再返回错误字典
        inputs=[feedback],  # 将反馈作为输入
        outputs=[try_on_output]
    )
    
    # 修改获取推荐的事件处理函数
    recommend_btn.click(
        fn=lambda style, num: app_instance.get_recommendations(style, int(num)),
        inputs=[recommendation_style, num_recommendations],  # 将所有参数作为输入
        outputs=[recommendations_output]
    )
    
    reset_btn.click(
        fn=app_instance.reset_session,
        inputs=[],
        outputs=[style_analysis_output, clothing_output, try_on_output, recommendations_output]
    )

def main():
    """应用程序主入口函数"""
    print("正在启动PersonalStyleAgent应用...")
    print(f"静态文件目录: {STATIC_FOLDER}")
    print(f"输出文件目录: {OUTPUT_FOLDER}")
    
    # 启动Gradio应用
    demo.launch(
        share=True,  # 设置为True可以生成公开可访问的链接
        debug=False,  # 设置为True可以启用调试模式
        server_port=7860  # 默认端口
    )

# 启动应用
if __name__ == "__main__":
    main()