#!/usr/bin/env python3
"""
Leo Skills Evolution Framework - 技能自我进化框架

提供技能自我学习、优化和进化的核心能力。

使用方法:
    from leo_skills.core.evolution import EvolvableSkill

    class MySkill(EvolvableSkill):
        def _execute_core(self, *args, **kwargs):
            # 实现你的技能逻辑
            return {'success': True, 'quality_score': 0.8}
"""

from .metrics import (
    ExecutionMetrics,
    AnalysisResult,
    BestPractice,
    OptimizationRule,
    ExecutionResult
)

from .learner import SkillLearner
from .evolver import SkillEvolver
from .adapter import SkillAdapter
from .performer import EvolvableSkill

__all__ = [
    'EvolvableSkill',
    'SkillLearner',
    'SkillEvolver',
    'SkillAdapter',
    'ExecutionMetrics',
    'AnalysisResult',
    'BestPractice',
    'OptimizationRule',
    'ExecutionResult'
]

__version__ = '0.1.0'
