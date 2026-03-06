# -*- coding: utf-8 -*-
"""
任务定义模块

定义调度任务的数据结构和状态管理
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"          # 等待执行
    RUNNING = "running"          # 执行中
    SUCCESS = "success"         # 执行成功
    FAILED = "failed"           # 执行失败
    RETRYING = "retrying"       # 重试中
    CANCELLED = "cancelled"     # 已取消
    SKIPPED = "skipped"         # 已跳过


class TaskPriority(str, Enum):
    """任务优先级"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TaskResult:
    """任务执行结果"""
    task_id: str
    status: TaskStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    output: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    duration_ms: int = 0

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "output": self.output,
            "error": self.error,
            "retry_count": self.retry_count,
            "duration_ms": self.duration_ms,
        }


@dataclass
class ScheduledTask:
    """
    定时任务定义

    Attributes:
        task_id: 唯一任务ID
        name: 任务名称
        skill_path: 技能路径
        cron_expr: Cron 表达式
        enabled: 是否启用
        priority: 优先级
        timeout: 超时时间(秒)
        retry_policy: 重试策略配置
        dependencies: 依赖任务ID列表
        last_run: 上次执行时间
        next_run: 下次执行时间
        status: 当前状态
    """
    task_id: str
    name: str
    skill_path: str
    cron_expr: str
    enabled: bool = True
    priority: TaskPriority = TaskPriority.NORMAL
    timeout: int = 300  # 5分钟默认超时
    retry_policy: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "max_retries": 3,
        "backoff_multiplier": 2,
        "initial_delay": 1,
    })
    dependencies: List[str] = field(default_factory=list)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING

    def __post_init__(self):
        """初始化后处理"""
        if not self.task_id:
            self.task_id = f"{self.skill_path}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "skill_path": self.skill_path,
            "cron_expr": self.cron_expr,
            "enabled": self.enabled,
            "priority": self.priority.value,
            "timeout": self.timeout,
            "retry_policy": self.retry_policy,
            "dependencies": self.dependencies,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScheduledTask':
        """从字典创建"""
        # 处理 datetime 字段
        if data.get("last_run") and isinstance(data["last_run"], str):
            data["last_run"] = datetime.fromisoformat(data["last_run"])
        if data.get("next_run") and isinstance(data["next_run"], str):
            data["next_run"] = datetime.fromisoformat(data["next_run"])
        if data.get("status") and isinstance(data["status"], str):
            data["status"] = TaskStatus(data["status"])
        if data.get("priority") and isinstance(data["priority"], str):
            data["priority"] = TaskPriority(data["priority"])

        return cls(**data)

    def update_next_run(self, now: datetime):
        """更新下次执行时间"""
        self.next_run = self._calculate_next_run(now)

    def _calculate_next_run(self, now: datetime) -> Optional[datetime]:
        """计算下次执行时间"""
        try:
            from croniter import croniter
            cron = croniter(self.cron_expr, now)
            return cron.get_next(datetime)
        except ImportError:
            # 如果没有 croniter，使用简单实现
            return self._simple_cron_calc(now)
        except Exception:
            return None

    def _simple_cron_calc(self, now: datetime) -> Optional[datetime]:
        """简单 Cron 计算 (仅支持简单格式)"""
        import calendar

        parts = self.cron_expr.split()
        if len(parts) != 5:
            return None

        minute, hour, day, month, weekday = parts

        # 简单实现：每4小时
        if self.cron_expr == "0 */4 * * *":
            from datetime import timedelta
            return now + timedelta(hours=4)

        # 每天 8 点
        if self.cron_expr == "0 8 * * *":
            from datetime import timedelta
            next_run = now.replace(hour=8, minute=0, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run

        # 每小时
        if self.cron_expr == "0 * * * *":
            from datetime import timedelta
            return now + timedelta(hours=1)

        return None


@dataclass
class ExecutionRecord:
    """执行记录"""
    record_id: str
    task_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    output: Any = None
    error: Optional[str] = None
    retry_count: int = 0

    def to_dict(self) -> Dict:
        return {
            "record_id": self.record_id,
            "task_id": self.task_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "retry_count": self.retry_count,
        }


class TaskRegistry:
    """任务注册表"""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path
        self.tasks: Dict[str, ScheduledTask] = {}
        self._load()

    def register(self, task: ScheduledTask) -> None:
        """注册任务"""
        self.tasks[task.task_id] = task
        self._save()

    def unregister(self, task_id: str) -> bool:
        """注销任务"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save()
            return True
        return False

    def get(self, task_id: str) -> Optional[ScheduledTask]:
        """获取任务"""
        return self.tasks.get(task_id)

    def list_all(self) -> List[ScheduledTask]:
        """列出所有任务"""
        return list(self.tasks.values())

    def list_enabled(self) -> List[ScheduledTask]:
        """列出已启用任务"""
        return [t for t in self.tasks.values() if t.enabled]

    def list_by_status(self, status: TaskStatus) -> List[ScheduledTask]:
        """按状态筛选"""
        return [t for t in self.tasks.values() if t.status == status]

    def _load(self) -> None:
        """加载任务配置"""
        if self.storage_path and Path(self.storage_path).exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for task_data in data.get("tasks", []):
                        task = ScheduledTask.from_dict(task_data)
                        self.tasks[task.task_id] = task
            except Exception as e:
                print(f"[Warning] Failed to load tasks: {e}")

    def _save(self) -> None:
        """保存任务配置"""
        if not self.storage_path:
            return

        try:
            data = {
                "tasks": [task.to_dict() for task in self.tasks.values()]
            }
            Path(self.storage_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Error] Failed to save tasks: {e}")
