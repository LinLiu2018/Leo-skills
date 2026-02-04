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

from .base_agent import AgentConfig, AgentFactory, BaseAgent
from .task_agent import TaskAgent

# 导入新实现的3个Agent
try:
    from .analysis_agent.analysis_agent import AnalysisAgent
    from .architect_agent.architect_agent import ArchitectAgent
    from .creative_agent.creative_agent import CreativeAgent
    from .mobile_agent.mobile_agent import MobileAgent
    from .product_manager_agent.product_manager_agent import ProductManagerAgent
    from .research_agent.research_agent import ResearchAgent
    from .realestate_agent.realestate_agent import RealEstateAgent
    from .ecommerce_agent.ecommerce_agent import EcommerceAgent

    __all__ = [
        "BaseAgent",
        "AgentConfig",
        "AgentFactory",
        "TaskAgent",
        "ResearchAgent",
        "AnalysisAgent",
        "CreativeAgent",
        "ArchitectAgent",
        "MobileAgent",
        "ProductManagerAgent",
        "RealEstateAgent",
        "EcommerceAgent",
    ]
except ImportError as e:
    print(f"[WARNING]  导入Agent失败: {e}")
    __all__ = [
        "BaseAgent",
        "AgentConfig",
        "AgentFactory",
        "TaskAgent",
    ]
from .ai_news_summary_agent import AiNewsSummaryAgent
