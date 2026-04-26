#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国际化模块

负责处理多语言翻译功能
"""

import os
import json


class I18n:
    """
    国际化类
    """

    def __init__(self, default_locale="zh-CN"):
        """
        初始化国际化类

        Args:
            default_locale: 默认语言区域
        """
        self.default_locale = default_locale
        self.translations = {}
        self.resource_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "resources", "i18n"
        )
        self.load_translations()

    def load_translations(self):
        """
        加载翻译文件
        """
        if not os.path.exists(self.resource_dir):
            return

        for filename in os.listdir(self.resource_dir):
            if filename.endswith(".json"):
                locale = filename[:-5]  # 移除 .json 后缀
                filepath = os.path.join(self.resource_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        self.translations[locale] = json.load(f)
                except Exception as e:
                    print(f"Error loading translation file {filename}: {e}")

    def get(self, key, locale=None, default=None):
        """
        获取翻译值

        Args:
            key: 翻译键
            locale: 语言区域
            default: 默认值

        Returns:
            翻译后的值
        """
        locale = locale or self.default_locale

        if locale not in self.translations:
            locale = self.default_locale

        if locale not in self.translations:
            return default or key

        keys = key.split(".")
        value = self.translations[locale]

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default or key

        return value

    def translate(self, key, locale=None, default=None):
        """
        翻译方法

        Args:
            key: 翻译键
            locale: 语言区域
            default: 默认值

        Returns:
            翻译后的值
        """
        return self.get(key, locale, default)


# 创建全局国际化实例
i18n = I18n()

# 导出翻译方法
translate = i18n.translate

# 导出I18n类
__all__ = ["I18n", "i18n", "translate"]
