# -*- coding: utf-8 -*-
"""
Leo System 自优化模块

实现 OpenClaw "越用越好" 的核心机制：
1. 对话分析器 - 分析会话历史，提取模式
2. 技能推荐引擎 - 基于意图推荐/生成技能
3. 效果追踪系统 - 记录和分析执行效果
4. 自优化引擎 - 整合分析-推荐-生成-追踪闭环
5. 自动技能生成器 - 基于意图自动生成技能代码
6. 联邦学习 - 跨用户模式聚合与优化
"""

from .conversation_analyzer import ConversationAnalyzer
from .skill_recommender import SkillRecommender
from .performance_tracker import PerformanceTracker
from .self_optimization_engine import SelfOptimizationEngine, run_self_optimization
from .auto_skill_generator import AutoSkillGenerator, auto_generate_skill
from .federated_learning import CrossUserLearning, contribute_user_patterns, get_global_insights

__all__ = [
    # 核心分析器
    "ConversationAnalyzer",
    "SkillRecommender",
    "PerformanceTracker",
    # 自优化引擎
    "SelfOptimizationEngine",
    "run_self_optimization",
    # 技能生成
    "AutoSkillGenerator",
    "auto_generate_skill",
    # 联邦学习
    "CrossUserLearning",
    "contribute_user_patterns",
    "get_global_insights",
]
