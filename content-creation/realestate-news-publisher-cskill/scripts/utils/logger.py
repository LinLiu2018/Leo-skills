# Logger Module
# 日志模块

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


class Logger:
    """日志管理器"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.loggers = {}

    def setup(self,
              name: str = "realestate_publisher",
              log_file: Optional[str] = None,
              level: str = "INFO",
              max_bytes: int = 10 * 1024 * 1024,
              backup_count: int = 5) -> logging.Logger:
        """
        设置日志器

        Args:
            name: 日志器名称
            log_file: 日志文件路径
            level: 日志级别
            max_bytes: 单个日志文件最大大小
            backup_count: 保留的日志文件数量

        Returns:
            配置好的日志器
        """
        if name in self.loggers:
            return self.loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))

        # 清除现有处理器
        logger.handlers.clear()

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # 控制台格式
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)

        # 文件处理器
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))

            # 文件格式
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)

        self.loggers[name] = logger
        return logger

    def get_logger(self, name: str = "realestate_publisher") -> logging.Logger:
        """获取日志器"""
        if name not in self.loggers:
            return self.setup(name)
        return self.loggers[name]


# 全局日志器实例
_logger_instance = Logger()


def get_logger(name: str = "realestate_publisher") -> logging.Logger:
    """获取日志器的便捷函数"""
    return _logger_instance.get_logger(name)
