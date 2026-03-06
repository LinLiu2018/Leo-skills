# -*- coding: utf-8 -*-
"""
统一日志系统

提供结构化日志收集和管理能力
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class LogLevel(str, Enum):
    """日志级别"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class LogEntry:
    """日志条目"""
    log_id: str
    timestamp: datetime
    level: LogLevel
    message: str
    source: str = ""
    skill: str = ""
    action: str = ""
    user: str = ""
    session_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    stack_trace: str = ""
    duration_ms: int = 0

    def to_dict(self) -> Dict:
        return {
            "log_id": self.log_id,
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "message": self.message,
            "source": self.source,
            "skill": self.skill,
            "action": self.action,
            "user": self.user,
            "session_id": self.session_id,
            "metadata": self.metadata,
            "stack_trace": self.stack_trace,
            "duration_ms": self.duration_ms
        }


class UnifiedLogger:
    """
    统一日志系统

    提供：
    - 结构化日志记录
    - 自动归类存储
    - 日志查询
    - 日志分析报告
    """

    def __init__(self, storage_path: str = ".leo_logs"):
        self.storage_path = Path(storage_path)
        self._logs: List[LogEntry] = []
        self._log_counter = 0

        # 确保目录存在
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # 索引文件
        self.index_file = self.storage_path / "index.json"
        self._load_index()

    def _load_index(self):
        """加载索引"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._log_counter = data.get("counter", 0)
            except Exception as e:
                print(f"[Logger] Failed to load index: {e}")

    def _save_index(self):
        """保存索引"""
        try:
            data = {"counter": self._log_counter}
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[Logger] Failed to save index: {e}")

    # ========== 日志记录 ==========

    def log(
        self,
        level: str,
        message: str,
        source: str = "",
        skill: str = "",
        action: str = "",
        user: str = "",
        session_id: str = "",
        metadata: Optional[Dict] = None,
        stack_trace: str = "",
        duration_ms: int = 0
    ) -> LogEntry:
        """
        记录日志

        Args:
            level: 日志级别
            message: 日志消息
            source: 来源模块
            skill: 技能名称
            action: 操作名称
            user: 用户
            session_id: 会话ID
            metadata: 额外数据
            stack_trace: 堆栈跟踪
            duration_ms: 耗时

        Returns:
            日志条目
        """
        self._log_counter += 1

        entry = LogEntry(
            log_id=f"log_{self._log_counter:08d}",
            timestamp=datetime.now(),
            level=LogLevel(level),
            message=message,
            source=source,
            skill=skill,
            action=action,
            user=user,
            session_id=session_id,
            metadata=metadata or {},
            stack_trace=stack_trace,
            duration_ms=duration_ms
        )

        # 内存缓存
        self._logs.append(entry)

        # 限制内存缓存大小
        if len(self._logs) > 10000:
            self._logs = self._logs[-5000:]

        # 持久化（批量）
        if self._log_counter % 100 == 0:
            self._persist_logs()

        return entry

    def debug(self, message: str, **kwargs) -> LogEntry:
        """记录调试日志"""
        return self.log("debug", message, **kwargs)

    def info(self, message: str, **kwargs) -> LogEntry:
        """记录信息日志"""
        return self.log("info", message, **kwargs)

    def warning(self, message: str, **kwargs) -> LogEntry:
        """记录警告日志"""
        return self.log("warning", message, **kwargs)

    def error(self, message: str, **kwargs) -> LogEntry:
        """记录错误日志"""
        return self.log("error", message, **kwargs)

    def critical(self, message: str, **kwargs) -> LogEntry:
        """记录严重错误日志"""
        return self.log("critical", message, **kwargs)

    # ========== 技能执行日志 ==========

    def log_skill_execution(
        self,
        skill: str,
        action: str,
        status: str,
        duration_ms: int = 0,
        error: str = "",
        metadata: Optional[Dict] = None
    ) -> LogEntry:
        """记录技能执行日志"""
        level = "info" if status == "success" else "error"
        message = f"Skill execution {status}: {skill}.{action}"

        if error:
            message += f" - Error: {error}"

        return self.log(
            level=level,
            message=message,
            skill=skill,
            action=action,
            metadata=metadata or {},
            duration_ms=duration_ms,
            stack_trace=error if status == "error" else ""
        )

    def log_api_call(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        duration_ms: int = 0,
        error: str = ""
    ) -> LogEntry:
        """记录API调用日志"""
        level = "info" if status_code < 400 else "error"
        message = f"API {method} {endpoint} - Status: {status_code}"

        return self.log(
            level=level,
            message=message,
            source="api",
            metadata={
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code
            },
            duration_ms=duration_ms,
            stack_trace=error
        )

    # ========== 查询 ==========

    def query(
        self,
        level: Optional[str] = None,
        skill: Optional[str] = None,
        source: Optional[str] = None,
        action: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        search: Optional[str] = None,
        limit: int = 1000
    ) -> List[LogEntry]:
        """
        查询日志

        Args:
            level: 日志级别筛选
            skill: 技能名称筛选
            source: 来源筛选
            action: 操作筛选
            since: 开始时间
            until: 结束时间
            search: 关键词搜索
            limit: 返回数量限制

        Returns:
            匹配的日志列表
        """
        results = self._logs

        # 筛选
        if level:
            results = [l for l in results if l.level.value == level]
        if skill:
            results = [l for l in results if l.skill == skill]
        if source:
            results = [l for l in results if l.source == source]
        if action:
            results = [l for l in results if l.action == action]
        if since:
            results = [l for l in results if l.timestamp >= since]
        if until:
            results = [l for l in results if l.timestamp <= until]
        if search:
            search_lower = search.lower()
            results = [l for l in results if search_lower in l.message.lower()]

        # 返回最近的
        return results[-limit:]

    def get_recent(self, limit: int = 100) -> List[LogEntry]:
        """获取最近的日志"""
        return self._logs[-limit:]

    def get_by_id(self, log_id: str) -> Optional[LogEntry]:
        """根据ID获取日志"""
        for log in reversed(self._logs):
            if log.log_id == log_id:
                return log
        return None

    # ========== 统计 ==========

    def get_stats(
        self,
        since: Optional[datetime] = None,
        by_level: bool = True,
        by_skill: bool = True,
        by_hour: bool = False
    ) -> Dict[str, Any]:
        """
        获取日志统计

        Args:
            since: 统计起始时间
            by_level: 按级别统计
            by_skill: 按技能统计
            by_hour: 按小时统计

        Returns:
            统计数据
        """
        logs = self._logs
        if since:
            logs = [l for l in logs if l.timestamp >= since]

        stats = {
            "total": len(logs),
            "since": since.isoformat() if since else None
        }

        # 按级别统计
        if by_level:
            level_counts = {}
            for level in LogLevel:
                count = sum(1 for l in logs if l.level == level)
                level_counts[level.value] = count
            stats["by_level"] = level_counts

        # 按技能统计
        if by_skill:
            skill_counts = {}
            for log in logs:
                if log.skill:
                    skill_counts[log.skill] = skill_counts.get(log.skill, 0) + 1
            stats["by_skill"] = skill_counts

        # 按小时统计
        if by_hour:
            hour_counts = {}
            for log in logs:
                hour_key = log.timestamp.strftime("%Y-%m-%d %H:00")
                hour_counts[hour_key] = hour_counts.get(hour_key, 0) + 1
            stats["by_hour"] = hour_counts

        return stats

    # ========== 持久化 ==========

    def _persist_logs(self):
        """持久化日志"""
        if not self._logs:
            return

        # 按日期保存
        date_str = datetime.now().strftime("%Y%m%d")
        log_file = self.storage_path / f"logs_{date_str}.jsonl"

        # 读取现有日志
        existing = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            existing.append(json.loads(line))
            except:
                pass

        # 添加新日志
        existing.extend([log.to_dict() for log in self._logs[-100:]])

        # 保存
        with open(log_file, 'w', encoding='utf-8') as f:
            for entry in existing[-10000:]:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        self._save_index()

    def load_logs(self, date: Optional[str] = None) -> List[LogEntry]:
        """加载指定日期的日志"""
        date_str = date or datetime.now().strftime("%Y%m%d")
        log_file = self.storage_path / f"logs_{date_str}.jsonl"

        if not log_file.exists():
            return []

        logs = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue

                data = json.loads(line)
                logs.append(LogEntry(
                    log_id=data["log_id"],
                    timestamp=datetime.fromisoformat(data["timestamp"]),
                    level=LogLevel(data["level"]),
                    message=data["message"],
                    source=data.get("source", ""),
                    skill=data.get("skill", ""),
                    action=data.get("action", ""),
                    user=data.get("user", ""),
                    session_id=data.get("session_id", ""),
                    metadata=data.get("metadata", {}),
                    stack_trace=data.get("stack_trace", ""),
                    duration_ms=data.get("duration_ms", 0)
                ))

        return logs

    def clear_memory_logs(self, before: Optional[datetime] = None):
        """清理内存日志"""
        if not before:
            self._logs.clear()
            return

        self._logs = [l for l in self._logs if l.timestamp >= before]


# 全局日志器
_global_logger: Optional[UnifiedLogger] = None


def get_unified_logger() -> UnifiedLogger:
    """获取全局日志器"""
    global _global_logger
    if _global_logger is None:
        _global_logger = UnifiedLogger()
    return _global_logger
