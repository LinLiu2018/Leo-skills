# -*- coding: utf-8 -*-
"""
任务执行器模块

负责执行调度任务，支持同步/异步执行
"""

import asyncio
import importlib.util
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from .task import ScheduledTask, TaskResult, TaskStatus
from .retry_policy import RetryExecutor, RetryPolicy, ExponentialBackoff


class TaskExecutor:
    """
    任务执行器

    负责：
    - 加载和执行技能
    - 处理执行结果
    - 管理超时
    - 重试机制
    """

    def __init__(self, skills_base_path: str = "src/leo_skills"):
        self.skills_base_path = Path(skills_base_path)
        self.execution_history: Dict[str, TaskResult] = {}

    def execute(self, task: ScheduledTask) -> TaskResult:
        """
        同步执行任务

        Args:
            task: 定时任务

        Returns:
            任务执行结果
        """
        start_time = datetime.now()
        task.status = TaskStatus.RUNNING

        # 检查依赖
        if not self._check_dependencies(task):
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.SKIPPED,
                start_time=start_time,
                end_time=datetime.now(),
                error="Dependencies not satisfied"
            )

        # 构建重试策略
        retry_policy = RetryPolicy(
            enabled=task.retry_policy.get("enabled", True),
            max_retries=task.retry_policy.get("max_retries", 3),
            backoff_multiplier=task.retry_policy.get("backoff_multiplier", 2),
            initial_delay=task.retry_policy.get("initial_delay", 1),
        )

        retry_executor = RetryExecutor(ExponentialBackoff())

        try:
            # 执行任务
            if retry_policy.enabled:
                output = retry_executor.execute(
                    self._execute_skill,
                    task
                )
            else:
                output = self._execute_skill(task)

            end_time = datetime.now()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            result = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.SUCCESS,
                start_time=start_time,
                end_time=end_time,
                output=output,
                duration_ms=duration_ms
            )

            task.status = TaskStatus.SUCCESS
            task.last_run = start_time

        except Exception as e:
            end_time = datetime.now()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            result = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                start_time=start_time,
                end_time=end_time,
                error=str(e),
                duration_ms=duration_ms
            )

            task.status = TaskStatus.FAILED
            task.last_run = start_time

        # 保存历史
        self.execution_history[task.task_id] = result

        return result

    async def execute_async(self, task: ScheduledTask) -> TaskResult:
        """
        异步执行任务

        Args:
            task: 定时任务

        Returns:
            任务执行结果
        """
        start_time = datetime.now()
        task.status = TaskStatus.RUNNING

        try:
            # 异步执行
            output = await asyncio.wait_for(
                self._execute_skill_async(task),
                timeout=task.timeout
            )

            end_time = datetime.now()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            result = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.SUCCESS,
                start_time=start_time,
                end_time=end_time,
                output=output,
                duration_ms=duration_ms
            )

            task.status = TaskStatus.SUCCESS
            task.last_run = start_time

        except asyncio.TimeoutError:
            end_time = datetime.now()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            result = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                start_time=start_time,
                end_time=end_time,
                error=f"Task timeout after {task.timeout}s",
                duration_ms=duration_ms
            )

            task.status = TaskStatus.FAILED

        except Exception as e:
            end_time = datetime.now()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            result = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                start_time=start_time,
                end_time=end_time,
                error=str(e),
                duration_ms=duration_ms
            )

            task.status = TaskStatus.FAILED

        self.execution_history[task.task_id] = result
        return result

    def _execute_skill(self, task: ScheduledTask) -> Any:
        """
        执行技能（同步）

        Args:
            task: 定时任务

        Returns:
            技能执行结果
        """
        skill_path = self.skills_base_path / task.skill_path

        # 动态加载技能模块
        skill_module = self._load_skill_module(skill_path)

        # 获取执行函数
        if hasattr(skill_module, 'execute'):
            execute_func = skill_module.execute
        elif hasattr(skill_module, 'run'):
            execute_func = skill_module.run
        else:
            raise AttributeError(f"Skill {task.skill_path} has no execute or run function")

        # 执行技能
        result = execute_func(action="run")

        return result

    async def _execute_skill_async(self, task: ScheduledTask) -> Any:
        """
        执行技能（异步）

        Args:
            task: 定时任务

        Returns:
            技能执行结果
        """
        # 尝试导入异步版本
        skill_path = self.skills_base_path / task.skill_path
        skill_module = self._load_skill_module(skill_path)

        if hasattr(skill_module, 'execute_async'):
            execute_func = skill_module.execute_async
            return await execute_func(action="run")
        elif hasattr(skill_module, 'execute'):
            # 同步版本，在线程池中运行
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                skill_module.execute,
                {"action": "run"}
            )
        else:
            raise AttributeError(f"Skill {task.skill_path} has no execute function")

    def _load_skill_module(self, skill_path: Path):
        """动态加载技能模块"""
        # 尝试多个可能的入口文件
        possible_files = [
            skill_path / "main.py",
            skill_path / f"{skill_path.name}.py",
            skill_path / "__init__.py",
        ]

        for file_path in possible_files:
            if file_path.exists():
                spec = importlib.util.spec_from_file_location(
                    f"leo_skills.{task.skill_path}",
                    file_path
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    return module

        raise FileNotFoundError(f"Skill module not found: {skill_path}")

    def _check_dependencies(self, task: ScheduledTask) -> bool:
        """
        检查任务依赖

        Args:
            task: 定时任务

        Returns:
            依赖是否满足
        """
        if not task.dependencies:
            return True

        for dep_id in task.dependencies:
            dep_result = self.execution_history.get(dep_id)
            if not dep_result or dep_result.status != TaskStatus.SUCCESS:
                return False

        return True

    def get_history(self, task_id: Optional[str] = None) -> Dict[str, TaskResult]:
        """
        获取执行历史

        Args:
            task_id: 可选的任务ID

        Returns:
            执行历史字典
        """
        if task_id:
            return {task_id: self.execution_history.get(task_id)}
        return self.execution_history

    def clear_history(self, before: Optional[datetime] = None) -> int:
        """
        清理执行历史

        Args:
            before: 清理此时间之前的记录

        Returns:
            清理的记录数
        """
        if not before:
            count = len(self.execution_history)
            self.execution_history.clear()
            return count

        count = 0
        to_remove = []
        for task_id, result in self.execution_history.items():
            if result.end_time and result.end_time < before:
                to_remove.append(task_id)

        for task_id in to_remove:
            del self.execution_history[task_id]
            count += 1

        return count
