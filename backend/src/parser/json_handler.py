"""
JSON文件处理模块

提供JSON文件的读取和解析功能
"""

import json
from typing import Dict, Any, List, Optional
from gw2_log_score.core.logger import Logger

logger = Logger(__name__)


class JSONHandler:
    """
    JSON文件处理�?
    支持多种编码格式的JSON文件读取
    """

    DEFAULT_ENCODINGS: List[str] = ["utf-8", "gbk", "gb2312", "gb18030", "utf-16"]

    @classmethod
    def read(
        cls, file_path: str, encodings: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        读取JSON文件，自动尝试多种编码格�?
        Args:
            file_path: JSON文件路径
            encodings: 自定义编码列表，默认使用DEFAULT_ENCODINGS

        Returns:
            解析后的字典数据

        Raises:
            ValueError: 所有编码格式均失败时抛�?        """
        encodings = encodings or cls.DEFAULT_ENCODINGS
        last_error: Optional[Exception] = None

        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    data = json.load(f)
                    logger.debug(
                        f"Successfully read JSON file with encoding: {encoding}"
                    )
                    return data
            except UnicodeDecodeError as e:
                last_error = e
                logger.debug(f"Failed to decode with {encoding}: {e}")
                continue
            except json.JSONDecodeError as e:
                last_error = e
                logger.error(f"JSON decode error with {encoding}: {e}")
                continue

        raise ValueError(
            f"Failed to parse JSON file {file_path}. "
            f"All attempted encodings failed. Last error: {last_error}"
        )

    @classmethod
    def write(
        cls, file_path: str, data: Dict[str, Any], encoding: str = "utf-8"
    ) -> None:
        """
        写入JSON文件

        Args:
            file_path: 目标文件路径
            data: 要写入的数据
            encoding: 编码格式，默认utf-8
        """
        with open(file_path, "w", encoding=encoding) as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.debug(f"Successfully wrote JSON file: {file_path}")

    @classmethod
    def validate_structure(cls, data: Dict[str, Any], required_keys: List[str]) -> bool:
        """
        验证JSON数据结构

        Args:
            data: 待验证的数据
            required_keys: 必需的键列表

        Returns:
            数据结构是否有效
        """
        for key in required_keys:
            if key not in data:
                logger.warning(f"Missing required key in JSON data: {key}")
                return False
        return True

