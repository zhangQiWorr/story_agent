import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

# 创建日志目录
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 日志文件路径
LOG_FILE = os.path.join(LOG_DIR, 'story_generator.log')

# 创建logger实例
logger = logging.getLogger('StoryGenerator')
logger.setLevel(logging.DEBUG)

# 日志格式
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# 文件处理器（按大小轮转，最大10MB，保留5个备份）
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# 添加处理器到logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

def log_story_generation(pdf_file, story_length, generation_time):
    """记录故事生成信息"""
    logger.info(f"Story generated from PDF: {pdf_file}")
    logger.info(f"Story length: {story_length} characters")
    logger.info(f"Generation time: {generation_time}")

def log_error(error_type, error_message, additional_info=None):
    """记录错误信息"""
    logger.error(f"Error type: {error_type}")
    logger.error(f"Error message: {error_message}")
    if additional_info:
        logger.error(f"Additional info: {additional_info}")

def log_translation(source_length, target_length, translation_time):
    """记录翻译信息"""
    logger.info(f"Translation completed")
    logger.info(f"Source length: {source_length} characters")
    logger.info(f"Target length: {target_length} characters")
    logger.info(f"Translation time: {translation_time}")

def log_api_call(api_name, status, response_time):
    """记录API调用信息"""
    logger.debug(f"API call: {api_name}")
    logger.debug(f"Status: {status}")
    logger.debug(f"Response time: {response_time}ms")

def get_log_contents(num_lines=100):
    """获取最近的日志内容"""
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()[-num_lines:]
        return ''.join(lines)
    except Exception as e:
        logger.error(f"Error reading log file: {str(e)}")
        return "无法读取日志文件" 