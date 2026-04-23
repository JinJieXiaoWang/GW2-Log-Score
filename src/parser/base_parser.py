"""
GW2日志解析器基础模块

提供日志解析的通用工具和基类
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from src.core.logger import Logger

logger = Logger(__name__)


class BaseParser(ABC):
    """
    日志解析器基类

    所有日志解析器都应继承此类并实现parse方法
    """

    @abstractmethod
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        解析日志文件

        Args:
            file_path: 日志文件路径

        Returns:
            解析后的战斗数据字典
        """
        pass

    def validate_file(self, file_path: str) -> bool:
        """
        验证文件是否存在且可读

        Args:
            file_path: 文件路径

        Returns:
            文件是否有效

        Raises:
            FileNotFoundError: 文件不存在时抛出
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Log file not found: {file_path}")
        return True

    def get_file_extension(self, file_path: str) -> str:
        """
        获取文件扩展名(小写)

        Args:
            file_path: 文件路径

        Returns:
            文件扩展名(包含点号，如'.json')
        """
        return os.path.splitext(file_path)[1].lower()


class FileHandler:
    """
    文件处理工具类

    提供文件读取、解压等通用操作
    """

    SUPPORTED_EXTENSIONS = ['.json', '.zevtc', '.evtc', '.zetvc']

    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        """
        检查文件格式是否支持

        Args:
            file_path: 文件路径

        Returns:
            是否支持该文件格式
        """
        ext = os.path.splitext(file_path)[1].lower()
        return ext in cls.SUPPORTED_EXTENSIONS

    @classmethod
    def ensure_directory(cls, dir_path: str) -> None:
        """
        确保目录存在，不存在则创建

        Args:
            dir_path: 目录路径
        """
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
