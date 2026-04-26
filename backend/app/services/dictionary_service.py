#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字典服务

封装字典相关的核心业务逻辑
"""

from typing import Dict, Any, List, Optional
from app.database.db_manager import DBManager
from app.utils.dict_utils import (
    get_dict_label,
    get_dict_value,
    get_dict_datas,
    get_dict_options,
    get_dict_values,
    get_dict_labels,
    clear_dict_cache,
    remove_dict_cache,
)
from app.core.logger import Logger


class DictionaryService:
    """字典服务类"""

    def __init__(self, db_path: str):
        """
        初始化字典服务
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.logger = Logger(__name__)

    def get_dict_label(self, dict_type: str, dict_value: str) -> str:
        """
        通过值获取字典标签
        Args:
            dict_type: 字典类型
            dict_value: 字典值
        Returns:
            字典标签
        """
        return get_dict_label(dict_type, dict_value, self.db_path)

    def get_dict_value(self, dict_type: str, dict_label: str) -> str:
        """
        通过标签获取字典值
        Args:
            dict_type: 字典类型
            dict_label: 字典标签

        Returns:
            字典值
        """
        return get_dict_value(dict_type, dict_label, self.db_path)

    def get_dict_datas(self, dict_type: str) -> List[Dict[str, Any]]:
        """
        获取指定类型的字典数据
        Args:
            dict_type: 字典类型

        Returns:
            字典数据列表
        """
        return get_dict_datas(dict_type, self.db_path)

    def get_dict_options(self, dict_type: str) -> List[Dict[str, str]]:
        """
        获取指定类型的字典选项（用于下拉选择）
        Args:
            dict_type: 字典类型

        Returns:
            字典选项列表
        """
        return get_dict_options(dict_type, self.db_path)

    def get_dict_values(self, dict_type: str) -> List[str]:
        """
        获取指定类型的所有字典值
        Args:
            dict_type: 字典类型

        Returns:
            字典值列表
        """
        return get_dict_values(dict_type, self.db_path)

    def get_dict_labels(self, dict_type: str) -> List[str]:
        """
        获取指定类型的所有字典标签
        Args:
            dict_type: 字典类型

        Returns:
            字典标签列表
        """
        return get_dict_labels(dict_type, self.db_path)

    def clear_dict_cache(self) -> None:
        """
        清除字典缓存
        """
        clear_dict_cache()

    def remove_dict_cache(self, dict_type: str) -> None:
        """
        移除指定类型的字典缓存
        Args:
            dict_type: 字典类型
        """
        remove_dict_cache(dict_type)

    def get_dict_categories(self) -> List[Dict[str, Any]]:
        """
        获取所有字典分类
        Returns:
            字典分类列表
        """
        db = DBManager(self.db_path)
        return db.get_dict_categories()

    def get_dict_by_category(self, category_code: str) -> List[Dict[str, Any]]:
        """
        获取分组下的字典

        Args:
            category_code: 分类编码

        Returns:
            字典列表
        """
        db = DBManager(self.db_path)
        return db.get_dict_by_category(category_code)

    def get_dict_detail(self, dict_id: int) -> Dict[str, Any]:
        """
        获取字典项详情
        Args:
            dict_id: 字典ID

        Returns:
            字典项详情
        """
        db = DBManager(self.db_path)
        return db.get_dict_by_id(dict_id)

    def get_dict_by_code(self, category_code: str, dict_value: str) -> Dict[str, Any]:
        """
        通过分组编码和字典值获取字典
        Args:
            category_code: 分类编码
            dict_value: 字典值
        Returns:
            字典详情
        """
        db = DBManager(self.db_path)
        return db.get_dict_by_code(category_code, dict_value)

    def create_dict_group(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建字典分组
        Args:
            data: 分组数据
        Returns:
            创建的分组信息
        """
        db = DBManager(self.db_path)
        return db.create_dict_group(data)

    def update_dict_group(self, dict_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新字典分组
        Args:
            dict_id: 分组ID
            data: 分组数据
        Returns:
            更新后的分组信息
        """
        db = DBManager(self.db_path)
        return db.update_dict_group(dict_id, data)

    def delete_dict_group(self, dict_id: int) -> bool:
        """
        删除字典分组
        Args:
            dict_id: 分组ID
        Returns:
            是否删除成功
        """
        db = DBManager(self.db_path)
        return db.delete_dict_group(dict_id)

    def get_dict_items_by_group(self, dict_type: str, include_disabled: bool = False) -> List[Dict[str, Any]]:
        """
        获取分组下的字典项
        Args:
            dict_type: 分组类型
            include_disabled: 是否包含禁用项
        Returns:
            字典项列表
        """
        db = DBManager(self.db_path)
        return db.get_dict_items_by_group(dict_type, include_disabled)

    def create_dict_item(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建字典项
        Args:
            data: 字典项数据
        Returns:
            创建的字典项信息
        """
        db = DBManager(self.db_path)
        return db.create_dict_item(data)

    def update_dict_item(self, dict_code: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新字典项
        Args:
            dict_code: 字典项ID
            data: 字典项数据
        Returns:
            更新后的字典项信息
        """
        db = DBManager(self.db_path)
        return db.update_dict_item(dict_code, data)

    def delete_dict_item(self, dict_code: int) -> bool:
        """
        删除字典项
        Args:
            dict_code: 字典项ID
        Returns:
            是否删除成功
        """
        db = DBManager(self.db_path)
        return db.delete_dict_item(dict_code)
