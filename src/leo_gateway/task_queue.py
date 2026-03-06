# -*- coding: utf-8 -*-
"""
异步任务队列 (Task Queue)

用于 MCP Agent 委托的异步执行。
支持任务提交、状态查询、结果获取。
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, Callable, List

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """任务状态"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """任务数据模型"""
    id: str
    agent_name: str
    task_description: str
    context: Dict[str, Any]
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


@dataclass
class TaskResult:
    """任务执行结果"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


class TaskQueue:
    """
    异步任务队列

    管理 Agent 委托任务的异步执行。
    """

    def __init__(self, max_workers: int = 3, max_queue_size: int = 100):
        """
        初始化任务队列

        Args:
            max_workers: 最大工作线程数
            max_queue_size: 最大队列长度
        """
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        self.tasks: Dict[str, Task] = {}
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self.workers: List[asyncio.Task] = []
        self._running = False
        self._agent_executor: Optional[Callable] = None

    def set_agent_executor(self, executor: Callable):
        """
        设置 Agent 执行器

        Args:
            executor: 异步执行函数，接收 (agent_name, task_description, context) 参数
        """
        self._agent_executor = executor

    async def start(self):
        """启动任务队列"""
        if self._running:
            return

        self._running = True
        for i in range(self.max_workers):
            worker = asyncio.create_task(
                self._worker_loop(),
                name=f"TaskWorker-{i}"
            )
            self.workers.append(worker)

        logger.info(f"TaskQueue started with {self.max_workers} workers")

    async def stop(self):
        """停止任务队列"""
        self._running = False

        # 取消所有工作线程
        for worker in self.workers:
            worker.cancel()

        # 等待所有工作线程完成
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()

        logger.info("TaskQueue stopped")

    async def submit(
        self,
        agent_name: str,
        task_description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        提交任务

        Args:
            agent_name: Agent 名称
            task_description: 任务描述
            context: 上下文信息

        Returns:
            任务ID
        """
        task_id = str(uuid.uuid4())

        task = Task(
            id=task_id,
            agent_name=agent_name,
            task_description=task_description,
            context=context or {},
            status=TaskStatus.QUEUED,
            created_at=datetime.now()
        )

        self.tasks[task_id] = task

        try:
            await asyncio.wait_for(
                self.queue.put(task_id),
                timeout=5.0
            )
            logger.info(f"Task {task_id} queued for agent {agent_name}")
        except asyncio.TimeoutError:
            logger.error(f"Task queue is full, task {task_id} rejected")
            task.status = TaskStatus.FAILED
            task.error = "Queue is full"
            raise Exception("Task queue is full")

        return task_id

    async def _worker_loop(self):
        """工作线程循环"""
        while self._running:
            try:
                # 获取任务，带超时以便检查运行状态
                task_id = await asyncio.wait_for(
                    self.queue.get(),
                    timeout=1.0
                )
            except asyncio.TimeoutError:
                continue

            task = self.tasks.get(task_id)
            if not task:
                self.queue.task_done()
                continue

            # 更新任务状态
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()

            try:
                # 执行任务
                result = await self._execute_task(task)

                task.status = TaskStatus.COMPLETED
                task.result = result
                task.execution_time_ms = (
                    datetime.now() - task.started_at
                ).total_seconds() * 1000

                logger.info(f"Task {task_id} completed in {task.execution_time_ms:.0f}ms")

            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                logger.error(f"Task {task_id} failed: {e}")

            finally:
                task.completed_at = datetime.now()
                self.queue.task_done()

    async def _execute_task(self, task: Task) -> Any:
        """
        执行具体任务

        Args:
            task: 任务对象

        Returns:
            执行结果
        """
        if self._agent_executor:
            # 使用外部执行器
            return await self._agent_executor(
                task.agent_name,
                task.task_description,
                task.context
            )

        # 默认执行逻辑：导入并调用 Agent
        try:
            # 尝试从注册表获取 Agent
            from leo_orchestrator.registry import get_registry
            registry = get_registry()
            agent = registry.get_agent(task.agent_name)

            if not agent:
                raise ValueError(f"Agent {task.agent_name} not found")

            # 构建执行上下文
            execution_context = {
                "agent_name": task.agent_name,
                "task": task.task_description,
                "context": task.context,
                "started_at": datetime.now().isoformat(),
            }

            # TODO: 实现具体的 Agent 调用逻辑
            # 这里可以集成实际的 Agent 执行框架

            return {
                "status": "completed",
                "agent": task.agent_name,
                "task": task.task_description,
                "context": execution_context,
                "note": "Agent execution simulated - integrate with actual agent framework"
            }

        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            raise

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态字典
        """
        task = self.tasks.get(task_id)
        if not task:
            return None

        return {
            "id": task.id,
            "status": task.status.value,
            "agent": task.agent_name,
            "description": task.task_description,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "execution_time_ms": task.execution_time_ms,
            "result": task.result,
            "error": task.error,
        }

    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """
        获取任务结果

        Args:
            task_id: 任务ID

        Returns:
            任务结果
        """
        task = self.tasks.get(task_id)
        if not task:
            return None

        if task.status == TaskStatus.COMPLETED:
            return TaskResult(
                success=True,
                data=task.result,
                execution_time_ms=task.execution_time_ms
            )
        elif task.status == TaskStatus.FAILED:
            return TaskResult(
                success=False,
                error=task.error
            )
        else:
            return None  # 任务尚未完成

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        agent_name: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        列出任务

        Args:
            status: 按状态过滤
            agent_name: 按 Agent 过滤
            limit: 返回数量限制

        Returns:
            任务列表
        """
        tasks = list(self.tasks.values())

        if status:
            tasks = [t for t in tasks if t.status == status]
        if agent_name:
            tasks = [t for t in tasks if t.agent_name == agent_name]

        # 按创建时间倒序
        tasks.sort(key=lambda t: t.created_at, reverse=True)

        return [self.get_task_status(t.id) for t in tasks[:limit]]

    def cleanup_old_tasks(self, max_age_hours: int = 24) -> int:
        """
        清理过期任务

        Args:
            max_age_hours: 最大保留时间(小时)

        Returns:
            清理数量
        """
        cutoff = datetime.now() - __import__('datetime').timedelta(hours=max_age_hours)

        to_remove = [
            task_id for task_id, task in self.tasks.items()
            if task.created_at < cutoff and task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED)
        ]

        for task_id in to_remove:
            del self.tasks[task_id]

        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old tasks")

        return len(to_remove)

    def get_stats(self) -> Dict[str, Any]:
        """获取队列统计信息"""
        status_counts = {}
        for task in self.tasks.values():
            status_counts[task.status.value] = status_counts.get(task.status.value, 0) + 1

        return {
            "total_tasks": len(self.tasks),
            "queue_size": self.queue.qsize(),
            "max_workers": self.max_workers,
            "running": self._running,
            "status_breakdown": status_counts,
        }


# 全局任务队列实例
_task_queue: Optional[TaskQueue] = None


def get_task_queue(max_workers: int = 3) -> TaskQueue:
    """获取全局任务队列实例"""
    global _task_queue
    if _task_queue is None:
        _task_queue = TaskQueue(max_workers=max_workers)
    return _task_queue


async def submit_agent_task(
    agent_name: str,
    task_description: str,
    context: Optional[Dict[str, Any]] = None
) -> str:
    """便捷函数：提交 Agent 任务"""
    queue = get_task_queue()
    if not queue._running:
        await queue.start()
    return await queue.submit(agent_name, task_description, context)


if __name__ == "__main__":
    # 测试
    async def test():
        queue = TaskQueue(max_workers=2)
        await queue.start()

        # 提交测试任务
        task_id = await queue.submit(
            "test_agent",
            "这是一个测试任务",
            {"param1": "value1"}
        )

        print(f"Task submitted: {task_id}")

        # 等待任务完成
        await asyncio.sleep(2)

        # 查询状态
        status = queue.get_task_status(task_id)
        print(f"Task status: {status}")

        await queue.stop()

    asyncio.run(test())
