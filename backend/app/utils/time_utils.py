#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时间处理工具

提供日期和时间操作相关的通用功能
"""

from datetime import datetime, timedelta
from typing import Optional


def get_current_datetime() -> datetime:
    """
    获取当前日期时间

    Returns:
        当前日期时间对象
    """
    return datetime.now()


def get_current_date() -> str:
    """
    获取当前日期（YYYY-MM-DD格式）

    Returns:
        当前日期字符串
    """
    return datetime.now().strftime("%Y-%m-%d")


def get_current_time() -> str:
    """
    获取当前时间（HH:MM:SS格式）

    Returns:
        当前时间字符串
    """
    return datetime.now().strftime("%H:%M:%S")


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化日期时间

    Args:
        dt: 日期时间对象
        format_str: 格式字符串

    Returns:
        格式化后的日期时间字符串
    """
    return dt.strftime(format_str)


def parse_datetime(
    date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S"
) -> Optional[datetime]:
    """
    解析日期时间字符串

    Args:
        date_str: 日期时间字符串
        format_str: 格式字符串

    Returns:
        日期时间对象，如果解析失败则返回None
    """
    try:
        return datetime.strptime(date_str, format_str)
    except ValueError:
        return None


def get_today_start() -> datetime:
    """
    获取今天开始时间（00:00:00）

    Returns:
        今天开始时间对象
    """
    now = datetime.now()
    return datetime(now.year, now.month, now.day, 0, 0, 0)


def get_today_end() -> datetime:
    """
    获取今天结束时间（23:59:59）

    Returns:
        今天结束时间对象
    """
    now = datetime.now()
    return datetime(now.year, now.month, now.day, 23, 59, 59)


def get_days_ago(days: int) -> datetime:
    """
    获取几天前的日期时间

    Args:
        days: 天数

    Returns:
        几天前的日期时间对象
    """
    return datetime.now() - timedelta(days=days)


def get_days_later(days: int) -> datetime:
    """
    获取几天后的日期时间

    Args:
        days: 天数

    Returns:
        几天后的日期时间对象
    """
    return datetime.now() + timedelta(days=days)


def calculate_time_difference(start_time: datetime, end_time: datetime) -> timedelta:
    """
    计算时间差

    Args:
        start_time: 开始时间
        end_time: 结束时间

    Returns:
        时间差对象
    """
    return end_time - start_time


def format_duration(seconds: float) -> str:
    """
    格式化持续时间

    Args:
        seconds: 秒数

    Returns:
        格式化后的持续时间字符串
    """
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif minutes > 0:
        return f"{int(minutes)}m {int(seconds)}s"
    else:
        return f"{int(seconds)}s"
