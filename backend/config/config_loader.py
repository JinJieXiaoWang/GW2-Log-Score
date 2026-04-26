import os
import sys
import json
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ConfigLoader:
    def __init__(self):
        self.config_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config"
        )
        self.default_config = self._load_config("default.json")
        self.professions_config = self._load_professions_config()
        self.scoring_rules_config = self._load_scoring_rules_config()
        self.environment = self.default_config.get("environment", "development")
        self.env_config = self._load_config(f"{self.environment}.json")
        self.config = self._merge_configs()

    def _load_scoring_rules_config(self):
        rules_path = os.path.join(self.config_dir, "scoring_rules.json")
        if os.path.exists(rules_path):
            with open(rules_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "version": "unknown",
            "default_threshold": 80,
            "profession_specialization_rules": {},
            "fallback_role_rules": {}
        }

    def _load_config(self, filename):
        config_path = os.path.join(self.config_dir, filename)
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _load_professions_config(self):
        professions_path = os.path.join(self.config_dir, "professions.json")
        if os.path.exists(professions_path):
            with open(professions_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"professions": [], "roles": {}, "professionColors": {}}

    def _merge_configs(self):
        merged = self.default_config.copy()
        self._deep_merge(merged, self.env_config)
        return merged

    def _deep_merge(self, target, source):
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                self._deep_merge(target[key], value)
            else:
                target[key] = value

    def get(self, key, default=None):
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def get_server_config(self):
        return self.get("server", {})

    def get_database_config(self):
        return self.get("database", {})

    def get_upload_config(self):
        return self.get("upload", {})

    def get_logging_config(self):
        return self.get("logging", {})

    def get_security_config(self):
        return self.get("security", {})

    def get_scoring_config(self):
        return self.get("scoring", {})

    def get_buff_ids(self):
        return self.get("buff_ids", {})

    def get_cors_config(self):
        return self.get(
            "cors",
            {
                "allow_origins": ["http://localhost:5173", "http://localhost:3000"],
                "allow_credentials": True,
                "allow_methods": ["*"],
                "allow_headers": ["*"],
            },
        )

    def get_environment(self):
        return self.get("environment", "development")

    def get_professions_config(self):
        return self.professions_config

    def get_roles(self):
        return self.professions_config.get("roles", {})

    def get_profession_colors(self):
        return self.professions_config.get("professionColors", {})

    def get_professions(self):
        return self.professions_config.get("professions", [])

    def get_profession_translations(self):
        translations = {}
        for prof in self.get_professions():
            name = prof.get("name")
            if name:
                translations[name] = name
                if "specializations" in prof:
                    for spec_name in prof["specializations"].keys():
                        translations[spec_name] = spec_name
        return translations

    def get_role_types(self):
        return {
            "DPS": {
                "name": "DPS",
                "color": {
                    "bg": "bg-red-50",
                    "text": "text-red-600",
                    "border": "border-red-200",
                },
            },
            "SUPPORT": {
                "name": "SUPPORT",
                "color": {
                    "bg": "bg-blue-50",
                    "text": "text-blue-600",
                    "border": "border-blue-200",
                },
            },
            "CONDITION": {
                "name": "CONDITION",
                "color": {
                    "bg": "bg-purple-50",
                    "text": "text-purple-600",
                    "border": "border-purple-200",
                },
            },
            "HEALING": {
                "name": "HEALING",
                "color": {
                    "bg": "bg-green-50",
                    "text": "text-green-600",
                    "border": "border-green-200",
                },
            },
            "CONTROL": {
                "name": "CONTROL",
                "color": {
                    "bg": "bg-yellow-50",
                    "text": "text-yellow-600",
                    "border": "border-yellow-200",
                },
            },
            "UTILITY": {
                "name": "UTILITY",
                "color": {
                    "bg": "bg-gray-50",
                    "text": "text-gray-600",
                    "border": "border-gray-200",
                },
            },
        }

    def get_role_type_translations(self):
        return {
            "DPS": "输出",
            "SUPPORT": "辅助",
            "CONDITION": "症状",
            "HEALING": "治疗",
            "CONTROL": "控制",
            "UTILITY": "功能",
        }

    def get_role_config(self):
        role_config = {}
        for prof in self.get_professions():
            prof_name = prof.get("name")
            if not prof_name:
                continue

            role_config[prof_name] = {"core": {"types": [prof.get("defaultRole", "DPS")]}}

            if "specializations" in prof:
                for spec_name, spec_data in prof["specializations"].items():
                    role_config[prof_name][spec_name] = {
                        "types": spec_data.get("types", ["DPS"]),
                        "description": spec_data.get("description", ""),
                        "icon": spec_data.get("icon", ""),
                    }
        return role_config

    def get_profession_default_roles(self):
        default_roles = {}
        for prof in self.get_professions():
            name = prof.get("name")
            default_role = prof.get("defaultRole")
            if name and default_role:
                default_roles[name] = default_role
            if "specializations" in prof:
                for spec_name, spec_data in prof["specializations"].items():
                    types = spec_data.get("types", ["DPS"])
                    if isinstance(types, list):
                        default_roles[spec_name] = types[0]
                    else:
                        default_roles[spec_name] = types
        return default_roles

    def get_profession_role_info(self, profession, specialization):
        role_config = self.get_role_config()
        if profession in role_config and specialization in role_config[profession]:
            return role_config[profession][specialization]
        return None

    def get_profession_color(self, profession):
        colors = self.get_profession_colors()
        if profession in colors:
            return colors[profession]
        for prof in self.get_professions():
            if prof.get("name") == profession:
                return prof.get("colors", {"bg": "bg-gray-100", "text": "text-gray-600"})
        return {"bg": "bg-gray-100", "text": "text-gray-600"}

    def get_profession_role(self, profession):
        default_roles = self.get_profession_default_roles()
        return default_roles.get(profession, "DPS")

    def get_all_profession_names(self):
        return list(self.get_profession_translations().keys())

    def get_all_specializations(self, profession):
        for prof in self.get_professions():
            if prof.get("name") == profession:
                return list(prof.get("specializations", {}).keys())
        return []

    def get_professions_full_data(self):
        professions_list = []
        for prof in self.get_professions():
            prof_name = prof.get("name")
            item = {
                "name": prof_name,
                "colors": prof.get("colors", self.get_profession_color(prof_name)),
                "defaultRole": prof.get("defaultRole", "DPS"),
                "icon": prof.get("icon", ""),
            }

            if "specializations" in prof:
                item["specializations"] = {}
                for spec_name, spec_data in prof["specializations"].items():
                    item["specializations"][spec_name] = {
                        "types": spec_data.get("types", ["DPS"]),
                        "description": spec_data.get("description", ""),
                        "icon": spec_data.get("icon", ""),
                    }

            professions_list.append(item)

        return professions_list

    def get_scoring_rules_version(self):
        return self.scoring_rules_config.get("version", "unknown")

    def get_scoring_rules_mode(self):
        return self.scoring_rules_config.get("mode", "WvW")

    def get_scoring_threshold(self):
        return self.scoring_rules_config.get("default_threshold", 80)

    def get_scoring_dimension_definitions(self):
        return self.scoring_rules_config.get("dimension_definitions", {})

    def get_scoring_normalization_rules(self):
        return self.scoring_rules_config.get("normalization_rules", {})

    def get_scoring_squad_size_rules(self):
        return self.scoring_rules_config.get("squad_size_rules", {
            "small_squad_threshold": 20,
            "small_squad_modifiers": {}
        })

    def get_scoring_profession_specialization_rules(self):
        return self.scoring_rules_config.get("profession_specialization_rules", {})

    def get_scoring_fallback_role_rules(self):
        return self.scoring_rules_config.get("fallback_role_rules", {})

    def get_scoring_rule_for_player(
        self,
        profession: str,
        specialization: str = None,
        stance: str = None,
        weapon: str = None,
        role: str = None
    ):
        rules = self.get_scoring_profession_specialization_rules()

        if stance:
            key = f"{profession}-{specialization}-{stance}"
            if key in rules:
                return rules[key]

        if weapon:
            key = f"{profession}-{specialization}-{weapon}"
            if key in rules:
                return rules[key]

        key = f"{profession}-{specialization}"
        if key in rules:
            return rules[key]

        fallback_rules = self.get_scoring_fallback_role_rules()
        if role and role in fallback_rules:
            return fallback_rules[role]

        return fallback_rules.get("DPS", {})

    def get_scoring_all_rules(self):
        return self.scoring_rules_config

    def save_scoring_rules(self, rules_data, user="system"):
        """保存评分规则配置，支持版本控�?""
        import time
        from datetime import datetime

        rules_path = os.path.join(self.config_dir, "scoring_rules.json")

        # 备份旧版�?        if os.path.exists(rules_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.config_dir, f"scoring_rules_backup_{timestamp}.json")
            import shutil
            shutil.copy2(rules_path, backup_path)

        # 更新版本信息
        if "version" in rules_data:
            current_version = rules_data.get("version", "1.0")
            version_parts = current_version.split(".")
            if len(version_parts) >= 2:
                try:
                    minor = int(version_parts[1]) + 1
                    rules_data["version"] = f"{version_parts[0]}.{minor}"
                except ValueError:
                    pass

        # 添加修改记录
        if "update_history" not in rules_data:
            rules_data["update_history"] = []

        rules_data["update_history"].append({
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "version": rules_data.get("version", "unknown")
        })

        # 保存新配�?        with open(rules_path, "w", encoding="utf-8") as f:
            json.dump(rules_data, f, ensure_ascii=False, indent=2)

        # 重新加载配置
        self.scoring_rules_config = self._load_scoring_rules_config()

        return True

    def get_scoring_rules_backups(self):
        """获取评分规则备份列表"""
        backups = []
        for filename in os.listdir(self.config_dir):
            if filename.startswith("scoring_rules_backup_") and filename.endswith(".json"):
                backup_path = os.path.join(self.config_dir, filename)
                stat = os.stat(backup_path)
                backups.append({
                    "filename": filename,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "size": stat.st_size
                })
        return sorted(backups, key=lambda x: x["created_at"], reverse=True)

    def restore_scoring_rules_from_backup(self, backup_filename):
        """从备份恢复评分规�?""
        backup_path = os.path.join(self.config_dir, backup_filename)
        if not os.path.exists(backup_path):
            return False

        target_path = os.path.join(self.config_dir, "scoring_rules.json")
        import shutil
        shutil.copy2(backup_path, target_path)

        # 重新加载配置
        self.scoring_rules_config = self._load_scoring_rules_config()

        return True


config_loader = ConfigLoader()


def _dict_to_object(d):
    """将嵌套字典转换为支持属性访问的对象"""
    if isinstance(d, dict):
        return types.SimpleNamespace(**{k: _dict_to_object(v) for k, v in d.items()})
    return d


# 从配置加载器中导出全局配置变量，供其他模块使用
settings = _dict_to_object(config_loader.config)
HOST = config_loader.get("server.host", "0.0.0.0")
PORT = config_loader.get("server.port", 8000)
DATABASE_URL = config_loader.get("database.url", "sqlite:///databases/gw2_logs.db")
UPLOAD_DIR = config_loader.get("upload.directory", "uploads/")
MAX_UPLOAD_SIZE = config_loader.get("upload.max_size", 10485760)
LOG_LEVEL = config_loader.get("logging.level", "INFO")
LOG_FILE = config_loader.get("logging.file", "logs/backend.log")
SECRET_KEY = config_loader.get("security.secret_key", "123456789")
SCORE_THRESHOLD = config_loader.get("scoring.threshold", 80)
SCORING_CONFIG = config_loader.get_scoring_config()
BUFF_IDS = config_loader.get_buff_ids()
PROF_ROLES = config_loader.get_roles()
ENVIRONMENT = config_loader.get_environment()
PROFESSIONS = config_loader.get_professions()
PROFESSION_COLORS = config_loader.get_profession_colors()
ROLE_TYPES = config_loader.get_role_types()
ROLE_TYPE_TRANSLATIONS = config_loader.get_role_type_translations()
ROLE_CONFIG = config_loader.get_role_config()
PROFESSIONS_FULL_DATA = config_loader.get_professions_full_data()

