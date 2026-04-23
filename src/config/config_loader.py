import os
import sys
import json

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ConfigLoader:
    def __init__(self):
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
        self.default_config = self._load_config('default.json')
        self.environment = self.default_config.get('environment', 'development')
        self.env_config = self._load_config(f'{self.environment}.json')
        self.config = self._merge_configs()
    
    def _load_config(self, filename):
        config_path = os.path.join(self.config_dir, filename)
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _merge_configs(self):
        merged = self.default_config.copy()
        self._deep_merge(merged, self.env_config)
        return merged
    
    def _deep_merge(self, target, source):
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    def get(self, key, default=None):
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def get_server_config(self):
        return self.get('server', {})
    
    def get_database_config(self):
        return self.get('database', {})
    
    def get_upload_config(self):
        return self.get('upload', {})
    
    def get_logging_config(self):
        return self.get('logging', {})
    
    def get_security_config(self):
        return self.get('security', {})
    
    def get_scoring_config(self):
        return self.get('scoring', {})
    
    def get_buff_ids(self):
        return self.get('buff_ids', {})
    
    def get_prof_roles(self):
        return self.get('prof_roles', {})
    
    def get_cors_config(self):
        return self.get('cors', {
            'allow_origins': ['http://localhost:5173', 'http://localhost:3000'],
            'allow_credentials': True,
            'allow_methods': ['*'],
            'allow_headers': ['*']
        })
    
    def get_professions_config(self):
        return self.get('professions', [])

    def get_professions(self):
        professions = self.get('professions', [])
        if isinstance(professions, list):
            # 从数组中提取翻译
            translations = {}
            for item in professions:
                # 找到职业名称的键（第一个键）
                profession_key = next((key for key in item.keys() if key not in ['colors', 'core', 'defaultRole', 'SUPPORT', 'DPS', 'CONDITION', 'HEALING', 'CONTROL', 'UTILITY']), None)
                if profession_key:
                    translations[profession_key] = item[profession_key]
            return translations
        return self.get('professions.translations', {})

    def get_profession_colors(self):
        professions = self.get('professions', [])
        if isinstance(professions, list):
            # 从数组中提取颜色
            colors = {}
            for item in professions:
                # 找到职业名称的键（第一个键）
                profession_key = next((key for key in item.keys() if key not in ['colors', 'core', 'defaultRole', 'SUPPORT', 'DPS', 'CONDITION', 'HEALING', 'CONTROL', 'UTILITY']), None)
                if profession_key and 'colors' in item:
                    colors[profession_key] = item['colors']
            return colors
        return self.get('professions.colors', {})

    def get_role_types(self):
        # 直接返回角色类型配置，因为这部分没有改变
        return {
            "DPS": {"name": "DPS", "color": {"bg": "bg-red-50", "text": "text-red-600", "border": "border-red-200"}},
            "SUPPORT": {"name": "SUPPORT", "color": {"bg": "bg-blue-50", "text": "text-blue-600", "border": "border-blue-200"}},
            "CONDITION": {"name": "CONDITION", "color": {"bg": "bg-purple-50", "text": "text-purple-600", "border": "border-purple-200"}},
            "HEALING": {"name": "HEALING", "color": {"bg": "bg-green-50", "text": "text-green-600", "border": "border-green-200"}},
            "CONTROL": {"name": "CONTROL", "color": {"bg": "bg-yellow-50", "text": "text-yellow-600", "border": "border-yellow-200"}},
            "UTILITY": {"name": "UTILITY", "color": {"bg": "bg-gray-50", "text": "text-gray-600", "border": "border-gray-200"}}
        }

    def get_role_type_translations(self):
        # 直接返回角色类型翻译，因为这部分没有改变
        return {
            "DPS": "输出",
            "SUPPORT": "辅助",
            "CONDITION": "症状",
            "HEALING": "治疗",
            "CONTROL": "控制",
            "UTILITY": "功能"
        }

    def get_role_config(self):
        professions = self.get('professions', [])
        if isinstance(professions, list):
            # 从数组中提取角色配置
            role_config = {}
            for item in professions:
                # 找到职业名称的键（第一个键）
                profession_key = next((key for key in item.keys() if key not in ['colors', 'core', 'defaultRole', 'SUPPORT', 'DPS', 'CONDITION', 'HEALING', 'CONTROL', 'UTILITY']), None)
                if profession_key and 'core' in item:
                    # 确定职业类别（核心职业还是精英特长）
                    is_core_profession = profession_key in ['Guardian', 'Warrior', 'Engineer', 'Ranger', 'Thief', 'Elementalist', 'Mesmer', 'Necromancer', 'Revenant']
                    
                    if is_core_profession:
                        # 核心职业
                        if profession_key not in role_config:
                            role_config[profession_key] = {}
                        role_config[profession_key]['core'] = item['core']
                    else:
                        # 精英特长，需要确定所属的核心职业
                        core_profession = ''
                        if profession_key in ['Firebrand', 'Willbender', 'Dragonhunter']:
                            core_profession = 'Guardian'
                        elif profession_key in ['Berserker', 'Spellbreaker', 'Bladesworn']:
                            core_profession = 'Warrior'
                        elif profession_key in ['Scrapper', 'Holosmith', 'Mechanist', 'Kinetic']:
                            core_profession = 'Engineer'
                        elif profession_key in ['Druid', 'Soulbeast', 'Untamed', 'Sylvarin']:
                            core_profession = 'Ranger'
                        elif profession_key in ['Daredevil', 'Deadeye', 'Specter', 'Nightblade']:
                            core_profession = 'Thief'
                        elif profession_key in ['Tempest', 'Weaver', 'Catalyst', 'Animist']:
                            core_profession = 'Elementalist'
                        elif profession_key in ['Chronomancer', 'Mirage', 'Virtuoso', 'Bard']:
                            core_profession = 'Mesmer'
                        elif profession_key in ['Reaper', 'Scourge', 'Harbinger', 'Ritualist']:
                            core_profession = 'Necromancer'
                        elif profession_key in ['Herald', 'Renegade', 'Vindicator', 'ForbiddenOathkeeper']:
                            core_profession = 'Revenant'
                        
                        if core_profession:
                            if core_profession not in role_config:
                                role_config[core_profession] = {}
                            role_config[core_profession][profession_key] = item['core']
            return role_config
        return self.get('professions.role_config', {})

    def get_profession_default_roles(self):
        professions = self.get('professions', [])
        if isinstance(professions, list):
            # 从数组中提取默认角色
            default_roles = {}
            for item in professions:
                # 找到职业名称的键（第一个键）
                profession_key = next((key for key in item.keys() if key not in ['colors', 'core', 'defaultRole', 'SUPPORT', 'DPS', 'CONDITION', 'HEALING', 'CONTROL', 'UTILITY']), None)
                if profession_key and 'defaultRole' in item and item['defaultRole']:
                    default_roles[profession_key] = item['defaultRole']
            return default_roles
        return self.get('professions.default_roles', {})

    def get_profession_role_info(self, profession, specialization):
        role_config = self.get_role_config()
        if profession in role_config and specialization in role_config[profession]:
            return role_config[profession][specialization]
        return None

    def get_profession_translation(self, profession):
        translations = self.get_professions()
        return translations.get(profession, profession)

    def get_profession_color(self, profession):
        colors = self.get_profession_colors()
        return colors.get(profession, {'bg': 'bg-gray-100', 'text': 'text-gray-600'})

    def get_profession_role(self, profession):
        default_roles = self.get_profession_default_roles()
        return default_roles.get(profession, 'DPS')

    def get_all_profession_names(self):
        translations = self.get_professions()
        return list(translations.keys())

    def get_all_specializations(self, profession):
        role_config = self.get_role_config()
        if profession in role_config:
            return list(role_config[profession].keys())
        return []

    def get_professions_full_data(self):
        professions = self.get('professions', [])
        if isinstance(professions, list):
            return professions
        # 兼容旧格式
        return {
            'translations': self.get_professions(),
            'colors': self.get_profession_colors(),
            'role_types': self.get_role_types(),
            'role_type_translations': self.get_role_type_translations(),
            'role_config': self.get_role_config(),
            'default_roles': self.get_profession_default_roles()
        }

    def get_environment(self):
        return self.get('environment', 'development')

# 创建全局配置实例
config_loader = ConfigLoader()

# 导出配置对象
class Settings:
    def __init__(self):
        server_config = config_loader.get_server_config()
        self.host = server_config.get('host', '0.0.0.0')
        self.port = server_config.get('port', 8000)
        
        database_config = config_loader.get_database_config()
        self.database_url = database_config.get('url', 'sqlite:///databases/gw2_logs.db')
        
        upload_config = config_loader.get_upload_config()
        self.upload_dir = upload_config.get('directory', 'uploads/')
        self.max_upload_size = upload_config.get('max_size', 10485760)
        
        logging_config = config_loader.get_logging_config()
        self.log_level = logging_config.get('level', 'INFO')
        self.log_file = logging_config.get('file', 'logs/backend.log')
        self.log_format = logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.log_rotation = logging_config.get('rotation', {})
        
        security_config = config_loader.get_security_config()
        self.secret_key = security_config.get('secret_key', 'your-secret-key-here')
        
        scoring_config = config_loader.get_scoring_config()
        self.score_threshold = scoring_config.get('threshold', 80)
        self.scoring_config = scoring_config.get('config', {})
        
        self.buff_ids = config_loader.get_buff_ids()
        self.prof_roles = config_loader.get_profession_default_roles()
        self.environment = config_loader.get_environment()
        self.cors = config_loader.get_cors_config()
        self.professions = config_loader.get_professions()
        self.profession_colors = config_loader.get_profession_colors()
        self.role_types = config_loader.get_role_types()
        self.role_type_translations = config_loader.get_role_type_translations()
        self.role_config = config_loader.get_role_config()
        self.professions_full_data = config_loader.get_professions_full_data()

settings = Settings()

# 向后兼容的变量
HOST = settings.host
PORT = settings.port
DATABASE_URL = settings.database_url
UPLOAD_DIR = settings.upload_dir
MAX_UPLOAD_SIZE = settings.max_upload_size
LOG_LEVEL = settings.log_level
LOG_FILE = settings.log_file
SECRET_KEY = settings.secret_key
SCORE_THRESHOLD = settings.score_threshold
SCORING_CONFIG = settings.scoring_config
BUFF_IDS = settings.buff_ids
PROF_ROLES = settings.prof_roles
ENVIRONMENT = settings.environment
PROFESSIONS = settings.professions
PROFESSION_COLORS = settings.profession_colors
ROLE_TYPES = settings.role_types
ROLE_TYPE_TRANSLATIONS = settings.role_type_translations
ROLE_CONFIG = settings.role_config
PROFESSIONS_FULL_DATA = settings.professions_full_data
