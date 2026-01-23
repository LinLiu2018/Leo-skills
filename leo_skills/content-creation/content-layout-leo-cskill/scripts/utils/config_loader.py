#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置加载器
Author: Leo Liu
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any

# 技能根目录
SKILL_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = SKILL_ROOT / "config"


def load_config(config_file: str = "style_profiles.yaml") -> Dict[str, Any]:
    """
    加载YAML配置文件

    Args:
        config_file: 配置文件名

    Returns:
        配置字典
    """
    config_path = CONFIG_DIR / config_file

    if not config_path.exists():
        return {}

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config or {}
    except Exception as e:
        print(f"Warning: Failed to load config {config_file}: {e}")
        return {}


def get_style_config(style_name: str) -> Dict[str, Any]:
    """
    获取指定风格的配置

    Args:
        style_name: 风格名称

    Returns:
        风格配置字典
    """
    config = load_config()
    styles = config.get("styles", [])

    for style in styles:
        if style.get("name") == style_name:
            return style

    # 如果找不到，返回第一个风格
    return styles[0] if styles else {}


def list_styles() -> list:
    """
    列出所有可用风格

    Returns:
        风格列表
    """
    config = load_config()
    styles = config.get("styles", [])
    return [style.get("name") for style in styles]
