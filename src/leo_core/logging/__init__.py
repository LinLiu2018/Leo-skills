"""
Leo Core Logging - 标准化日志系统

提供结构化日志配置和使用接口。
"""

from __future__ import annotations

import logging
import sys
import json
from datetime import datetime
from enum import Enum
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional
from functools import wraps

# ============================================================
# 日志级别
# ============================================================

class LogLevel(str, Enum):
    """日志级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# ============================================================
# 日志格式器
# ============================================================

class StructuredFormatter(logging.Formatter):
    """结构化日志格式器"""

    def __init__(self, format_json: bool = False):
        super().__init__()
        self.format_json = format_json

    def format(self, record: logging.LogRecord) -> str:
        if self.format_json:
            return self._format_json(record)
        return self._format_human(record)

    def _format_json(self, record: logging.LogRecord) -> str:
        """JSON 格式"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # 添加额外字段
        if hasattr(record, "extra"):
            log_data["extra"] = record.extra

        return json.dumps(log_data)

    def _format_human(self, record: logging.LogRecord) -> str:
        """人类可读格式"""
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        level = record.levelname.ljust(8)
        logger = record.name.ljust(30)
        message = record.getMessage()

        parts = [f"{timestamp} | {level} | {logger} | {message}"]

        # 添加额外字段
        if hasattr(record, "extra"):
            extra_parts = [f"{k}={v}" for k, v in record.extra.items()]
            if extra_parts:
                parts.append(" | ".join(extra_parts))

        result = " | ".join(parts)

        if record.exc_info:
            result += "\n" + self.formatException(record.exc_info)

        return result


class ColoredFormatter(ColoredFormatter):
    """彩色日志格式器（仅控制台）"""

    COLORS = {
        "DEBUG": "\033[36m",    # 青色
        "INFO": "\033[32m",     # 绿色
        "WARNING": "\033[33m",  # 黄色
        "ERROR": "\033[31m",    # 红色
        "CRITICAL": "\033[35m", # 紫色
        "RESET": "\033[0m",
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]

        # 添加颜色
        record.levelname = f"{color}{record.levelname}{reset}"
        record.name = f"{color}{record.name}{reset}"

        return super().format(record)


# ============================================================
# 日志配置
# ============================================================

class LogConfig:
    """日志配置"""

    def __init__(
        self,
        level: str = "INFO",
        log_file: Optional[str] = None,
        format_json: bool = False,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
    ):
        self.level = level
        self.log_file = log_file
        self.format_json = format_json
        self.max_bytes = max_bytes
        self.backup_count = backup_count


# ============================================================
# 日志管理器
# ============================================================

class LogManager:
    """日志管理器"""

    _instance: Optional[LogManager] = None
    _loggers: Dict[str, logging.Logger] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._config = LogConfig()

    def configure(self, config: LogConfig) -> None:
        """配置日志系统"""
        self._config = config
        self._setup_root_logger()

    def _setup_root_logger(self) -> None:
        """设置根日志器"""
        config = self._config

        # 根日志器
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, config.level.upper()))

        # 清除现有处理器
        root_logger.handlers.clear()

        # 人类可读格式（控制台）
        if not config.format_json:
            console_formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            console = logging.StreamHandler(sys.stdout)
            console.setFormatter(console_formatter)
            root_logger.addHandler(console)

        # JSON 格式（文件）
        if config.log_file:
            # 确保目录存在
            log_path = Path(config.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_formatter = StructuredFormatter(format_json=config.format_json)
            file_handler = RotatingFileHandler(
                config.log_file,
                maxBytes=config.max_bytes,
                backupCount=config.backup_count,
                encoding="utf-8",
            )
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)

    def get_logger(self, name: str) -> logging.Logger:
        """获取日志器"""
        if name not in self._loggers:
            logger = logging.getLogger(name)
            self._loggers[name] = logger
        return self._loggers[name]


# ============================================================
# 便捷函数
# ============================================================

def get_logger(name: str) -> logging.Logger:
    """获取日志器便捷函数"""
    manager = LogManager()
    return manager.get_logger(name)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_json: bool = False,
) -> None:
    """设置日志便捷函数"""
    config = LogConfig(
        level=level,
        log_file=log_file,
        format_json=format_json,
    )
    manager = LogManager()
    manager.configure(config)


# ============================================================
# 结构化日志辅助
# ============================================================

class LoggerAdapter(logging.LoggerAdapter):
    """带额外字段的日志适配器"""

    def process(self, msg: str, kwargs: dict) -> tuple:
        # 将 extra 合并到 kwargs
        if "extra" in kwargs:
            kwargs["extra"].update(self.extra)
        else:
            kwargs["extra"] = self.extra.copy()
        return msg, kwargs


def log_execution(logger: logging.Logger):
    """函数执行日志装饰器"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__qualname__
            logger.debug(f"Executing {func_name}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Completed {func_name}")
                return result
            except Exception as e:
                logger.error(f"Error in {func_name}: {e}", exc_info=True)
                raise

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            func_name = func.__qualname__
            logger.debug(f"Executing {func_name}")
            try:
                result = await func(*args, **kwargs)
                logger.debug(f"Completed {func_name}")
                return result
            except Exception as e:
                logger.error(f"Error in {func_name}: {e}", exc_info=True)
                raise

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper

    return decorator


def log_async_execution(logger: logging.Logger):
    """异步函数执行日志装饰器"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            func_name = func.__qualname__
            logger.debug(f"Starting {func_name}")
            start_time = datetime.now()
            try:
                result = await func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                logger.info(f"Completed {func_name} in {duration:.2f}s")
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                logger.error(
                    f"Failed {func_name} after {duration:.2f}s: {e}",
                    exc_info=True
                )
                raise

        return wrapper

    return decorator


# ============================================================
# 上下文日志
# ============================================================

class ContextLogger:
    """上下文日志器 - 支持添加上下文信息"""

    def __init__(self, logger: logging.Logger, context: Dict[str, Any]):
        self.logger = logger
        self.context = context

    def _add_context(self, kwargs: dict) -> dict:
        """添加上下文"""
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        kwargs["extra"].update(self.context)
        return kwargs

    def debug(self, msg: str, **kwargs):
        self.logger.debug(msg, **self._add_context(kwargs))

    def info(self, msg: str, **kwargs):
        self.logger.info(msg, **self._add_context(kwargs))

    def warning(self, msg: str, **kwargs):
        self.logger.warning(msg, **self._add_context(kwargs))

    def error(self, msg: str, **kwargs):
        self.logger.error(msg, **self._add_context(kwargs))

    def critical(self, msg: str, **kwargs):
        self.logger.critical(msg, **self._add_context(kwargs))


def create_context_logger(logger: logging.Logger, **context) -> ContextLogger:
    """创建带上下文的日志器"""
    return ContextLogger(logger, context)
