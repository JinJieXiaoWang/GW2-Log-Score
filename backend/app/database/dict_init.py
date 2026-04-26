#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字典数据初始化模块

负责初始化游戏相关的字典数据，如职业、精英特长、角色定位等
"""

import json
import os
from typing import Dict, List, Any

# Tailwind类到十六进制颜色的映射
COLOR_MAP = {
    "text-yellow-800": "#854d0e",
    "text-red-800": "#991b1b",
    "text-orange-800": "#9a3412",
    "text-green-800": "#166534",
    "text-gray-800": "#1f2937",
    "text-cyan-800": "#155e75",
    "text-purple-800": "#6b21a8",
    "text-gray-900": "#111827",
    "text-indigo-800": "#3730a3",
}


class DictionaryDataInitializer:
    """
    字典数据初始化器
    """

    def __init__(self, db_manager):
        """
        初始化字典数据初始化器

        Args:
            db_manager: 数据库管理器实例
        """
        self.db = db_manager
        self.config_dir = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ),
            "config",
        )
        self.resource_dir = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ),
            "resources",
            "i18n",
        )
        self.professions_path = os.path.join(self.config_dir, "professions.json")
        self.scoring_rules_path = os.path.join(self.config_dir, "scoring_rules.json")
        self.default_config_path = os.path.join(self.config_dir, "default.json")
        self.translations = self._load_translations()

    def _load_translations(self):
        """
        加载翻译文件

        Returns:
            翻译字典
        """
        translations = {}
        if os.path.exists(self.resource_dir):
            for filename in os.listdir(self.resource_dir):
                if filename.endswith(".json"):
                    filepath = os.path.join(self.resource_dir, filename)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if "professions" in data:
                                translations = data["professions"]
                                break
                    except Exception as e:
                        print(f"Error loading translation file {filename}: {e}")
        return translations

    def _get_translation(self, key):
        """
        获取翻译值

        Args:
            key: 翻译键

        Returns:
            翻译后的值
        """
        return self.translations.get(key, key)

    def load_json_file(self, file_path: str) -> Dict[str, Any]:
        """
        加载JSON文件

        Args:
            file_path: 文件路径

        Returns:
            JSON数据字典
        """
        if not os.path.exists(file_path):
            print(f"配置文件不存在 {file_path}")
            return {}
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def initialize_all(self) -> Dict[str, Any]:
        """
        初始化所有字典数据

        Returns:
            初始化结果
        """
        results = {
            "professions": {"created": 0, "skipped": 0},
            "specializations": {"created": 0, "skipped": 0},
            "roles": {"created": 0, "skipped": 0},
            "scoring_dimensions": {"created": 0, "skipped": 0},
            "game_modes": {"created": 0, "skipped": 0},
            "buff_ids": {"created": 0, "skipped": 0},
        }

        # 初始化字典类型
        self._init_dict_types()
        
        # 初始化具体数据
        self._init_professions(results["professions"])
        self._init_specializations(results["specializations"])
        self._init_roles(results["roles"])
        self._init_scoring_dimensions(results["scoring_dimensions"])
        self._init_game_modes(results["game_modes"])
        self._init_buff_ids(results["buff_ids"])

        return results

    def check_dict_data_exists(self) -> bool:
        """
        检查字典表是否存在数据

        Returns:
            bool: 是否存在数据
        """
        try:
            import sqlite3
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # 检查字典类型表
                cursor.execute("SELECT COUNT(*) FROM sys_dict_type")
                type_count = cursor.fetchone()[0]
                
                # 检查字典数据表
                cursor.execute("SELECT COUNT(*) FROM sys_dict_data")
                data_count = cursor.fetchone()[0]
                
                return type_count > 0 or data_count > 0
        except Exception as e:
            print(f"检查字典数据失败: {e}")
            return False

    def reinitialize_all(self, force: bool = False) -> Dict[str, Any]:
        """
        重新初始化所有字典数据（先清空再初始化）

        Args:
            force: 是否强制初始化，跳过确认

        Returns:
            初始化结果
        """
        try:
            import sqlite3
            
            # 检查是否需要确认
            data_exists = self.check_dict_data_exists()
            
            # 如果需要确认但没有强制，返回需要确认的信息
            if data_exists and not force:
                return {
                    "status": "confirm_required",
                    "message": "字典表中已存在数据，初始化将清空所有数据并重新插入",
                    "data_exists": True
                }
            
            # 开始事务
            with sqlite3.connect(self.db.db_path) as conn:
                try:
                    # 开始事务
                    conn.execute("BEGIN TRANSACTION")
                    
                    # 清空字典数据表
                    conn.execute("DELETE FROM sys_dict_data")
                    # 清空字典类型表
                    conn.execute("DELETE FROM sys_dict_type")
                    
                    # 提交清空操作
                    conn.commit()
                    
                    # 重新初始化
                    results = self.initialize_all()
                    
                    # 添加状态信息
                    results["status"] = "success"
                    results["message"] = "字典数据重新初始化成功"
                    
                    return results
                    
                except Exception as e:
                    # 回滚事务
                    conn.rollback()
                    print(f"重新初始化失败: {e}")
                    return {
                        "status": "error",
                        "message": f"重新初始化失败: {str(e)}",
                        "error": str(e)
                    }
        except Exception as e:
            print(f"重新初始化失败: {e}")
            return {
                "status": "error",
                "message": f"重新初始化失败: {str(e)}",
                "error": str(e)
            }

    def _init_dict_types(self):
        """
        初始化字典类型
        """
        dict_types = [
            {"dict_type": "gw2_professions", "dict_name": "职业", "sort_order": 1},
            {"dict_type": "gw2_specializations", "dict_name": "精英特长", "sort_order": 2},
            {"dict_type": "gw2_roles", "dict_name": "角色定位", "sort_order": 3},
            {"dict_type": "gw2_scoring_dimensions", "dict_name": "评分维度", "sort_order": 4},
            {"dict_type": "gw2_game_modes", "dict_name": "游戏模式", "sort_order": 5},
            {"dict_type": "gw2_buff_ids", "dict_name": "增益ID", "sort_order": 6},
        ]

        for dt in dict_types:
            self._init_dict_type(dt["dict_type"], dt["dict_name"], sort_order=dt["sort_order"])

    def _init_dict_type(
        self, dict_type: str, dict_name: str, remark: str = None, sort_order: int = 0
    ):
        """
        初始化字典类型

        Args:
            dict_type: 字典类型
            dict_name: 字典名称
            remark: 备注
            sort_order: 排序顺序

        Returns:
            字典类型ID
        """
        try:
            import sqlite3
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO sys_dict_type 
                    (dict_type, dict_name, status, sort_order, remark)
                    VALUES (?, ?, 0, ?, ?)
                    """,
                    (dict_type, dict_name, sort_order, remark or "")
                )
                conn.commit()
                # 获取插入的ID
                cursor.execute("SELECT dict_id FROM sys_dict_type WHERE dict_type = ?", (dict_type,))
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            print(f"初始化字典类型失败 {dict_type}: {e}")
            return 0

    def _add_dict_data_safe(
        self,
        dict_type: str,
        dict_label: str,
        dict_value: str,
        dict_sort: int = 0,
        data_type: str = "",
        css_class: str = None,
        list_class: str = None,
        is_default: int = 0,
        remark: str = None,
        color: str = None,
    ) -> bool:
        """
        安全添加字典数据

        Args:
            dict_type: 字典类型
            dict_label: 字典标签
            dict_value: 字典值
            dict_sort: 排序顺序
            data_type: 数据类型
            css_class: CSS类
            list_class: 列表类
            is_default: 是否默认
            remark: 备注
            color: 颜色

        Returns:
            是否添加成功
        """
        try:
            import sqlite3
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                # 检查是否已存在
                cursor.execute(
                    "SELECT dict_code FROM sys_dict_data WHERE dict_type = ? AND dict_value = ?",
                    (dict_type, dict_value)
                )
                if cursor.fetchone():
                    return False  # 已存在，跳过
                
                # 如果color不为None，使用color作为css_class
                if color is not None:
                    css_class = color
                
                # 插入新数据
                cursor.execute(
                    """
                    INSERT INTO sys_dict_data 
                    (dict_sort, dict_label, dict_value, dict_type, data_type, css_class, list_class, is_default, status, remark)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
                    """,
                    (dict_sort, dict_label, dict_value, dict_type, data_type, css_class or "", list_class or "", is_default, remark or "")
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"添加字典数据失败 {dict_type}:{dict_value}: {e}")
            return False

    def _init_professions(self, result: Dict[str, int]):
        """
        初始化职业数据

        Args:
            result: 结果字典
        """
        professions_data = self.load_json_file(self.professions_path)
        professions = professions_data.get("professions", [])
        
        # 为每个职业分配一个颜色
        colors = list(COLOR_MAP.values())
        for i, profession in enumerate(professions):
            name = profession.get("name")
            if not name:
                continue
            
            label = self._get_translation(name)
            # 循环使用颜色列表
            color = colors[i % len(colors)]
            if self._add_dict_data_safe(
                "gw2_professions",
                label,
                name,
                dict_sort=i,
                color=color
            ):
                result["created"] += 1
            else:
                result["skipped"] += 1

    def _init_specializations(self, result: Dict[str, int]):
        """
        初始化精英特长数据

        Args:
            result: 结果字典
        """
        professions_data = self.load_json_file(self.professions_path)
        professions = professions_data.get("professions", [])
        
        # 为每个精英特长分配一个颜色
        colors = list(COLOR_MAP.values())
        sort_order = 0
        for profession in professions:
            specializations = profession.get("specializations", {})
            for spec_name in specializations:
                label = self._get_translation(spec_name)
                # 循环使用颜色列表
                color = colors[sort_order % len(colors)]
                if self._add_dict_data_safe(
                    "gw2_specializations",
                    label,
                    spec_name,
                    dict_sort=sort_order,
                    color=color
                ):
                    result["created"] += 1
                else:
                    result["skipped"] += 1
                sort_order += 1

    def _init_roles(self, result: Dict[str, int]):
        """
        初始化角色定位数据

        Args:
            result: 结果字典
        """
        roles = [
            {"value": "DPS", "label": "输出"},
            {"value": "SUPPORT", "label": "辅助"},
            {"value": "CONDITION", "label": "症状"},
            {"value": "HEALING", "label": "治疗"},
            {"value": "CONTROL", "label": "控制"},
            {"value": "UTILITY", "label": "功能"},
        ]
        
        # 为每个角色定位分配一个颜色
        colors = list(COLOR_MAP.values())
        for i, role in enumerate(roles):
            # 循环使用颜色列表
            color = colors[i % len(colors)]
            if self._add_dict_data_safe(
                "gw2_roles",
                role["label"],
                role["value"],
                dict_sort=i,
                color=color
            ):
                result["created"] += 1
            else:
                result["skipped"] += 1

    def _init_scoring_dimensions(self, result: Dict[str, int]):
        """
        初始化评分维度数据

        Args:
            result: 结果字典
        """
        scoring_rules = self.load_json_file(self.scoring_rules_path)
        dimensions = scoring_rules.get("dimension_definitions", {})
        
        # 为每个评分维度分配一个颜色
        colors = list(COLOR_MAP.values())
        sort_order = 0
        for dim_key, dim_data in dimensions.items():
            label = dim_data.get("name", dim_key)
            # 循环使用颜色列表
            color = colors[sort_order % len(colors)]
            if self._add_dict_data_safe(
                "gw2_scoring_dimensions",
                label,
                dim_key,
                dict_sort=sort_order,
                color=color
            ):
                result["created"] += 1
            else:
                result["skipped"] += 1
            sort_order += 1

    def _init_game_modes(self, result: Dict[str, int]):
        """
        初始化游戏模式数据

        Args:
            result: 结果字典
        """
        game_modes = [
            {"value": "WvW", "label": "世界之战"},
            {"value": "PVE", "label": "玩家对战环境"},
            {"value": "PvP", "label": "玩家对战玩家"},
            {"value": "Fractals", "label": "碎层"},
            {"value": "Raids", "label": "团队副本"},
        ]
        
        # 为每个游戏模式分配一个颜色
        colors = list(COLOR_MAP.values())
        for i, mode in enumerate(game_modes):
            # 循环使用颜色列表
            color = colors[i % len(colors)]
            if self._add_dict_data_safe(
                "gw2_game_modes",
                mode["label"],
                mode["value"],
                dict_sort=i,
                color=color
            ):
                result["created"] += 1
            else:
                result["skipped"] += 1

    def _init_buff_ids(self, result: Dict[str, int]):
        """
        初始化Buff ID数据

        Args:
            result: 结果字典
        """
        default_config = self.load_json_file(self.default_config_path)
        buff_ids = default_config.get("buff_ids", {})
        
        # 为每个Buff ID分配一个颜色
        colors = list(COLOR_MAP.values())
        sort_order = 0
        for buff_name, buff_id in buff_ids.items():
            # 循环使用颜色列表
            color = colors[sort_order % len(colors)]
            if self._add_dict_data_safe(
                "gw2_buff_ids",
                buff_name,
                str(buff_id),
                dict_sort=sort_order,
                color=color
            ):
                result["created"] += 1
            else:
                result["skipped"] += 1
            sort_order += 1

    def get_current_data_summary(self) -> Dict[str, Any]:
        """
        获取当前数据摘要

        Returns:
            数据摘要
        """
        # 暂时返回空摘要，因为db_manager还没有实现相关方法
        return {"total_types": 0, "total_data": 0, "types": []}
