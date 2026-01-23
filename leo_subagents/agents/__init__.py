"""
Leo Subagents
=============
各类Subagent的实现

包括:
- BaseAgent: 所有Agent的基类
- TaskAgent: 任务执行代理
- ResearchAgent: 研究代理
- AnalysisAgent: 分析代理
- CreativeAgent: 创作代理
"""

from .base_agent import BaseAgent, AgentConfig, AgentFactory
from .task_agent import TaskAgent

# 导入新实现的3个Agent
try:
    from .research_agent.research_agent import ResearchAgent
    from .analysis_agent.analysis_agent import AnalysisAgent
    from .creative_agent.creative_agent import CreativeAgent

    __all__ = [
        'BaseAgent',
        'AgentConfig',
        'AgentFactory',
        'TaskAgent',
        'ResearchAgent',
        'AnalysisAgent',
        'CreativeAgent',
    ]
except ImportError as e:
    print(f"⚠️  导入Agent失败: {e}")
    __all__ = [
        'BaseAgent',
        'AgentConfig',
        'AgentFactory',
        'TaskAgent',
    ]
