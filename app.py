import gradio as gr
from core import StateManager, FileHandler, StoryProcessor
from core.config import Config
from util import get_log_contents

# 创建Gradio界面
def create_interface():
    """创建Gradio界面"""
    state_manager = StateManager()
    file_handler = FileHandler()
    story_processor = StoryProcessor(state_manager, file_handler)
    
    with gr.Blocks(title="儿童故事生成器", theme=gr.themes.Soft()) as demo:
        # 创建界面组件
        with gr.Tabs():
            # 生成故事标签页
            with gr.TabItem("生成故事"):
                with gr.Row():
                    with gr.Column(scale=1):
                        pdf_input = gr.File(label="上传PDF文件", file_types=[".pdf"], type="filepath")
                        with gr.Row():
                            submit_btn = gr.Button("🔮 生成故事", variant="primary", size="lg")
                            stop_btn = gr.Button("⏹️ 停止生成", variant="stop", size="lg")
                            chinese_file_output = gr.File(label="中文故事文件", visible=True)
                            english_file_output = gr.File(label="英文故事文件", visible=True)
                        
                    with gr.Column(scale=2):
                        story_output = gr.Textbox(label="生成的故事", lines=20, interactive=True)
                        with gr.Row():
                            translate_btn = gr.Button("🔄 翻译为英文", variant="secondary")
                        story_output_english = gr.Textbox(label="生成的英文故事", lines=20, interactive=True)
                        stop_status = gr.Textbox(label="状态", visible=False)
                        request_id_output = gr.Textbox(label="请求ID", visible=False)
            
            # 高级设置标签页
            with gr.TabItem("高级设置"):
                with gr.Row():
                    with gr.Column(scale=1):
                        vl_system_prompt_input = gr.Textbox(
                            label="图片识别系统提示",
                            value=Config.DEFAULT_VL_SYSTEM_PROMPT,
                            lines=10,
                            placeholder="输入自定义图片识别系统提示，留空则使用默认提示"
                        )
                        gr.Markdown("""
                        ### 图片识别系统提示说明
                        
                        此提示用于指导AI模型如何分析PDF中的图片内容。您可以根据需要自定义提示，以获得不同风格或内容的图片描述。
                        
                        默认提示专为儿童故事设计，强调:
                        - 提取页面中的关键元素（人物、场景、事件等）
                        - 识别封面中的主题和人物
                        - 保存每张页面的信息
                        """)
                    
                    with gr.Column(scale=1):
                        story_system_prompt_input = gr.Textbox(
                            label="故事生成系统提示",
                            value=Config.DEFAULT_STORY_SYSTEM_PROMPT,
                            lines=10,
                            placeholder="输入自定义故事生成系统提示，留空则使用默认提示"
                        )
                        gr.Markdown("""
                        ### 故事生成系统提示说明
                        
                        此提示用于指导AI模型如何将图片描述转化为连贯的故事。您可以根据需要自定义提示，以获得不同风格或内容的故事。
                        
                        默认提示专为儿童故事设计，强调:
                        - 故事的连贯性和趣味性
                        - 适合2-8岁儿童的阅读水平
                        - 包含积极的价值观和教育意义
                        - 角色塑造和互动元素
                        """)
            
            # 系统日志标签页
            with gr.TabItem("系统日志"):
                refresh_log_btn = gr.Button("刷新日志")
                system_log_output = gr.Textbox(
                    label="系统日志",
                    lines=20,
                    value=get_log_contents(),
                    interactive=False
                )
        
        # 添加事件处理
        stop_btn.click(
            fn=state_manager.stop_generation,
            inputs=[request_id_output],
            outputs=[stop_status]
        )
        
        submit_btn.click(
            fn=state_manager.generate_request_id,
            inputs=[],
            outputs=[request_id_output],
        ).then(
            fn=story_processor.process_pdf,
            inputs=[pdf_input, request_id_output, vl_system_prompt_input, story_system_prompt_input],
            outputs=[story_output, chinese_file_output]
        )
        
        pdf_input.change(
            fn=lambda: ("", "", None, None),
            inputs=[],
            outputs=[story_output, request_id_output, chinese_file_output, english_file_output]
        )
        
        translate_btn.click(
            fn=story_processor.translate_to_english,
            inputs=[story_output],
            outputs=[story_output_english, english_file_output]
        )
        
        refresh_log_btn.click(
            fn=get_log_contents,
            inputs=[],
            outputs=[system_log_output]
        )
        
        # 添加使用说明
        with gr.Accordion("使用说明", open=False):
            gr.Markdown("""
            ### 使用步骤
            1. 点击"上传PDF文件"按钮选择一个包含儿童故事页面的PDF文件
            2. 可选：在"高级设置"标签页中自定义系统提示
            3. 点击"生成故事"按钮开始处理
            4. 系统将自动提取PDF中的页面，分析页面内容，并生成一个连贯的儿童故事
            5. 处理日志会显示处理过程中的详细信息
            6. 故事将实时生成并显示在界面上
            
            ### 注意事项
            - 处理时间取决于PDF的大小和页面数量
            - 请确保PDF文件包含清晰的页面
            - 生成的故事会根据页面内容自动创建，适合2-8岁儿童阅读
            - 自定义系统提示可以改变故事的风格和内容
            """)
        
        gr.Markdown("---")
        gr.Markdown("© 2024 儿童故事生成器 | 基于人工智能技术")
    
    return demo

