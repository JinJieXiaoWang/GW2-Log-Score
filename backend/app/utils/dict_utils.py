#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字典工具模块
借鉴RuoYi框架的DictUtils实现，为GW2 Log Score项目提供字典操作功能
"""

from typing import List, Dict, Optional

# 分隔符
SEPARATOR = ","

# 全局缓存 - 简单的内存缓存
_dict_cache: Dict[str, List[Dict]] = {}


def set_dict_cache(dict_type: str, dict_datas: List[Dict]) -> None:
    """
    设置字典缓存

    Args:
        dict_type: 字典类型
        dict_datas: 字典数据列表
    """
    _dict_cache[dict_type] = dict_datas


def get_dict_cache(dict_type: str) -> Optional[List[Dict]]:
    """
    获取字典缓存

    Args:
        dict_type: 字典类型

    Returns:
        字典数据列表
    """
    return _dict_cache.get(dict_type)


def clear_dict_cache() -> None:
    """
    清空所有字典缓存
    """
    _dict_cache.clear()


def remove_dict_cache(dict_type: str) -> None:
    """
    删除指定字典缓存

    Args:
        dict_type: 字典类型
    """
    if dict_type in _dict_cache:
        del _dict_cache[dict_type]


def load_dict_from_db(dict_type: str, db_path: str = None) -> List[Dict]:
    """
    从数据库加载字典数据

    Args:
        dict_type: 字典类型
        db_path: 数据库路径
    Returns:
        字典数据列表
    """
    # 暂时返回空列表，因为db_manager还没有实现get_dict_data_by_type方法
    datas = []
    if datas:
        set_dict_cache(dict_type, datas)
    return datas


def get_dict_datas(dict_type: str, db_path: str = None) -> List[Dict]:
    """
    获取指定字典类型的所有字典数据
    Args:
        dict_type: 字典类型
        db_path: 数据库路径
    Returns:
        字典数据列表
    """
    datas = get_dict_cache(dict_type)
    if datas is None:
        datas = load_dict_from_db(dict_type, db_path)
    return datas or []


def get_dict_label(dict_type: str, dict_value: str, db_path: str = None, separator: str = SEPARATOR) -> str:
    """
    根据字典类型和字典值获取字典标签
    Args:
        dict_type: 字典类型
        dict_value: 字典值
        db_path: 数据库路径
        separator: 分隔符
    Returns:
        字典标签
    """
    if not dict_value:
        return ""

    datas = get_dict_datas(dict_type, db_path)
    if not datas:
        return ""

    # 创建值到标签的映射
    dict_map = {data["dict_value"]: data["dict_label"] for data in datas}

    # 单个值的情况
    if separator not in dict_value:
        return dict_map.get(dict_value, "")

    # 多个值的情况
    label_builder = []
    for separated_value in dict_value.split(separator):
        if separated_value in dict_map:
            label_builder.append(dict_map[separated_value])

    return separator.join(label_builder)


def get_dict_value(dict_type: str, dict_label: str, db_path: str = None, separator: str = SEPARATOR) -> str:
    """
    根据字典类型和字典标签获取字典值
    Args:
        dict_type: 字典类型
        dict_label: 字典标签
        db_path: 数据库路径
        separator: 分隔符
    Returns:
        字典值
    """
    if not dict_label:
        return ""

    datas = get_dict_datas(dict_type, db_path)
    if not datas:
        return ""

    # 创建标签到值的映射
    dict_map = {data["dict_label"]: data["dict_value"] for data in datas}

    # 单个标签的情况
    if separator not in dict_label:
        return dict_map.get(dict_label, "")

    # 多个标签的情况
    value_builder = []
    for separated_label in dict_label.split(separator):
        if separated_label in dict_map:
            value_builder.append(dict_map[separated_label])

    return separator.join(value_builder)


def get_dict_values(dict_type: str, db_path: str = None) -> str:
    """
    根据字典类型获取字典所有值
    Args:
        dict_type: 字典类型
        db_path: 数据库路径
    Returns:
        字典值，多个值用分隔符连接
    """
    datas = get_dict_datas(dict_type, db_path)
    if not datas:
        return ""

    values = [data["dict_value"] for data in datas]
    return SEPARATOR.join(values)


def get_dict_labels(dict_type: str, db_path: str = None) -> str:
    """
    根据字典类型获取字典所有标签
    Args:
        dict_type: 字典类型
        db_path: 数据库路径
    Returns:
        字典标签，多个标签用分隔符连接
    """
    datas = get_dict_datas(dict_type, db_path)
    if not datas:
        return ""

    labels = [data["dict_label"] for data in datas]
    return SEPARATOR.join(labels)


def get_dict_options(dict_type: str, db_path: str = None) -> List[Dict[str, str]]:
    """
    获取字典选项列表，通常用于前端下拉选择

    Args:
        dict_type: 字典类型
        db_path: 数据库路径
    Returns:
        字典选项列表，每个选项包含label和value
    """
    datas = get_dict_datas(dict_type, db_path)
    return [
        {"label": data["dict_label"], "value": data["dict_value"]} for data in datas
    ]


def get_profession_chinese_name(english_name: str) -> str:
    """
    获取职业或精英特长的中文名称

    Args:
        english_name: 职业或精英特长的英文名称

    Returns:
        中文名称
    """
    # 暂时直接返回英文名称，因为字典功能还未实现
    return english_name


def get_specialization_chinese_name(english_name: str) -> str:
    """
    获取精英特长的中文名称
    Args:
        english_name: 精英特长英文名称

    Returns:
        精英特长中文名称
    """
    # 暂时直接返回英文名称，因为字典功能还未实现
    return english_name
