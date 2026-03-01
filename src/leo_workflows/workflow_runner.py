# -*- coding: utf-8 -*-
"""
工作流运行器
===========

统一管理和执行所有工作流，支持：
- 手动触发
- 定时执行
- 事件触发
- 执行历史记录
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..leo_orchestrator.workflow_engine import WorkflowEngine
from ..leo_memory import get_auto_memory


class WorkflowRunner:
    """
    工作流运行器

    所有工作流的统一入口
    """

    def __init__(self):
        self.memory = get_auto_memory()
        self.execution_history: List[Dict[str, Any]] = []
        self.definitions_dir = Path(__file__).parent / "definitions"

        # 工作流注册表
        self._workflows: Dict[str, Dict[str, Any]] = {}
        self._register_workflows()

    def _register_workflows(self):
        """注册所有工作流定义"""
        if not self.definitions_dir.exists():
            return

        for yaml_file in self.definitions_dir.glob("*.yaml"):
            workflow_id = yaml_file.stem
            self._workflows[workflow_id] = {
                "id": workflow_id,
                "path": str(yaml_file),
                "name": workflow_id.replace("_", " ").title(),
            }

    def list_workflows(self) -> List[Dict[str, str]]:
        """列出所有可用工作流"""
        return [
            {"id": k, "name": v["name"], "path": v["path"]}
            for k, v in self._workflows.items()
        ]

    def run(self, workflow_id: str, agents: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        运行指定工作流

        Args:
            workflow_id: 工作流ID（YAML文件名，不含扩展名）
            agents: Agent字典
            **kwargs: 工作流参数

        Returns:
            执行结果
        """
        # 记录执行开始
        run_id = self.memory.auto_record(
            event_type="workflow_start",
            content={"workflow_id": workflow_id, "params": kwargs},
            agent="workflow_runner",
            importance=3,
            tags=["workflow", workflow_id],
        )

        try:
            # 创建工作流引擎
            engine = WorkflowEngine(agents)

            # 查找工作流定义
            workflow_def = self._workflows.get(workflow_id)
            if not workflow_def:
                raise ValueError(f"工作流不存在: {workflow_id}")

            # 执行工作流
            result = engine.execute_from_yaml(workflow_def["path"], **kwargs)

            # 记录执行成功
            self.memory.auto_record(
                event_type="workflow_complete",
                content={
                    "run_id": run_id,
                    "workflow_id": workflow_id,
                    "success": result.get("success", False),
                },
                agent="workflow_runner",
                importance=3,
                tags=["workflow", "success", workflow_id],
            )

            # 保存执行历史
            self.execution_history.append({
                "run_id": run_id,
                "workflow_id": workflow_id,
                "timestamp": datetime.now().isoformat(),
                "result": result,
            })

            return result

        except Exception as e:
            # 记录执行失败
            self.memory.auto_record(
                event_type="workflow_error",
                content={"run_id": run_id, "workflow_id": workflow_id, "error": str(e)},
                agent="workflow_runner",
                importance=4,
                tags=["workflow", "error", workflow_id],
            )
            raise

    def run_scheduled(self, workflow_id: str, agents: Dict[str, Any], schedule: str, **kwargs) -> Dict[str, Any]:
        """
        定时运行工作流

        Args:
            workflow_id: 工作流ID
            agents: Agent字典
            schedule: 调度表达式（cron格式）
            **kwargs: 工作流参数

        Returns:
            执行结果
        """
        # TODO: 集成调度器
        self.memory.auto_record(
            event_type="scheduled_workflow",
            content={"workflow_id": workflow_id, "schedule": schedule},
            agent="workflow_runner",
            importance=3,
            tags=["scheduled", workflow_id],
        )

        return self.run(workflow_id, agents, **kwargs)

    def get_execution_history(self, workflow_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取执行历史

        Args:
            workflow_id: 可选的工作流ID过滤

        Returns:
            执行历史列表
        """
        if workflow_id:
            return [h for h in self.execution_history if h["workflow_id"] == workflow_id]
        return self.execution_history


# 全局运行器实例
_runner: Optional[WorkflowRunner] = None


def get_workflow_runner() -> WorkflowRunner:
    """获取工作流运行器实例"""
    global _runner
    if _runner is None:
        _runner = WorkflowRunner()
    return _runner


def run_workflow(workflow_id: str, agents: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    快速运行工作流

    Args:
        workflow_id: 工作流ID
        agents: Agent字典
        **kwargs: 工作流参数

    Returns:
        执行结果
    """
    runner = get_workflow_runner()
    return runner.run(workflow_id, agents, **kwargs)


def list_available_workflows() -> List[Dict[str, str]]:
    """列出所有可用工作流"""
    runner = get_workflow_runner()
    return runner.list_workflows()


__all__ = [
    "WorkflowRunner",
    "get_workflow_runner",
    "run_workflow",
    "list_available_workflows",
]
