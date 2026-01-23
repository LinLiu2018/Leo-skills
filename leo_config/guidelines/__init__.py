"""
去AI化内容处理指南模块
======================

提供去AI化的配置和工具函数
"""

from .deaiifier import DeAIifier, deaiify, check_text_quality

__all__ = [
    'DeAIifier',
    'deaiify',
    'check_text_quality',
]
