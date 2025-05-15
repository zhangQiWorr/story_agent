import uuid
from typing import Tuple, Optional, Dict, List, Union

from util.logger import logger


# 全局状态管理
class StateManager:
    """状态管理类，处理请求状态和文件管理"""

    def __init__(self):
        self.request_states: Dict[str, Dict] = {}

    def generate_request_id(self) -> str:
        """生成新的请求ID并初始化状态"""
        request_id = str(uuid.uuid4())
        self.request_states[request_id] = {'stop': False}
        return request_id

    def stop_generation(self, request_id: str) -> str:
        """停止特定请求的故事生成过程"""
        if request_id in self.request_states:
            self.request_states[request_id]['stop'] = True
            logger.info(f"用户请求停止故事生成 (请求ID: {request_id})")
            return "正在停止生成过程..."
        return "未找到对应的生成任务"

    def cleanup_request(self, request_id: str) -> None:
        """清理请求状态"""
        if request_id in self.request_states:
            del self.request_states[request_id]