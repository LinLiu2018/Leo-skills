"""
Subagent基类
============
所有Subagent的基础类
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from dataclasses import dataclass
from datetime import datetime

if TYPE_CHECKING:
    from ..skills_bridge import SkillLoader, SkillExecutor


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
        from ..skills_bridge.skill_loader import get_loader
        from ..skills_bridge.skill_executor import get_executor

        self.config = config
        self.skill_loader = get_loader()
        self.skill_executor = get_executor()
        self.task_history: List[Dict[str, Any]] = []

    @abstractmethod
    def can_handle(self, task: str) -> float:
        """
        判断是否能处理此任务

        Args:
            task: 任务描述

        Returns:
            置信度 (0.0 - 1.0)
        """
        pass

    @abstractmethod
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        执行任务

        Args:
            task: 任务描述
            **kwargs: 任务参数

        Returns:
            执行结果
        """
        pass

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

    def use_skill(self,
                  skill_name: str,
                  action: str,
                  **kwargs) -> Any:
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
            raise ValueError(f"Agent '{self.config.name}' 没有 Skill '{skill_name}'")

        result = self.skill_executor.execute(skill_name, action, **kwargs)

        return result

    def plan_execution(self,
                      task: str,
                      **kwargs) -> List[Dict[str, Any]]:
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
            steps.append({
                "step": len(steps) + 1,
                "skill": skill_name,
                "action": "execute",
                "params": kwargs
            })

        return steps

    def log_task(self,
                 task: str,
                 result: Dict[str, Any]):
        """
        记录任务执行历史

        Args:
            task: 任务描述
            result: 执行结果
        """
        self.task_history.append({
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "result": result
        })

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
            "tasks_completed": len(self.task_history)
        }

    def __repr__(self):
        return f"Agent({self.config.name}, type={self.config.type}, skills={len(self.config.skills)})"


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
    def register_agent_class(cls,
                            agent_type: str,
                            agent_class: type):
        """
        注册Agent类

        Args:
            agent_type: Agent类型
            agent_class: Agent类
        """
        cls._agent_classes[agent_type] = agent_class

    @classmethod
    def create_agent(cls,
                    config: AgentConfig) -> BaseAgent:
        """
        创建Agent实例

        Args:
            config: Agent配置

        Returns:
            Agent实例
        """
        agent_class = cls._agent_classes.get(config.type)

        if not agent_class:
            raise ValueError(f"未知的Agent类型: {config.type}")

        agent = agent_class(config)
        cls._agents[config.name] = agent

        return agent

    @classmethod
    def get_agent(cls,
                 name: str) -> Optional[BaseAgent]:
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
            result = {
                "task": task,
                "status": "completed",
                "message": f"任务 '{task}' 已完成"
            }
            self.log_task(task, result)
            return result

    # 创建配置
    config = AgentConfig(
        name="simple-agent",
        type="simple",
        priority=1,
        skills=["skill1", "skill2"]
    )

    # 创建Agent
    agent = SimpleAgent(config)

    # 执行任务
    result = agent.execute("测试任务")
    print(f"执行结果: {result}")
