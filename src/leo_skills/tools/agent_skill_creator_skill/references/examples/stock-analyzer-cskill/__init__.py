# -*- coding: utf-8 -*-
"""
stock-analyzer-cskill - 技能描述

详情请查看 SKILL.md
"""

from importlib import import_module as _im

# 文件名含连字符，无法直接 import，使用 importlib
_mod = _im(".stock-analyzer-cskill", __package__)
StockAnalyzerCskillSkill = _mod.StockAnalyzerCskillSkill

__all__ = ["StockAnalyzerCskillSkill"]
