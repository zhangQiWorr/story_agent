import os
import traceback

from core.config import Config
from util import logger
from app import create_interface


def user_login(username, password):
    if username == "admin" and password == "admin":
        return True
    else:
        return False

def main():
    """主函数"""
    try:
        # 设置API密钥
        os.environ["DASHSCOPE_API_KEY"] = Config.API_KEY
        logger.info("Using DASHSCOPE_API_KEY from environment variables")

        # 检查python命令
        python_cmd = "python3" if os.system("python3 --version > /dev/null 2>&1") == 0 else "python"
        logger.info(f"Using Python command: {python_cmd}")

        # 创建并启动Gradio界面
        demo = create_interface()
        logger.info("Starting Gradio interface...")
        demo.launch(share=True, server_name="0.0.0.0", server_port=8000, auth=user_login)

    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Application startup error: {error_trace}")

        # 检查常见问题
        if "ModuleNotFoundError" in str(e):
            logger.error("Missing dependencies. Try running: pip install -r requirements.txt")
        elif "PermissionError" in str(e):
            logger.error("Permission error. Check file and directory permissions")
        elif "Address already in use" in str(e):
            logger.error("Port is already in use. Try closing other applications or specify a different port")


if __name__ == "__main__":
    main()