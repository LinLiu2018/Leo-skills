"""
Agent Definition & Multi-Agent Coordinator
==========================================
Agent 定义类和多代理协调器

参考 Claude Code 官方最佳实践:
- research-agent 多代理协作模式
- AgentDefinition 配置
- Task 工具动态委派
"""

import uuid
import time
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AgentStatus(Enum):
    """Agent 状态"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentDefinition:
    """
    子代理定义
    ==========
    参考官方 AgentDefinition 模式，每个子代理有:
    - name: 名称
    - description: 描述 (用于 LLM 理解何时调用)
    - tools: 允许的工具列表
    - model: 独立模型选择
    - prompt: 子代理提示词
    """
    name: str
    description: str  # 用于 LLM 理解何时调用此代理
    tools: List[str] = field(default_factory=list)  # 允许的工具列表
    model: str = "haiku"  # 独立模型选择
    prompt: str = ""  # 子代理提示词
    timeout: int = 120  # 超时时间(秒)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "tools": self.tools,
            "model": self.model,
            "prompt": self.prompt,
            "timeout": self.timeout
        }


@dataclass
class TaskDelegate:
    """任务委派记录"""
    task_id: str
    subagent_name: str
    task: str
    context: Dict[str, Any]
    status: AgentStatus = AgentStatus.IDLE
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_ms: float = 0.0


class MultiAgentCoordinator:
    """
    多代理协调器
    ============
    负责任务分解和委派给子代理

    参考官方 research-agent 模式:
    - Lead Agent 负责任务分解
    - 通过 Task 工具动态委派给子代理
    - 支持并行执行多个子代理
    """

    def __init__(self, agent_definitions: Optional[Dict[str, AgentDefinition]] = None):
        """
        初始化协调器

        Args:
            agent_definitions: 子代理定义字典
        """
        self.agent_definitions: Dict[str, AgentDefinition] = agent_definitions or {}
        self.delegated_tasks: Dict[str, TaskDelegate] = {}
        self.task_results: Dict[str, Any] = {}

        # 回调函数
        self.on_task_start: Optional[Callable] = None
        self.on_task_complete: Optional[Callable] = None
        self.on_task_error: Optional[Callable] = None

    def register_agent(self, definition: AgentDefinition) -> None:
        """注册子代理"""
        self.agent_definitions[definition.name] = definition

    def get_agent(self, name: str) -> Optional[AgentDefinition]:
        """获取子代理定义"""
        return self.agent_definitions.get(name)

    def list_agents(self) -> List[AgentDefinition]:
        """列出所有子代理"""
        return list(self.agent_definitions.values())

    def delegate_task(
        self,
        subagent_name: str,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> TaskDelegate:
        """
        委派任务给子代理

        Args:
            subagent_name: 子代理名称
            task: 任务描述
            context: 上下文参数

        Returns:
            TaskDelegate: 任务委派记录
        """
        task_id = f"task_{uuid.uuid4().hex[:8]}"

        # 获取子代理定义
        agent_def = self.get_agent(subagent_name)
        if not agent_def:
            raise ValueError(f"Unknown subagent: {subagent_name}")

        # 创建任务记录
        delegate = TaskDelegate(
            task_id=task_id,
            subagent_name=subagent_name,
            task=task,
            context=context or {},
            status=AgentStatus.RUNNING,
            start_time=datetime.now()
        )
        self.delegated_tasks[task_id] = delegate

        # 回调
        if self.on_task_start:
            self.on_task_start(delegate)

        return delegate

    def execute_delegated_task(
        self,
        task_id: str,
        executor: Callable[[str, str, Dict], Any]
    ) -> Any:
        """
        执行委派的任务

        Args:
            task_id: 任务 ID
            executor: 执行函数 (subagent_name, task, context) -> result

        Returns:
            执行结果
        """
        delegate = self.delegated_tasks.get(task_id)
        if not delegate:
            raise ValueError(f"Task not found: {task_id}")

        try:
            # 执行任务
            start = time.time()
            result = executor(
                delegate.subagent_name,
                delegate.task,
                delegate.context
            )
            duration_ms = (time.time() - start) * 1000

            # 更新任务状态
            delegate.result = result
            delegate.status = AgentStatus.COMPLETED
            delegate.end_time = datetime.now()
            delegate.duration_ms = duration_ms

            self.task_results[task_id] = result

            # 回调
            if self.on_task_complete:
                self.on_task_complete(delegate)

            return result

        except Exception as e:
            # 更新任务状态
            delegate.error = str(e)
            delegate.status = AgentStatus.FAILED
            delegate.end_time = datetime.now()

            # 回调
            if self.on_task_error:
                self.on_task_error(delegate, e)

            raise

    def spawn_parallel_agents(
        self,
        tasks: List[Dict[str, str]],
        executor: Callable[[str, str, Dict], Any]
    ) -> List[Any]:
        """
        并行执行多个子代理任务

        Args:
            tasks: 任务列表 [{"subagent": "xxx", "task": "xxx", "context": {}}]
            executor: 执行函数

        Returns:
            所有任务的结果列表
        """
        # 委派所有任务
        task_ids = []
        for t in tasks:
            delegate = self.delegate_task(
                subagent_name=t["subagent"],
                task=t["task"],
                context=t.get("context", {})
            )
            task_ids.append(delegate.task_id)

        # 并行执行 (简化实现，实际可用 ThreadPoolExecutor)
        results = []
        for task_id in task_ids:
            try:
                result = self.execute_delegated_task(task_id, executor)
                results.append(result)
            except Exception as e:
                results.append({"error": str(e)})

        return results

    def get_task_status(self, task_id: str) -> Optional[AgentStatus]:
        """获取任务状态"""
        delegate = self.delegated_tasks.get(task_id)
        return delegate.status if delegate else None

    def wait_for_task(self, task_id: str, timeout: int = 120) -> Any:
        """等待任务完成"""
        delegate = self.delegated_tasks.get(task_id)
        if not delegate:
            raise ValueError(f"Task not found: {task_id}")

        # 简化实现 - 实际应该用异步等待
        start_time = time.time()
        while delegate.status == AgentStatus.RUNNING:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Task timeout: {task_id}")
            time.sleep(0.1)

        if delegate.status == AgentStatus.FAILED:
            raise RuntimeError(f"Task failed: {delegate.error}")

        return delegate.result


# ==================== 便捷工厂函数 ====================

def create_research_agent() -> AgentDefinition:
    """创建研究代理定义"""
    return AgentDefinition(
        name="researcher",
        description="使用 web_search_skill 和 research_assistant_skill 收集信息，进行研究调研",
        tools=["web_search_skill", "research_assistant_skill"],
        model="haiku",
        prompt="你是一个专业的研究助手，负责收集和整理信息。"
    )


def create_analyst_agent() -> AgentDefinition:
    """创建分析代理定义"""
    return AgentDefinition(
        name="analyst",
        description="使用 data_analyzer_skill 进行数据分析和趋势预测",
        tools=["data_analyzer_skill"],
        model="haiku",
        prompt="你是一个专业的数据分析师，负责分析数据并生成洞察。"
    )


def create_creative_agent() -> AgentDefinition:
    """创建创意代理定义"""
    return AgentDefinition(
        name="creative",
        description="使用 content_layout_leo_skill 进行内容创作和文案生成",
        tools=["content_layout_leo_skill", "article_to_prototype_skill"],
        model="sonnet",
        prompt="你是一个创意内容专家，负责生成高质量的营销内容。"
    )


def create_default_coordinator() -> MultiAgentCoordinator:
    """创建默认的多代理协调器"""
    coordinator = MultiAgentCoordinator()
    coordinator.register_agent(create_research_agent())
    coordinator.register_agent(create_analyst_agent())
    coordinator.register_agent(create_creative_agent())
    return coordinator
