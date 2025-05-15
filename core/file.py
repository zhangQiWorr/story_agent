import datetime
import os
import shutil
from typing import Tuple, Optional, Dict, List, Union

from core.config import Config
from util.logger import logger


# 文件处理类
class FileHandler:
    """文件处理类，处理文件保存和读取"""

    @staticmethod
    def save_story(story_content: str, story_type: str, pdf_name: Optional[str] = None) -> Optional[str]:
        """
        保存故事到本地文件

        Args:
            story_content: 故事内容
            story_type: 故事类型 ('chinese' 或 'english')
            pdf_name: PDF文件名（可选）

        Returns:
            str: 故事文件路径
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            story_name = f"{os.path.splitext(os.path.basename(pdf_name))[0]}_" if pdf_name else ""
            filename = f"{story_name}{story_type}_{timestamp}.txt"
            story_path = Config.STORIES_DIR / filename

            with open(story_path, "w", encoding="utf-8") as f:
                f.write(story_content)

            logger.info(f"{story_type.capitalize()} story saved: {story_path}")
            return str(story_path)
        except Exception as e:
            logger.error(f"Error saving {story_type} story: {str(e)}")
            return None

    @staticmethod
    def save_pdf_to_temp(pdf_file: str, temp_dir: str) -> Tuple[bool, str, str]:
        """
        保存PDF文件到临时目录

        Args:
            pdf_file: PDF文件路径或对象
            temp_dir: 临时目录路径

        Returns:
            Tuple[bool, str, str]: (是否成功, 错误信息, 临时文件路径)
        """
        temp_pdf_path = os.path.join(temp_dir, "uploaded.pdf")

        try:
            if isinstance(pdf_file, str):
                if os.path.exists(pdf_file):
                    with open(pdf_file, "rb") as src_file:
                        with open(temp_pdf_path, "wb") as dest_file:
                            dest_file.write(src_file.read())
                    return True, "", temp_pdf_path
                return False, f"错误：找不到文件 {pdf_file}", ""
            else:
                if hasattr(pdf_file, 'name'):
                    shutil.copy(pdf_file.name, temp_pdf_path)
                    return True, "", temp_pdf_path
                else:
                    with open(temp_pdf_path, "wb") as f:
                        f.write(pdf_file)
                    return True, "", temp_pdf_path
        except Exception as e:
            return False, f"错误：保存上传文件时出错 - {str(e)}", ""