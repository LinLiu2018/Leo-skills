# -*- coding: utf-8 -*-
import importlib.util
import sys
from pathlib import Path

# 动态导入连字符模块
_module_name = "chain-of-thought-prompter"
_spec = importlib.util.spec_from_file_location(
    _module_name,
    Path(__file__).parent / "chain-of-thought-prompter.py"
)
_module = importlib.util.module_from_spec(_spec)
sys.modules[_module_name] = _module
_spec.loader.exec_module(_module)

# 导出类
ChainOfThoughtPrompter = _module.ChainOfThoughtPrompter

__all__ = ["ChainOfThoughtPrompter"]
