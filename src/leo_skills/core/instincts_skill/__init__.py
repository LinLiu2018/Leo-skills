# -*- coding: utf-8 -*-
"""Instincts Skill 模块"""

from .instincts_skill import (
    InstinctsSkill,
    InstinctRegistry,
    Instinct,
    InstinctEvidence,
    TriggerType,
    get_instinct_registry,
    match_input,
    get_triggered_skill
)

__all__ = [
    "InstinctsSkill",
    "InstinctRegistry",
    "Instinct",
    "InstinctEvidence",
    "TriggerType",
    "get_instinct_registry",
    "match_input",
    "get_triggered_skill"
]