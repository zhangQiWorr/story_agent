# 故事处理类
import datetime
import tempfile
import time
import traceback
from typing import Tuple, Optional, List, Union
from core import FileHandler
from core import StateManager
import gradio as gr

from core.config import Config
from llm import generate_story, get_text_from_image
from util import log_error, log_translation, pdf_convert_page_to_image
from util.logger import logger, log_story_generation


class StoryProcessor:
    """故事处理类，处理故事生成和翻译"""

    def __init__(self, state_manager: StateManager, file_handler: FileHandler):
        self.state_manager = state_manager
        self.file_handler = file_handler

    def _update_progress(self, progress: gr.Progress, value: float, desc: str) -> None:
        """
        更新进度条

        Args:
            progress: Gradio进度条对象
            value: 进度值 (0-1)
            desc: 进度描述
        """

        print("zq:", progress)

        if isinstance(progress, gr.Progress):
            progress(value, desc=desc)

    def process_pdf(self, pdf_file: str, request_id: str,
                    vl_system_prompt: str = Config.DEFAULT_VL_SYSTEM_PROMPT,
                    story_system_prompt: str = Config.DEFAULT_STORY_SYSTEM_PROMPT,
                    progress=gr.Progress()):
        """
        处理PDF文件并生成故事

        Args:
            pdf_file: PDF文件路径
            request_id: 请求ID
            vl_system_prompt: 图片识别系统提示
            story_system_prompt: 故事生成系统提示
            progress: Gradio进度条对象

        Returns:
            Tuple[str, Optional[str], Optional[str]]: (故事内容, 中文文件路径)
        """
        start_time = time.time()

        try:
            # 初始化处理环境
            self._update_progress(progress, 0.05, "初始化处理环境...")

            # 检查文件
            if not self._check_pdf_file(pdf_file):
                return "错误：未上传PDF文件", None

            # 处理PDF文件
            with tempfile.TemporaryDirectory() as temp_dir:
                self._update_progress(progress, 0.1, "准备处理PDF文件...")
                success, error_msg, temp_pdf_path = FileHandler.save_pdf_to_temp(pdf_file, temp_dir)
                if not success:
                    return error_msg, None

                # 转换PDF为图片
                self._update_progress(progress, 0.15, "转换PDF为图片...")
                images_path = self._convert_pdf_to_images(temp_pdf_path)
                if not images_path:
                    return "无法从PDF提取页面，请确保PDF包含有效的页面内容", None

                # 处理图片并生成故事
                story = self._process_images_and_generate_story(
                    images_path, request_id, vl_system_prompt, story_system_prompt,
                    start_time, pdf_file, progress
                )

                if isinstance(story, tuple):  # 错误情况
                    return story

                # 保存中文故事
                self._update_progress(progress, 0.95, "保存生成的故事...")
                chinese_path = self.file_handler.save_story(
                    story, 'chinese',
                    pdf_file if isinstance(pdf_file, str) else pdf_file.name
                )

                self._update_progress(progress, 1.0, "处理完成!")
                return story, chinese_path

        except Exception as e:
            error_msg = f"处理过程中出错: {str(e)}"
            error_trace = traceback.format_exc()
            log_error("ProcessingError", error_trace)
            return error_msg, None
        finally:
            self.state_manager.cleanup_request(request_id)

    def translate_to_english(self, text: str) -> Tuple[str, Optional[str]]:
        """
        将中文故事翻译为英文

        Args:
            text: 中文故事内容

        Returns:
            Tuple[str, Optional[str], Optional[str]]: (英文故事, 中文文件路径, 英文文件路径)
        """
        if not text or text.strip() == "":
            logger.warning("Translation attempted with empty text")
            return "请先生成或输入故事内容", None

        try:
            # 构建翻译提示
            translation_prompt = f"""请将以下中文故事翻译成英文，保持故事的风格和内容不变，使其适合2-8岁的中国儿童阅读：
{text}
请直接输出翻译结果，不要添加任何解释或前言。"""

            # 翻译故事
            translated_text = generate_story(text, "", translation_prompt, stream=False)

            # 记录翻译信息
            log_translation(
                source_length=len(text),
                target_length=len(translated_text),
                translation_time=f"{time.time() - time.time():.2f}s"
            )

            # 保存英文故事
            english_path = self.file_handler.save_story(translated_text, 'english')
            if english_path:
                logger.info(f"English story saved after translation: {english_path}")

            return translated_text, english_path

        except Exception as e:
            error_msg = f"翻译时出错: {str(e)}"
            error_trace = traceback.format_exc()
            log_error("TranslationError", error_trace)
            return error_msg, None

    def _check_pdf_file(self, pdf_file: str) -> bool:
        """检查PDF文件"""
        if pdf_file is None:
            error_msg = "错误：未上传PDF文件"
            error_trace = traceback.format_exc()
            log_error("FileError", error_trace)
            return False
        return True

    def _convert_pdf_to_images(self, temp_pdf_path: str) -> Optional[List[str]]:
        """转换PDF为图片"""
        try:
            images_path = pdf_convert_page_to_image(temp_pdf_path)
            if not images_path or len(images_path) == 0:
                logger.error("无法从PDF提取页面")
                return None
            logger.info(f"PDF已转换为 {len(images_path)} 张页面")
            return images_path
        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(f"转换PDF为页面时出错: {error_trace}")
            return None

    def _process_images_and_generate_story(self, images_path: List[str], request_id: str,
                                           vl_prompt: str, story_prompt: str,
                                           start_time: float, pdf_file: str, progress
                                           ) -> Union[str, Tuple[str, Optional[str], Optional[str]]]:
        """处理图片并生成故事"""
        conversation_history = [{"role": "system", "content": [{"type": "text", "text": vl_prompt}]}]
        images_text = []
        total_pages = len(images_path)

        self._update_progress(progress, 0.2, f"开始处理 {total_pages} 张页面...")

        for index, image_path in enumerate(images_path):
            if self.state_manager.request_states[request_id]['stop']:
                return "处理已停止", None, None

            current_page = index + 1

            # 计算进度百分比 (20% - 70%)
            progress_value = 0.2 + (0.5 * (index / total_pages))
            self._update_progress(progress, progress_value,
                                  f"处理页面 {current_page}/{total_pages} ({int(progress_value * 100)}%)")

            try:
                output, conversation_history = get_text_from_image(image_path, index, conversation_history)
                images_text.append(output)
                logger.info(f"页面 {current_page} 处理完成: {output}")
            except Exception as e:
                error_trace = traceback.format_exc()
                logger.error(f"处理页面 {current_page} 时出错: {error_trace}")
                continue

        if not images_text:
            return "无法处理PDF中的页面，请尝试使用其他PDF文件", None, None

        combined_text = "\n".join(images_text)
        logger.info(f"所有页面处理完成，开始生成故事...")

        self._update_progress(progress, 0.7, "开始生成完整故事...")

        try:
            story = generate_story(combined_text, story_prompt, stream=False)

            # 记录故事生成信息
            generation_time = time.time() - start_time
            log_story_generation(
                pdf_file=pdf_file if isinstance(pdf_file, str) else pdf_file.name,
                story_length=len(story),
                generation_time=f"{generation_time:.2f}s"
            )

            self._update_progress(progress, 0.9, "故事生成完成，准备保存...")

            total_time = datetime.datetime.now() - datetime.datetime.fromtimestamp(start_time)
            logger.info(f"总用时: {total_time}")

            return story

        except Exception as e:
            error_msg = f"生成故事时出错: {str(e)}"
            error_trace = traceback.format_exc()
            log_error("StoryGenerationError", error_trace)
            return error_msg, None, None