# -*- coding: utf-8 -*-
"""
evolution.base - 向后兼容导入模块

此模块为兼容早期代码的导入路径而保留。
新代码应直接使用：from leo_skills.core.evolution import EvolvableSkill
"""

from .evolution_skill import EvolutionSkill

# 兼容性别名
EvolvableSkill = EvolutionSkill

__all__ = ["EvolvableSkill", "EvolutionSkill"]
