# -*- coding: utf-8 -*-
"""
统一调度中心核心模块

集中管理所有定时任务，支持：
- 技能任务自动发现与注册
- Cron 表达式解析与执行
- 失败重试机制
- 任务状态管理
- 依赖处理
"""

import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ...base import BaseSkill, SkillResult

from .task import ScheduledTask, TaskRegistry, TaskStatus, TaskResult, ExecutionRecord
from .executor import TaskExecutor
from .retry_policy import ExponentialBackoff


class UnifiedScheduler:
    """
    统一调度中心

    集中管理所有定时任务，提供：
    - 任务自动发现与注册
    - Cron 调度执行
    - 失败重试
    - 依赖管理
    - 状态持久化
    """

    def __init__(
        self,
        skills_base_path: str = "src/leo_skills",
        config_path: Optional[str] = None
    ):
        self.skills_base_path = Path(skills_base_path)
        self.config_path = config_path or ".leo_scheduler/tasks.json"

        # 任务注册表
        self.registry = TaskRegistry(self.config_path)

        # 任务执行器
        self.executor = TaskExecutor(str(self.skills_base_path))

        # 执行记录
        self.execution_records: List[ExecutionRecord] = []

        # 调度线程
        self._scheduler_thread: Optional[threading.Thread] = None
        self._running = False
        self._check_interval = 60  # 每60秒检查一次

        # 回调函数
        self._on_task_start: Optional[Callable] = None
        self._on_task_complete: Optional[Callable] = None
        self._on_task_error: Optional[Callable] = None

        # 自动发现的技能
        self._discovered_skills: Dict[str, Dict] = {}

    def get_actions(self) -> List[str]:
        """获取可用动作"""
        return [
            "discover",           # 自动发现技能
            "register",           # 手动注册任务
            "list",               # 列出所有任务
            "run",                # 手动执行任务
            "enable",             # 启用任务
            "disable",            # 禁用任务
            "remove",             # 删除任务
            "start",              # 启动调度器
            "stop",               # 停止调度器
            "status",             # 获取调度器状态
            "history",           # 获取执行历史
            "clear_history",     # 清理历史
            "get_dashboard",     # 获取仪表板数据
        ]

    def execute(
        self,
        action: str = "list",
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> SkillResult:
        """
        执行调度器动作

        Args:
            action: 动作名称
            context: 上下文参数
            **kwargs: 额外参数

        Returns:
            SkillResult
        """
        params = self._merge_params(action, context, kwargs)

        try:
            if action == "discover":
                data = self.discover_skills()
            elif action == "register":
                data = self.register_task(**params)
            elif action == "list":
                data = self.list_tasks(**params)
            elif action == "run":
                data = self.run_task(**params)
            elif action == "enable":
                data = self.enable_task(**params)
            elif action == "disable":
                data = self.disable_task(**params)
            elif action == "remove":
                data = self.remove_task(**params)
            elif action == "start":
                data = self.start()
            elif action == "stop":
                data = self.stop()
            elif action == "status":
                data = self.get_status()
            elif action == "history":
                data = self.get_history(**params)
            elif action == "clear_history":
                data = self.clear_history(**params)
            elif action == "get_dashboard":
                data = self.get_dashboard()
            else:
                return SkillResult.fail(f"Unknown action: {action}")

            return SkillResult.ok(data=data)

        except Exception as e:
            return SkillResult.fail(str(e))

    def _merge_params(
        self,
        action: str,
        context: Optional[Dict],
        kwargs: Dict
    ) -> Dict:
        """合并参数"""
        params = {}

        if isinstance(context, dict):
            params.update(context.get("params", {}))
            params.update(context)

        params.update(kwargs)

        # 处理 action 参数
        if "action" not in params:
            params["action"] = action

        return params

    # ========== 技能发现 ==========

    def discover_skills(self) -> Dict[str, Any]:
        """
        自动发现支持定时调度的技能

        扫描 skills_base_path 下所有技能，
        识别具有 default_schedule 属性的技能并注册

        Returns:
            发现的技能列表
        """
        discovered = []
        skills_path = self.skills_base_path

        if not skills_path.exists():
            return {
                "status": "error",
                "message": f"Skills path not found: {skills_path}",
                "discovered": []
            }

        # 递归扫描所有目录
        for category_dir in skills_path.iterdir():
            if not category_dir.is_dir():
                continue

            for skill_dir in category_dir.iterdir():
                if not skill_dir.is_dir():
                    continue

                skill_info = self._parse_skill(skill_dir, category_dir.name)
                if skill_info:
                    discovered.append(skill_info)
                    self._discovered_skills[skill_info["skill_path"]] = skill_info

        # 统计
        existing_tasks = set(t.task_id for t in self.registry.list_all())
        new_skills = [
            s for s in discovered
            if s["skill_path"] not in existing_tasks
        ]

        return {
            "status": "success",
            "discovered": discovered,
            "new_skills": new_skills,
            "total": len(discovered),
            "existing": len(existing_tasks)
        }

    def _parse_skill(self, skill_dir: Path, category: str) -> Optional[Dict]:
        """解析技能信息"""
        # 查找 Python 文件
        py_files = list(skill_dir.glob("*.py"))

        for py_file in py_files:
            if py_file.name.startswith("_"):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")

                # 检查是否有 default_schedule
                if "default_schedule" in content:
                    # 提取 schedule 值
                    import re
                    match = re.search(r'default_schedule\s*=\s*["\']([^"\']+)["\']', content)

                    if match:
                        schedule = match.group(1)
                        skill_name = skill_dir.name

                        return {
                            "skill_path": f"{category}/{skill_name}",
                            "skill_name": skill_name,
                            "category": category,
                            "default_schedule": schedule,
                            "module_file": str(py_file)
                        }

            except Exception as e:
                print(f"[Warning] Failed to parse {py_file}: {e}")

        return None

    # ========== 任务管理 ==========

    def register_task(
        self,
        skill_path: str,
        name: Optional[str] = None,
        cron_expr: Optional[str] = None,
        enabled: bool = True,
        priority: str = "normal",
        timeout: int = 300,
        retry_policy: Optional[Dict] = None,
        dependencies: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        注册定时任务

        Args:
            skill_path: 技能路径 (category/skill_name)
            name: 任务名称
            cron_expr: Cron 表达式
            enabled: 是否启用
            priority: 优先级
            timeout: 超时时间(秒)
            retry_policy: 重试策略
            dependencies: 依赖任务ID

        Returns:
            注册结果
        """
        # 如果未指定 schedule，尝试从技能获取
        if not cron_expr:
            skill_info = self._discovered_skills.get(skill_path)
            if skill_info:
                cron_expr = skill_info.get("default_schedule")
            else:
                return {
                    "status": "error",
                    "message": "No cron_expr provided and skill not discovered"
                }

        # 生成任务ID
        task_id = f"task_{skill_path.replace('/', '_')}"

        # 创建任务
        task = ScheduledTask(
            task_id=task_id,
            name=name or f"Schedule: {skill_path}",
            skill_path=skill_path,
            cron_expr=cron_expr,
            enabled=enabled,
            timeout=timeout,
            retry_policy=retry_policy or {
                "enabled": True,
                "max_retries": 3,
                "backoff_multiplier": 2,
                "initial_delay": 1,
            },
            dependencies=dependencies or []
        )

        # 计算下次执行时间
        task.update_next_run(datetime.now())

        # 注册
        self.registry.register(task)

        return {
            "status": "success",
            "task_id": task_id,
            "message": f"Task registered: {task.name}",
            "next_run": task.next_run.isoformat() if task.next_run else None
        }

    def register_discovered(self) -> Dict[str, Any]:
        """注册所有发现的技能"""
        result = self.discover_skills()
        new_skills = result.get("new_skills", [])

        registered = []
        for skill in new_skills:
            reg_result = self.register_task(
                skill_path=skill["skill_path"],
                cron_expr=skill["default_schedule"]
            )
            if reg_result.get("status") == "success":
                registered.append(skill["skill_path"])

        return {
            "status": "success",
            "registered": registered,
            "count": len(registered)
        }

    def list_tasks(
        self,
        status: Optional[str] = None,
        enabled: Optional[bool] = None
    ) -> Dict[str, Any]:
        """列出任务"""
        tasks = self.registry.list_all()

        # 筛选
        if status:
            tasks = [t for t in tasks if t.status.value == status]
        if enabled is not None:
            tasks = [t for t in tasks if t.enabled == enabled]

        return {
            "status": "success",
            "tasks": [t.to_dict() for t in tasks],
            "count": len(tasks)
        }

    def enable_task(self, task_id: str) -> Dict[str, Any]:
        """启用任务"""
        task = self.registry.get(task_id)
        if not task:
            return {"status": "error", "message": f"Task not found: {task_id}"}

        task.enabled = True
        task.update_next_run(datetime.now())
        self.registry.register(task)

        return {
            "status": "success",
            "task_id": task_id,
            "message": f"Task enabled: {task.name}"
        }

    def disable_task(self, task_id: str) -> Dict[str, Any]:
        """禁用任务"""
        task = self.registry.get(task_id)
        if not task:
            return {"status": "error", "message": f"Task not found: {task_id}"}

        task.enabled = False
        self.registry.register(task)

        return {
            "status": "success",
            "task_id": task_id,
            "message": f"Task disabled: {task.name}"
        }

    def remove_task(self, task_id: str) -> Dict[str, Any]:
        """删除任务"""
        success = self.registry.unregister(task_id)

        return {
            "status": "success" if success else "error",
            "task_id": task_id,
            "message": f"Task removed: {task_id}" if success else "Task not found"
        }

    # ========== 任务执行 ==========

    def run_task(self, task_id: str) -> Dict[str, Any]:
        """手动执行任务"""
        task = self.registry.get(task_id)
        if not task:
            return {"status": "error", "message": f"Task not found: {task_id}"}

        # 执行
        result = self.executor.execute(task)

        # 记录
        self._record_execution(task, result)

        return {
            "status": "success",
            "task_id": task_id,
            "result": result.to_dict()
        }

    def _record_execution(self, task: ScheduledTask, result: TaskResult):
        """记录执行结果"""
        record = ExecutionRecord(
            record_id=f"{task.task_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            task_id=task.task_id,
            start_time=result.start_time,
            end_time=result.end_time or datetime.now(),
            status=result.status,
            output=result.output,
            error=result.error,
            retry_count=result.retry_count
        )
        self.execution_records.append(record)

    # ========== 调度器控制 ==========

    def start(self) -> Dict[str, Any]:
        """启动调度器"""
        if self._running:
            return {"status": "warning", "message": "Scheduler already running"}

        self._running = True
        self._scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            daemon=True
        )
        self._scheduler_thread.start()

        return {
            "status": "success",
            "message": "Scheduler started",
            "check_interval": self._check_interval
        }

    def stop(self) -> Dict[str, Any]:
        """停止调度器"""
        if not self._running:
            return {"status": "warning", "message": "Scheduler not running"}

        self._running = False
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5)

        return {"status": "success", "message": "Scheduler stopped"}

    def _scheduler_loop(self):
        """调度循环"""
        while self._running:
            try:
                self._check_and_execute()
            except Exception as e:
                print(f"[Scheduler] Error in scheduler loop: {e}")

            time.sleep(self._check_interval)

    def _check_and_execute(self):
        """检查并执行到期任务"""
        now = datetime.now()

        for task in self.registry.list_enabled():
            if task.next_run and task.next_run <= now:
                # 执行任务
                print(f"[Scheduler] Executing task: {task.name}")

                # 回调
                if self._on_task_start:
                    self._on_task_start(task)

                try:
                    result = self.executor.execute(task)

                    # 回调
                    if self._on_task_complete:
                        self._on_task_complete(task, result)

                except Exception as e:
                    print(f"[Scheduler] Task failed: {task.name}, error: {e}")

                    if self._on_task_error:
                        self._on_task_error(task, e)

                # 更新下次执行时间
                task.update_next_run(now)
                self.registry.register(task)

    # ========== 状态和历史 ==========

    def get_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        tasks = self.registry.list_all()

        return {
            "status": "success",
            "running": self._running,
            "tasks": {
                "total": len(tasks),
                "enabled": len([t for t in tasks if t.enabled]),
                "disabled": len([t for t in tasks if not t.enabled]),
                "running": len([t for t in tasks if t.status == TaskStatus.RUNNING]),
                "success": len([t for t in tasks if t.status == TaskStatus.SUCCESS]),
                "failed": len([t for t in tasks if t.status == TaskStatus.FAILED]),
            },
            "check_interval": self._check_interval,
            "execution_records": len(self.execution_records)
        }

    def get_history(
        self,
        task_id: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """获取执行历史"""
        records = self.execution_records

        if task_id:
            records = [r for r in records if r.task_id == task_id]

        # 返回最近记录
        records = records[-limit:]

        return {
            "status": "success",
            "records": [r.to_dict() for r in records],
            "count": len(records)
        }

    def clear_history(self, before: Optional[str] = None) -> Dict[str, Any]:
        """清理执行历史"""
        count = len(self.execution_records)

        if before:
            before_dt = datetime.fromisoformat(before)
            self.execution_records = [
                r for r in self.execution_records
                if r.start_time >= before_dt
            ]
            count -= len(self.execution_records)
        else:
            self.execution_records.clear()

        return {
            "status": "success",
            "cleared": count
        }

    # ========== 仪表板 ==========

    def get_dashboard(self) -> Dict[str, Any]:
        """获取仪表板数据"""
        status = self.get_status()
        tasks = self.registry.list_all()

        # 按状态分组
        by_status = {}
        for task in tasks:
            s = task.status.value
            if s not in by_status:
                by_status[s] = []
            by_status[s].append(task.to_dict())

        # 即将执行的任务
        now = datetime.now()
        upcoming = [
            t.to_dict() for t in tasks
            if t.enabled and t.next_run and t.next_run > now
        ]
        upcoming.sort(key=lambda x: x.get("next_run", ""))
        upcoming = upcoming[:5]

        return {
            "status": "success",
            "scheduler": status,
            "by_status": by_status,
            "upcoming": upcoming,
            "discovered_skills": len(self._discovered_skills)
        }

    # ========== 回调设置 ==========

    def on_task_start(self, callback: Callable):
        """设置任务开始回调"""
        self._on_task_start = callback

    def on_task_complete(self, callback: Callable):
        """设置任务完成回调"""
        self._on_task_complete = callback

    def on_task_error(self, callback: Callable):
        """设置任务错误回调"""
        self._on_task_error = callback
