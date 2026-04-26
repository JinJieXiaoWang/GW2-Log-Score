#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
职业服务

封装职业相关的核心业务逻辑
"""

from typing import Dict, Any, List
from app.config.config_loader import ConfigLoader
from app.core.logger import Logger


class ProfessionService:
    """职业服务类"""

    def __init__(self):
        """
        初始化职业服务
        """
        self.logger = Logger(__name__)
        self.config_loader = ConfigLoader()

    def get_professions(self) -> Dict[str, str]:
        """
        获取职业翻译映射

        Returns:
            职业翻译字典
        """
        return self.config_loader.get_professions()

    def get_profession_colors(self) -> Dict[str, Dict[str, str]]:
        """
        获取职业颜色配置

        Returns:
            职业颜色字典
        """
        return self.config_loader.get_profession_colors()

    def get_role_types(self) -> Dict[str, str]:
        """
        获取角色类型翻译

        Returns:
            角色类型翻译字典
        """
        return self.config_loader.get_role_types()

    def get_role_config(self) -> Dict[str, Any]:
        """
        获取角色配置

        Returns:
            角色配置字典
        """
        return self.config_loader.get_role_config()

    def get_profession_default_roles(self) -> Dict[str, str]:
        """
        获取职业默认角色

        Returns:
            职业默认角色字典
        """
        return self.config_loader.get_profession_default_roles()

    def get_professions_full_data(self) -> List[Dict[str, Any]]:
        """
        获取完整的职业数据

        Returns:
            完整的职业数据列表
        """
        return self.config_loader.get_professions_full_data()
