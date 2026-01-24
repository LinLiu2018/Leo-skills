#!/usr/bin/env python3
"""
Leo System - 统一日志系统

提供统一的日志配置和管理功能。
"""
import logging
import sys
from pathlib import Path
from typing import Optional

# 日志目录
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)


# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# 全局日志级别配置
DEFAULT_LOG_LEVEL = logging.INFO


def get_logger(
    name: str,
    level: Optional[int] = None,
    log_to_file: bool = True,
    log_to_console: bool = True,
) -> logging.Logger:
    """
    获取配置好的日志记录器

    Args:
        name: 日志记录器名称（通常使用 __name__）
        level: 日志级别（默认 INFO）
        log_to_file: 是否输出到文件
        log_to_console: 是否输出到控制台

    Returns:
        配置好的 Logger 实例
    """
    logger = logging.getLogger(name)

    # 如果已经配置过，直接返回
    if logger.handlers:
        return logger

    # 设置日志级别
    logger.setLevel(level or DEFAULT_LOG_LEVEL)

    # 创建格式化器
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # 文件处理器
    if log_to_file:
        # 使用模块名作为日志文件名
        log_file = LOGS_DIR / f"{name.replace('.', '_')}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level or DEFAULT_LOG_LEVEL)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # 控制台处理器
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level or DEFAULT_LOG_LEVEL)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def set_log_level(logger: logging.Logger, level: int) -> None:
    """
    设置日志级别

    Args:
        logger: 日志记录器
        level: 日志级别（logging.DEBUG, INFO, WARNING, ERROR, CRITICAL）
    """
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


def clear_log_file(name: str) -> None:
    """
    清空指定的日志文件

    Args:
        name: 日志记录器名称
    """
    log_file = LOGS_DIR / f"{name.replace('.', '_')}.log"
    if log_file.exists():
        log_file.unlink()


# 创建系统级日志记录器
system_logger = get_logger("leo_system")


# 便捷函数
def debug(msg: str, logger_name: str = "leo_system") -> None:
    """记录 DEBUG 级别日志"""
    get_logger(logger_name).debug(msg)


def info(msg: str, logger_name: str = "leo_system") -> None:
    """记录 INFO 级别日志"""
    get_logger(logger_name).info(msg)


def warning(msg: str, logger_name: str = "leo_system") -> None:
    """记录 WARNING 级别日志"""
    get_logger(logger_name).warning(msg)


def error(msg: str, logger_name: str = "leo_system") -> None:
    """记录 ERROR 级别日志"""
    get_logger(logger_name).error(msg)


def critical(msg: str, logger_name: str = "leo_system") -> None:
    """记录 CRITICAL 级别日志"""
    get_logger(logger_name).critical(msg)
