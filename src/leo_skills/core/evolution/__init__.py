# -*- coding: utf-8 -*-
"""
evolution - 技能进化管理
"""

from .evolution_skill import EvolutionSkill, Evolution_Skill

# 兼容性别名
EvolvableSkill = EvolutionSkill

__all__ = ["EvolutionSkill", "Evolution_Skill", "EvolvableSkill"]
