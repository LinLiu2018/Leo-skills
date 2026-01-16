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
    import sys
    from pathlib import Path

    # 导入ResearchAgent
    research_agent_path = Path(__file__).parent / "research-agent" / "research_agent.py"
    if research_agent_path.exists():
        sys.path.insert(0, str(research_agent_path.parent))
        from research_agent import ResearchAgent

    # 导入AnalysisAgent
    analysis_agent_path = Path(__file__).parent / "analysis-agent" / "analysis_agent.py"
    if analysis_agent_path.exists():
        sys.path.insert(0, str(analysis_agent_path.parent))
        from analysis_agent import AnalysisAgent

    # 导入CreativeAgent
    creative_agent_path = Path(__file__).parent / "creative-agent" / "creative_agent.py"
    if creative_agent_path.exists():
        sys.path.insert(0, str(creative_agent_path.parent))
        from creative_agent import CreativeAgent

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
