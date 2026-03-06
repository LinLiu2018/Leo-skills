# -*- coding: utf-8 -*-
"""
evolution - 技能进化管理

核心模块：
- EvolutionSkill: 技能进化基础实现
- LLMAnalyzer: LLM 深度分析引擎
- CodeGenerator: 代码自动生成系统
- EvolutionExecutor: 进化执行器
"""

from .evolution_skill import EvolutionSkill, Evolution_Skill
from .analyzer import LLMAnalyzer
from .code_generator import CodeGenerator
from .evolution_executor import EvolutionExecutor

# 兼容性别名
EvolvableSkill = EvolutionSkill

__all__ = [
    "EvolutionSkill",
    "Evolution_Skill",
    "EvolvableSkill",
    "LLMAnalyzer",
    "CodeGenerator",
    "EvolutionExecutor",
]
