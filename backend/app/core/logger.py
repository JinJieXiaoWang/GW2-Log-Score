import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from app.config.config_loader import settings

log_config = settings.logging

log_dir = os.path.dirname(log_config.file)
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir)


class Logger:
    def __init__(self, name=None):
        self.name = name or __name__
        self.logger = self._setup_logger()

    def _setup_logger(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(getattr(logging, log_config.level))

        if not logger.handlers:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, log_config.level))
            console_formatter = logging.Formatter(log_config.format)
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

            rotation_config = log_config.rotation
            max_bytes = (
                rotation_config.max_size
                if hasattr(rotation_config, "max_size")
                else 10485760
            )
            backup_count = (
                rotation_config.backup_count
                if hasattr(rotation_config, "backup_count")
                else 5
            )

            file_handler = RotatingFileHandler(
                log_config.file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8",
            )
            file_handler.setLevel(getattr(logging, log_config.level))
            file_formatter = logging.Formatter(log_config.format)
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


global_logger = Logger()

debug = global_logger.debug
info = global_logger.info
warning = global_logger.warning
error = global_logger.error
critical = global_logger.critical
exception = global_logger.exception

__all__ = ["Logger", "debug", "info", "warning", "error", "critical", "exception"]
