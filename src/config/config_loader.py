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
        self.prof_roles = config_loader.get_prof_roles()
        self.environment = config_loader.get_environment()
        self.cors = config_loader.get_cors_config()

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
