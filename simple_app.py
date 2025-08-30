import gradio as gr
import os

# 确保输出目录存在
OUTPUT_FOLDER = "static/outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

class SimpleStyleAgent:
    def __init__(self):
        self.current_style_analysis = ""
        
    def analyze_style(self, user_input):
        """简单的风格分析方法"""
        try:
            # 简单的模拟分析结果
            analysis = f"用户需求: {user_input}\n\n风格分析:\n- 这是一个简单的风格分析示例\n- 我们正在解决Gradio客户端JSON schema类型错误问题\n- 当前时间: {time.strftime('%Y-%m-%d %H:%M:%S')}"
            self.current_style_analysis = analysis
            return analysis
        except Exception as e:
            return f"分析过程中出错: {str(e)}"
    
    def reset_session(self):
        """重置会话状态"""
        try:
            self.current_style_analysis = ""
            return "会话已重置", [], None, []
        except Exception as e:
            return f"重置会话时出错: {str(e)}", [], None, []

# 导入时间模块
import time

# 初始化应用实例
simple_app = SimpleStyleAgent()

# 创建Gradio界面
with gr.Blocks(title="Simple Style Agent") as demo:
    gr.Markdown("# Simple Style Agent - 简化版")
    gr.Markdown("这是一个简化版的应用，用于测试Gradio界面功能。")
    
    with gr.Row():
        with gr.Column(scale=1):
            # 风格输入区域
            style_input = gr.Textbox(label="请描述您的服装风格需求", placeholder="例如：我需要一件适合夏季的休闲连衣裙")
            analyze_btn = gr.Button("分析风格需求")
            
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
        fn=simple_app.analyze_style,
        inputs=[style_input],
        outputs=[style_analysis_output]
    )
    
    reset_btn.click(
        fn=simple_app.reset_session,
        inputs=[],
        outputs=[style_analysis_output, clothing_output, try_on_output, recommendations_output]
    )

def main():
    """应用程序主入口函数"""
    print("正在启动简化版StyleAgent应用...")
    print(f"输出文件目录: {OUTPUT_FOLDER}")
    
    # 启动Gradio应用
    demo.launch(
        share=False,  # 暂时设置为False，避免frpc相关错误
        debug=False,
        server_port=7862  # 使用不同的端口
    )

# 启动应用
if __name__ == "__main__":
    main()