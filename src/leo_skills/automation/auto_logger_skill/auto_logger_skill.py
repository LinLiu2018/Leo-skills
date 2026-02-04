# -*- coding: utf-8 -*-
"""
auto_logger_skill - 自动日志记录技能

自动记录系统活动、事件和状态变更，支持日志轮转和格式化管理。
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import threading


class LogLevel(Enum):
    """日志级别"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class LogCategory(Enum):
    """日志类别"""
    SYSTEM = "system"
    USER = "user"
    TASK = "task"
    ERROR = "error"
    PERFORMANCE = "performance"
    SECURITY = "security"


@dataclass
class LogEntry:
    """日志条目"""
    timestamp: str
    level: str
    category: str
    message: str
    source: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


class AutoLoggerSkill:
    """
    自动日志记录技能

    功能：
    - 自动记录系统活动
    - 支持日志级别过滤
    - 日志文件轮转管理
    - 结构化日志输出
    - 线程安全记录

    使用场景：
    - 记录用户操作
    - 跟踪任务执行
    - 监控性能指标
    - 安全审计日志
    """

    DEFAULT_LOG_DIR = "logs"
    DEFAULT_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    DEFAULT_BACKUP_COUNT = 5

    def __init__(self, log_dir: str = None, level: str = "INFO"):
        self.name = "auto_logger_skill"
        self.version = "1.0.0"
        self.description = "自动日志记录技能 - 记录系统活动和事件"

        self.log_dir = Path(log_dir) if log_dir else Path(self.DEFAULT_LOG_DIR)
        self.log_level = getattr(logging, level.upper(), logging.INFO)
        self._lock = threading.Lock()

        # 初始化日志目录
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 设置Python日志
        self._setup_logger()

    def _setup_logger(self):
        """设置Python日志记录器"""
        self.logger = logging.getLogger(f"leo_{self.name}")
        self.logger.setLevel(self.log_level)

        # 清除已有处理器
        self.logger.handlers.clear()

        # 文件处理器
        log_file = self.log_dir / f"{self.name}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)

        # 格式化
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行日志记录

        Args:
            message: 日志消息
            level: 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
            category: 日志类别 (system/user/task/error/performance/security)
            source: 日志来源
            details: 详细信息字典
            action: 执行动作 (log/rotate/clear/query)

        Returns:
            Dict 包含执行结果
        """
        action = kwargs.get("action", "log")

        try:
            if action == "log":
                return self._log_message(kwargs)
            elif action == "rotate":
                return self._rotate_logs()
            elif action == "clear":
                return self._clear_logs(kwargs.get("before_days", 7))
            elif action == "query":
                return self._query_logs(kwargs)
            else:
                return {"status": "error", "message": f"Unknown action: {action}"}

        except Exception as e:
            return {"status": "error", "error": str(e), "skill": self.name}

    def _log_message(self, kwargs: Dict) -> Dict[str, Any]:
        """记录日志消息"""
        message = kwargs.get("message", "")
        level = kwargs.get("level", "INFO")
        category = kwargs.get("category", "system")
        source = kwargs.get("source", "")
        details = kwargs.get("details", {})

        log_level = getattr(logging, level.upper(), logging.INFO)
        category_enum = LogCategory(category)

        # 创建结构化日志
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level.upper(),
            category=category_enum.value,
            message=message,
            source=source,
            details=details
        )

        # 记录日志
        with self._lock:
            if log_level == logging.DEBUG:
                self.logger.debug(message, extra={'details': details})
            elif log_level == logging.INFO:
                self.logger.info(message, extra={'details': details})
            elif log_level == logging.WARNING:
                self.logger.warning(message, extra={'details': details})
            elif log_level == logging.ERROR:
                self.logger.error(message, extra={'details': details})
            elif log_level == logging.CRITICAL:
                self.logger.critical(message, extra={'details': details})

        # 保存结构化日志
        self._save_structured_log(entry)

        return {
            "status": "success",
            "skill": self.name,
            "logged": {
                "timestamp": entry.timestamp,
                "level": entry.level,
                "category": entry.category,
                "message": entry.message
            }
        }

    def _save_structured_log(self, entry: LogEntry):
        """保存结构化日志到JSON文件"""
        log_file = self.log_dir / f"{entry.category}_logs.jsonl"
        with self._lock:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry.__dict__, ensure_ascii=False) + '\n')

    def _rotate_logs(self) -> Dict[str, Any]:
        """日志轮转"""
        rotated = []
        for log_file in self.log_dir.glob("*.log"):
            if log_file.stat().st_size > self.DEFAULT_MAX_SIZE:
                # 创建备份
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup = log_file.with_suffix(f".{timestamp}.backup")
                log_file.rename(backup)
                rotated.append(str(backup))

        return {
            "status": "success",
            "skill": self.name,
            "rotated_files": rotated
        }

    def _clear_logs(self, before_days: int) -> Dict[str, Any]:
        """清理旧日志"""
        cutoff = datetime.now() - timedelta(days=before_days)
        cleared = []

        for log_file in self.log_dir.glob("*.log*"):
            if log_file.stat().st_mtime < cutoff.timestamp():
                log_file.unlink()
                cleared.append(str(log_file))

        return {
            "status": "success",
            "skill": self.name,
            "cleared_files": cleared
        }

    def _query_logs(self, kwargs: Dict) -> Dict[str, Any]:
        """查询日志"""
        category = kwargs.get("category")
        level = kwargs.get("level")
        start_time = kwargs.get("start_time")
        end_time = kwargs.get("end_time")
        keyword = kwargs.get("keyword", "")

        entries = []
        log_file = self.log_dir / f"{category or 'leo_auto_logger_skill'}_logs.jsonl"

        if not log_file.exists():
            return {"status": "success", "entries": []}

        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line)
                # 过滤
                if category and entry.get("category") != category:
                    continue
                if level and entry.get("level") != level.upper():
                    continue
                if keyword and keyword not in entry.get("message", ""):
                    continue
                entries.append(entry)

        return {
            "status": "success",
            "skill": self.name,
            "entries": entries[-100:]  # 最多返回100条
        }

    def log_user_action(self, user_id: str, action: str, **extra):
        """记录用户操作"""
        return self.execute(
            message=f"User {user_id} performed: {action}",
            level="INFO",
            category="user",
            source=user_id,
            details={"action": action, **extra}
        )

    def log_task_event(self, task_id: str, event: str, **extra):
        """记录任务事件"""
        return self.execute(
            message=f"Task {task_id}: {event}",
            level="INFO",
            category="task",
            source=task_id,
            details={"event": event, **extra}
        )

    def log_error(self, error: str, source: str = "", **extra):
        """记录错误"""
        return self.execute(
            message=error,
            level="ERROR",
            category="error",
            source=source,
            details=extra
        )

    def log_performance(self, operation: str, duration_ms: float, **extra):
        """记录性能指标"""
        return self.execute(
            message=f"Performance: {operation} took {duration_ms}ms",
            level="INFO",
            category="performance",
            source=operation,
            details={"duration_ms": duration_ms, **extra}
        )

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "features": [
                "structured_logging",
                "log_rotation",
                "log_query",
                "log_clear",
                "user_action_tracking",
                "task_event_logging",
                "performance_monitoring"
            ],
            "log_levels": [e.name for e in LogLevel],
            "log_categories": [e.value for e in LogCategory],
            "default_log_dir": str(self.log_dir)
        }


# 向后兼容
Auto_Logger_Skill = AutoLoggerSkill


def main():
    """入口函数 - 演示用法"""
    print("=" * 60)
    print("Auto Logger Skill - 演示")
    print("=" * 60)

    skill = AutoLoggerSkill()

    # 演示1: 记录普通日志
    print("\n1. 记录普通日志")
    print("-" * 40)
    result = skill.execute(
        message="系统启动完成",
        level="INFO",
        category="system"
    )
    print(f"结果: {result}")

    # 演示2: 记录用户操作
    print("\n2. 记录用户操作")
    print("-" * 40)
    result = skill.log_user_action(
        user_id="user_001",
        action="login",
        ip="192.168.1.100"
    )
    print(f"结果: {result}")

    # 演示3: 记录性能指标
    print("\n3. 记录性能指标")
    print("-" * 40)
    result = skill.log_performance(
        operation="database_query",
        duration_ms=45.6,
        query="SELECT * FROM users"
    )
    print(f"结果: {result}")

    # 演示4: 记录错误
    print("\n4. 记录错误")
    print("-" * 40)
    result = skill.log_error(
        error="数据库连接失败",
        source="db_manager",
        retry_count=3
    )
    print(f"结果: {result}")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return skill


if __name__ == "__main__":
    main()
