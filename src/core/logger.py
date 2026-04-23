import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from src.config import settings

# 确保日志目录存在
log_dir = os.path.dirname(settings.log_file)
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir)

class Logger:
    def __init__(self, name=None):
        self.name = name or __name__
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(getattr(logging, settings.log_level))
        
        # 避免重复添加处理器
        if not logger.handlers:
            # 控制台处理器
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, settings.log_level))
            console_formatter = logging.Formatter(settings.log_format)
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
            
            # 文件处理器（带轮转）
            rotation_config = settings.log_rotation
            max_bytes = rotation_config.get('max_size', 10485760)
            backup_count = rotation_config.get('backup_count', 5)
            
            file_handler = RotatingFileHandler(
                settings.log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, settings.log_level))
            file_formatter = logging.Formatter(settings.log_format)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def debug(self, message, *args, **kwargs):
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message, *args, **kwargs):
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message, *args, **kwargs):
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message, *args, **kwargs):
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message, *args, **kwargs):
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message, *args, **kwargs):
        self.logger.exception(message, *args, **kwargs)

# 创建全局日志实例
global_logger = Logger()

# 导出日志方法
debug = global_logger.debug
info = global_logger.info
warning = global_logger.warning
error = global_logger.error
critical = global_logger.critical
exception = global_logger.exception

# 导出Logger类
__all__ = ['Logger', 'debug', 'info', 'warning', 'error', 'critical', 'exception']
