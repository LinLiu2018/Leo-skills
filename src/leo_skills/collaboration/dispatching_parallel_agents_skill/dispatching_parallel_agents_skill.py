# -*- coding: utf-8 -*-
"""
dispatching_parallel_agents_skill - 分发并行代理协作技能

当面对 2+ 个可以无需共享状态或顺序依赖地处理独立任务时使用。
核心理念：每个问题域分发一个代理。让它们并发工作。
基于 obra/superpowers 的 dispatching-parallel-agents 技能。
"""

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import concurrent.futures
import threading


class AgentStatus(Enum):
    """代理状态"""
    PENDING = "pending"         # 等待执行
    RUNNING = "running"         # 执行中
    COMPLETED = "completed"     # 已完成
    FAILED = "failed"           # 失败
    CANCELLED = "cancelled"     # 已取消


@dataclass
class AgentTask:
    """代理任务"""
    id: str
    name: str
    description: str
    scope: str
    constraints: List[str]
    expected_output: str
    status: AgentStatus = AgentStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


@dataclass
class DispatchResult:
    """分发结果"""
    status: str
    message: str
    tasks: List[AgentTask] = field(default_factory=list)
    completed_count: int = 0
    failed_count: int = 0
    summary: str = ""


class DispatchingParallelAgentsSkill:
    """
    分发并行代理技能 - 并行化独立任务处理

    功能：
    - 识别独立任务域
    - 创建专注的代理任务
    - 并行分发执行
    - 汇总和验证结果

    核心理念：每个问题域分发一个代理。让它们并发工作。
    """

    def __init__(self, max_workers: int = 5):
        self.name = "dispatching_parallel_agents_skill"
        self.version = "1.0.0"
        self.description = "分发并行代理协作技能"
        self.max_workers = max_workers
        self.active_tasks: Dict[str, AgentTask] = {}
        self._lock = threading.Lock()

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行技能主入口

        Args:
            action: 动作类型 (identify/create/dispatch/collect)
            failures: 失败列表
            domains: 独立域列表
            tasks: 任务定义列表
            task_ids: 任务ID列表
            timeout: 超时时间（秒）

        Returns:
            Dict 包含执行结果
        """
        action = kwargs.get("action", "identify")

        try:
            if action == "identify":
                result = self.identify_domains(
                    failures=kwargs.get("failures", [])
                )
            elif action == "create":
                result = self.create_tasks(
                    domains=kwargs.get("domains", [])
                )
            elif action == "dispatch":
                result = self.dispatch_tasks(
                    tasks=kwargs.get("tasks", []),
                    timeout=kwargs.get("timeout", 300)
                )
            elif action == "collect":
                result = self.collect_results(
                    task_ids=kwargs.get("task_ids", [])
                )
            elif action == "validate":
                result = self.validate_results(
                    results=kwargs.get("results", [])
                )
            else:
                return {
                    "status": "error",
                    "skill": self.name,
                    "error": f"Unknown action: {action}"
                }

            return {
                "status": "success" if result.status != "error" else "error",
                "skill": self.name,
                "action": action,
                "result": result
            }

        except Exception as e:
            return {
                "status": "error",
                "skill": self.name,
                "action": action,
                "error": str(e)
            }

    def identify_domains(
        self,
        failures: List[Dict[str, Any]]
    ) -> DispatchResult:
        """
        识别独立域

        按损坏内容分组失败，识别可以独立处理的域。

        Args:
            failures: 失败列表，每项包含 file, test, error 等信息

        Returns:
            DispatchResult 域识别结果
        """
        domains = {}

        for failure in failures:
            file_path = failure.get("file", "unknown")
            error_type = failure.get("error_type", "general")

            # 按文件分组
            if file_path not in domains:
                domains[file_path] = {
                    "name": Path(file_path).stem,
                    "file": file_path,
                    "failures": [],
                    "error_types": set()
                }

            domains[file_path]["failures"].append(failure)
            domains[file_path]["error_types"].add(error_type)

        # 转换为列表
        domain_list = [
            {
                "name": d["name"],
                "file": d["file"],
                "failure_count": len(d["failures"]),
                "error_types": list(d["error_types"]),
                "independent": len(d["error_types"]) == 1  # 单一错误类型通常更独立
            }
            for d in domains.values()
        ]

        # 建议哪些可以并行
        independent_domains = [d for d in domain_list if d["independent"]]

        return DispatchResult(
            status="success",
            message=f"识别了 {len(domain_list)} 个域，{len(independent_domains)} 个可以并行处理",
            summary=f"建议并行处理: {[d['name'] for d in independent_domains]}"
        )

    def create_tasks(
        self,
        domains: List[Dict[str, Any]]
    ) -> DispatchResult:
        """
        创建专注的代理任务

        每个代理获得：特定范围、清晰目标、约束、预期输出

        Args:
            domains: 域列表

        Returns:
            DispatchResult 任务创建结果
        """
        tasks = []

        for domain in domains:
            task = AgentTask(
                id=str(uuid.uuid4())[:8],
                name=f"修复 {domain['name']}",
                description=f"调查并修复 {domain['file']} 中的 {domain['failure_count']} 个失败",
                scope=domain['file'],
                constraints=[
                    f"专注于 {domain['file']}",
                    "不要更改其他文件",
                    "记录根因和修复方案"
                ],
                expected_output="根因分析、修复方案、更改摘要"
            )
            tasks.append(task)

            with self._lock:
                self.active_tasks[task.id] = task

        return DispatchResult(
            status="success",
            message=f"创建了 {len(tasks)} 个代理任务",
            tasks=tasks
        )

    def dispatch_tasks(
        self,
        tasks: List[Union[AgentTask, Dict[str, Any]]],
        timeout: int = 300
    ) -> DispatchResult:
        """
        并行分发任务

        Args:
            tasks: 任务列表
            timeout: 超时时间（秒）

        Returns:
            DispatchResult 分发执行结果
        """
        # 转换字典为 AgentTask 对象
        agent_tasks = []
        for task in tasks:
            if isinstance(task, dict):
                agent_task = AgentTask(
                    id=task.get("id", str(uuid.uuid4())[:8]),
                    name=task.get("name", "未命名任务"),
                    description=task.get("description", ""),
                    scope=task.get("scope", ""),
                    constraints=task.get("constraints", []),
                    expected_output=task.get("expected_output", "")
                )
            else:
                agent_task = task
            agent_tasks.append(agent_task)
            with self._lock:
                self.active_tasks[agent_task.id] = agent_task

        completed = 0
        failed = 0

        # 使用线程池并行执行
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_task = {
                executor.submit(self._execute_agent_task, task, timeout): task
                for task in agent_tasks
            }

            for future in concurrent.futures.as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    if result:
                        completed += 1
                    else:
                        failed += 1
                except Exception as e:
                    task.status = AgentStatus.FAILED
                    task.error = str(e)
                    failed += 1

        return DispatchResult(
            status="success",
            message=f"任务执行完成: {completed} 成功, {failed} 失败",
            tasks=agent_tasks,
            completed_count=completed,
            failed_count=failed
        )

    def _execute_agent_task(
        self,
        task: AgentTask,
        timeout: int
    ) -> bool:
        """
        执行单个代理任务（模拟）

        实际项目中，这里应该调用真实的子代理执行。

        Args:
            task: 代理任务
            timeout: 超时时间

        Returns:
            bool 是否成功
        """
        task.status = AgentStatus.RUNNING
        task.start_time = datetime.now()

        try:
            # 模拟代理执行任务
            # 实际项目中，这里应该：
            # 1. 调用 Task 工具创建子代理
            # 2. 传递任务上下文和约束
            # 3. 等待子代理完成
            # 4. 收集结果

            import time
            time.sleep(0.5)  # 模拟执行时间

            # 生成模拟结果
            task.result = f"""
任务 {task.name} 完成

范围: {task.scope}
发现:
- 识别了问题根因
- 应用了修复方案
- 验证了修复效果

更改摘要:
- 修改了相关代码
- 更新了测试用例
"""
            task.status = AgentStatus.COMPLETED
            task.end_time = datetime.now()
            return True

        except Exception as e:
            task.status = AgentStatus.FAILED
            task.error = str(e)
            task.end_time = datetime.now()
            return False

    def collect_results(
        self,
        task_ids: List[str]
    ) -> DispatchResult:
        """
        收集任务结果

        Args:
            task_ids: 任务ID列表

        Returns:
            DispatchResult 结果收集
        """
        tasks = []
        for task_id in task_ids:
            if task_id in self.active_tasks:
                tasks.append(self.active_tasks[task_id])

        # 生成汇总
        summary_lines = ["并行代理执行结果汇总", "=" * 40]
        for task in tasks:
            summary_lines.append(f"\n任务: {task.name}")
            summary_lines.append(f"状态: {task.status.value}")
            if task.result:
                summary_lines.append(f"结果: {task.result[:200]}...")
            if task.error:
                summary_lines.append(f"错误: {task.error}")

        return DispatchResult(
            status="success",
            message=f"收集了 {len(tasks)} 个任务的结果",
            tasks=tasks,
            summary="\n".join(summary_lines)
        )

    def validate_results(
        self,
        results: List[Dict[str, Any]]
    ) -> DispatchResult:
        """
        验证结果

        检查：
        1. 修复是否冲突
        2. 是否满足预期输出
        3. 是否需要进一步处理

        Args:
            results: 结果列表

        Returns:
            DispatchResult 验证结果
        """
        conflicts = []
        issues = []

        # 检查文件冲突
        files_modified = {}
        for result in results:
            file_path = result.get("file_modified", "")
            if file_path:
                if file_path in files_modified:
                    conflicts.append({
                        "file": file_path,
                        "agents": [files_modified[file_path], result.get("agent_id")]
                    })
                else:
                    files_modified[file_path] = result.get("agent_id")

        # 检查问题
        for result in results:
            if not result.get("has_fix"):
                issues.append({
                    "agent": result.get("agent_id"),
                    "issue": "未找到修复方案"
                })

        status = "success" if not conflicts and not issues else "warning"
        message = f"验证完成"
        if conflicts:
            message += f", 发现 {len(conflicts)} 个冲突"
        if issues:
            message += f", 发现 {len(issues)} 个问题"

        return DispatchResult(
            status=status,
            message=message,
            summary=f"冲突: {len(conflicts)}, 问题: {len(issues)}"
        )

    def get_task_status(self, task_id: str) -> Optional[AgentTask]:
        """获取任务状态"""
        return self.active_tasks.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            if task.status in [AgentStatus.PENDING, AgentStatus.RUNNING]:
                task.status = AgentStatus.CANCELLED
                return True
        return False

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "max_workers": self.max_workers,
            "features": [
                "identify_domains",
                "create_tasks",
                "dispatch_parallel",
                "collect_results",
                "validate_results"
            ]
        }


# 向后兼容
Dispatching_Parallel_Agents_Skill = DispatchingParallelAgentsSkill


def main():
    """入口函数 - 演示用法"""
    print("=" * 60)
    print("Dispatching Parallel Agents Skill - 演示")
    print("=" * 60)

    skill = DispatchingParallelAgentsSkill(max_workers=3)

    # 演示1: 识别域
    print("\n1. 识别独立域")
    print("-" * 40)
    failures = [
        {"file": "agent-tool-abort.test.ts", "error_type": "timeout", "test": "应该中止工具"},
        {"file": "agent-tool-abort.test.ts", "error_type": "timeout", "test": "应该处理混合完成"},
        {"file": "batch-completion.test.ts", "error_type": "assertion", "test": "批次完成行为"},
        {"file": "race-condition.test.ts", "error_type": "race", "test": "竞态条件"}
    ]
    result = skill.identify_domains(failures=failures)
    print(f"消息: {result.message}")
    print(f"建议: {result.summary}")

    # 演示2: 创建任务
    print("\n2. 创建代理任务")
    print("-" * 40)
    domains = [
        {"name": "agent-tool-abort", "file": "agent-tool-abort.test.ts", "failure_count": 2, "error_types": ["timeout"], "independent": True},
        {"name": "batch-completion", "file": "batch-completion.test.ts", "failure_count": 1, "error_types": ["assertion"], "independent": True},
        {"name": "race-condition", "file": "race-condition.test.ts", "failure_count": 1, "error_types": ["race"], "independent": True}
    ]
    result = skill.create_tasks(domains=domains)
    print(f"消息: {result.message}")
    print(f"任务数: {len(result.tasks)}")

    # 演示3: 分发任务
    print("\n3. 并行分发任务")
    print("-" * 40)
    result = skill.dispatch_tasks(tasks=result.tasks, timeout=60)
    print(f"消息: {result.message}")
    print(f"成功: {result.completed_count}, 失败: {result.failed_count}")

    # 演示4: 收集结果
    print("\n4. 收集结果")
    print("-" * 40)
    task_ids = [t.id for t in result.tasks]
    result = skill.collect_results(task_ids=task_ids)
    print(f"消息: {result.message}")
    print(f"汇总长度: {len(result.summary)} 字符")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return skill


if __name__ == "__main__":
    main()
