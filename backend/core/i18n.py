import os
import json


class I18n:
    def __init__(self, default_locale="zh-CN"):
        self.default_locale = default_locale
        self.translations = {}
        self.resource_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "resources", "i18n"
        )
        self.load_translations()

    def load_translations(self):
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
        return self.get(key, locale, default)


# 创建全局国际化实�?i18n = I18n()

# 导出翻译方法
translate = i18n.translate

# 导出I18n�?__all__ = ["I18n", "i18n", "translate"]

