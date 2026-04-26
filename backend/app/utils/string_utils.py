#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字符串处理工具

提供字符串操作相关的通用功能
"""

import re
from typing import Optional, List


def ensure_utf8_string(value: any) -> str:
    """
    确保值是UTF-8编码的字符串

    Args:
        value: 任意类型的值

    Returns:
        UTF-8编码的字符串
    """
    if isinstance(value, str):
        return value
    elif isinstance(value, bytes):
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError:
            return value.decode("utf-8", errors="replace")
    else:
        return str(value)


def sanitize_string(value: str) -> str:
    """
    清理字符串，移除无效字符

    Args:
        value: 输入字符串

    Returns:
        清理后的字符串
    """
    # 移除控制字符，保留可打印字符
    return "".join(c for c in value if c.isprintable() or c in "\n\t\r")


def format_number(value: float, decimal_places: int = 2) -> str:
    """
    格式化数字

    Args:
        value: 数字值
        decimal_places: 小数位数

    Returns:
        格式化后的字符串
    """
    return f"{value:.{decimal_places}f}"


def truncate_string(value: str, max_length: int, suffix: str = "...") -> str:
    """
    截断字符串

    Args:
        value: 输入字符串
        max_length: 最大长度
        suffix: 截断后的后缀

    Returns:
        截断后的字符串
    """
    if len(value) <= max_length:
        return value
    return value[: max_length - len(suffix)] + suffix


def camel_case_to_snake_case(value: str) -> str:
    """
    将驼峰命名转换为蛇形命名

    Args:
        value: 驼峰命名的字符串

    Returns:
        蛇形命名的字符串
    """
    return re.sub(r"([a-z0-9]|(?=[A-Z]))([A-Z])", r"\1_\2", value).lower()


def snake_case_to_camel_case(value: str) -> str:
    """
    将蛇形命名转换为驼峰命名

    Args:
        value: 蛇形命名的字符串

    Returns:
        驼峰命名的字符串
    """
    parts = value.split("_")
    return parts[0] + "".join(part.title() for part in parts[1:])


def is_valid_email(email: str) -> bool:
    """
    验证邮箱格式

    Args:
        email: 邮箱地址

    Returns:
        是否是有效的邮箱格式
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def split_string(value: str, separator: str = ",") -> List[str]:
    """
    分割字符串

    Args:
        value: 输入字符串
        separator: 分隔符

    Returns:
        分割后的字符串列表
    """
    return [item.strip() for item in value.split(separator) if item.strip()]
