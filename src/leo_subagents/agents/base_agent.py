"""
Subagent基类
============
所有Subagent的基础类
"""

import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

# 添加父目录到路径
parent_path = Path(__file__).parent.parent.parent
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))

if TYPE_CHECKING:
    pass

# 导入日志和错误处理
from leo_system.logger import get_logger
from leo_system.errors import AgentError, AgentDispatchError
from leo_system.metrics import track_time

# 创建日志记录器
logger = get_logger(__name__)


@dataclass
class AgentConfig:
    """Agent配置"""

    name: str
    type: str
    priority: int
    skills: List[str]
    description: str = ""
    enabled: bool = True
    max_retries: int = 3
    timeout: int = 300


class BaseAgent(ABC):
    """
    Subagent基类
    ============
    定义所有Agent必须实现的接口
    """

    def __init__(self, config: AgentConfig):
        """
        初始化Agent

        Args:
            config: Agent配置
        """
        from ..skills_bridge.skill_executor import get_executor
        from ..skills_bridge.skill_loader import get_loader

        self.config = config
        self.skill_loader = get_loader()
        self.skill_executor = get_executor()
        self.task_history: List[Dict[str, Any]] = []
        self.context_cache: Dict[str, str] = {}  # Modular Context 缓存

    @abstractmethod
    def can_handle(self, task: str) -> float:
        """
        判断是否能处理此任务

        Args:
            task: 任务描述

        Returns:
            置信度 (0.0 - 1.0)
        """

    @abstractmethod
    @track_time
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        执行任务

        Args:
            task: 任务描述
            **kwargs: 任务参数

        Returns:
            执行结果
        """

    def get_available_skills(self) -> List[str]:
        """
        获取可用的Skills

        Returns:
            Skill名称列表
        """
        return self.config.skills

    def has_skill(self, skill_name: str) -> bool:
        """
        检查是否有某个Skill

        Args:
            skill_name: Skill名称

        Returns:
            是否拥有此Skill
        """
        return skill_name in self.config.skills

    def use_skill(self, skill_name: str, action: str, **kwargs) -> Any:
        """
        调用Skill

        Args:
            skill_name: Skill名称
            action: 操作名称
            **kwargs: 参数

        Returns:
            Skill执行结果
        """
        if not self.has_skill(skill_name):
            logger.error(f"Agent '{self.config.name}' 没有 Skill '{skill_name}'")
            raise AgentDispatchError(self.config.name, skill_name, "Skill not available")

        result = self.skill_executor.execute(skill_name, action, **kwargs)

        return result

    def load_context(self, path: str) -> str:
        """
        加载知识上下文 (Modular Context)

        Args:
            path: 相对路径 (e.g., "templates/prd_template.md")

        Returns:
            文件内容
        """
        from pathlib import Path

        # 缓存检查
        if path in self.context_cache:
            return self.context_cache[path]

        # 路径解析 (Project Root)
        # base_agent.py 在 leo_subagents/agents/base_agent.py
        # root 在 ../../../
        root_path = Path(__file__).parent.parent.parent
        knowledge_path = root_path / "leo_knowledge" / path

        if not knowledge_path.exists():
            logger.warning(f"Context file not found: {knowledge_path}")
            return ""

        try:
            with open(knowledge_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.context_cache[path] = content
                return content
        except Exception as e:
            logger.error(f"Error loading context {path}: {e}")
            return ""

    def plan_execution(self, task: str, **kwargs) -> List[Dict[str, Any]]:
        """
        规划任务执行步骤

        Args:
            task: 任务描述
            **kwargs: 任务参数

        Returns:
            执行步骤列表
        """
        # 默认实现：简单规划
        # 子类可以重写此方法以实现更复杂的规划

        # 尝试将任务映射到合适的Skill
        steps = []

        for skill_name in self.config.skills:
            # 这里应该有更智能的匹配逻辑
            # 简化实现：每个Skill一个步骤
            steps.append(
                {"step": len(steps) + 1, "skill": skill_name, "action": "execute", "params": kwargs}
            )

        return steps

    def log_task(self, task: str, result: Dict[str, Any]):
        """
        记录任务执行历史

        Args:
            task: 任务描述
            result: 执行结果
        """
        self.task_history.append(
            {"timestamp": datetime.now().isoformat(), "task": task, "result": result}
        )

    def get_status(self) -> Dict[str, Any]:
        """
        获取Agent状态

        Returns:
            状态信息字典
        """
        return {
            "name": self.config.name,
            "type": self.config.type,
            "enabled": self.config.enabled,
            "priority": self.config.priority,
            "skills": self.config.skills,
            "tasks_completed": len(self.task_history),
        }

    def __repr__(self):
        return (
            f"Agent({self.config.name}, type={self.config.type}, skills={len(self.config.skills)})"
        )


# ==================== Agent工厂 ====================


class AgentFactory:
    """
    Agent工厂
    =========
    负责创建和管理Agent实例
    """

    _agents: Dict[str, BaseAgent] = {}
    _agent_classes: Dict[str, type] = {}

    @classmethod
    def register_agent_class(cls, agent_type: str, agent_class: type):
        """
        注册Agent类

        Args:
            agent_type: Agent类型
            agent_class: Agent类
        """
        cls._agent_classes[agent_type] = agent_class

    @classmethod
    def create_agent(cls, config: AgentConfig) -> BaseAgent:
        """
        创建Agent实例

        Args:
            config: Agent配置

        Returns:
            Agent实例
        """
        agent_class = cls._agent_classes.get(config.type)

        if not agent_class:
            logger.error(f"未知的Agent类型: {config.type}")
            raise AgentError(f"Unknown agent type: {config.type}")

        agent = agent_class(config)
        cls._agents[config.name] = agent

        return agent

    @classmethod
    def get_agent(cls, name: str) -> Optional[BaseAgent]:
        """
        获取Agent实例

        Args:
            name: Agent名称

        Returns:
            Agent实例或None
        """
        return cls._agents.get(name)

    @classmethod
    def list_agents(cls) -> List[str]:
        """
        列出所有已创建的Agent

        Returns:
            Agent名称列表
        """
        return list(cls._agents.keys())


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 示例：创建一个简单的Agent类
    class SimpleAgent(BaseAgent):
        def can_handle(self, task: str) -> float:
            return 0.8

        def execute(self, task: str, **kwargs) -> Dict[str, Any]:
            result = {"task": task, "status": "completed", "message": f"任务 '{task}' 已完成"}
            self.log_task(task, result)
            return result

    # 创建配置
    config = AgentConfig(
        name="simple-agent", type="simple", priority=1, skills=["skill1", "skill2"]
    )

    # 创建Agent
    agent = SimpleAgent(config)

    # 执行任务
    result = agent.execute("测试任务")
    logger.info(f"执行结果: {result}")
