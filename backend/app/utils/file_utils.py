#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件处理工具

提供文件操作相关的通用功能
"""

import os
import hashlib
import tempfile
import shutil


def compute_file_hash(file_path: str) -> str:
    """
    计算文件的MD5哈希值

    Args:
        file_path: 文件路径

    Returns:
        MD5哈希字符串
    """
    hash_obj = hashlib.md5()
    with open(file_path, "rb") as f:
        hash_obj.update(f.read())
    return hash_obj.hexdigest()


def create_temp_directory() -> str:
    """
    创建临时目录

    Returns:
        临时目录路径
    """
    return tempfile.mkdtemp()


def cleanup_temp_directory(directory: str) -> None:
    """
    清理临时目录

    Args:
        directory: 临时目录路径
    """
    if os.path.exists(directory):
        shutil.rmtree(directory)


def get_file_extension(filename: str) -> str:
    """
    获取文件扩展名

    Args:
        filename: 文件名

    Returns:
        文件扩展名（小写）
    """
    return os.path.splitext(filename)[1].lower()


def ensure_directory_exists(directory: str) -> None:
    """
    确保目录存在，如果不存在则创建

    Args:
        directory: 目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_file_size(file_path: str) -> int:
    """
    获取文件大小（字节）

    Args:
        file_path: 文件路径

    Returns:
        文件大小（字节）
    """
    return os.path.getsize(file_path)


def is_valid_file(file_path: str) -> bool:
    """
    检查文件是否存在且是一个普通文件

    Args:
        file_path: 文件路径

    Returns:
        是否是有效文件
    """
    return os.path.exists(file_path) and os.path.isfile(file_path)


def copy_file(source: str, destination: str) -> None:
    """
    复制文件

    Args:
        source: 源文件路径
        destination: 目标文件路径
    """
    shutil.copy2(source, destination)


def move_file(source: str, destination: str) -> None:
    """
    移动文件

    Args:
        source: 源文件路径
        destination: 目标文件路径
    """
    shutil.move(source, destination)


def delete_file(file_path: str) -> None:
    """
    删除文件

    Args:
        file_path: 文件路径
    """
    if os.path.exists(file_path):
        os.remove(file_path)
