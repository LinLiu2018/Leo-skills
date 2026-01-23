"""
Leo Subagents - 智能体代理库
============================
提供各类AI Agent的实现和管理
"""

from pathlib import Path

# 包版本
__version__ = "1.0.0"

# 包路径
PACKAGE_DIR = Path(__file__).parent.absolute()
AGENTS_DIR = PACKAGE_DIR / "agents"

# 延迟导入
def get_agent_factory():
    """获取 AgentFactory 实例"""
    from .agents.base_agent import AgentFactory
    return AgentFactory

def get_skill_loader():
    """获取 SkillLoader 实例"""
    from .skills_bridge.skill_loader import SkillLoader
    return SkillLoader()

def get_skill_executor():
    """获取 SkillExecutor 实例"""
    from .skills_bridge.skill_loader import SkillLoader
    from .skills_bridge.skill_executor import SkillExecutor
    loader = SkillLoader()
    return SkillExecutor(loader)

# 导出的公共接口
__all__ = [
    "__version__",
    "PACKAGE_DIR",
    "AGENTS_DIR",
    "get_agent_factory",
    "get_skill_loader",
    "get_skill_executor",
]
