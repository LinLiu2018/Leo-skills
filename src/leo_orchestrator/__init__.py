"""
Leo Orchestrator - 统一编排器
============================
提供Skills和Subagents的统一管理和协调
"""

from pathlib import Path

# 包版本
__version__ = "1.0.0"

# 包路径
PACKAGE_DIR = Path(__file__).parent.absolute()


# 延迟导入以避免循环依赖
def get_registry():
    """获取统一注册表实例"""
    from .registry import get_registry as _get_registry

    return _get_registry()


def get_api():
    """获取 LeoAPI 实例"""
    from .api import LeoAPI

    return LeoAPI()


def get_intent_recognizer(registry=None):
    """获取意图识别器实例"""
    from .intent_recognizer import get_intent_recognizer as _get_recognizer
    return _get_recognizer(registry)


def get_workflow_engine(agents=None, max_workers=4):
    """获取工作流引擎实例"""
    from .workflow_engine import WorkflowEngine
    return WorkflowEngine(agents or {}, max_workers)


# 导出的公共接口
__all__ = [
    "__version__",
    "PACKAGE_DIR",
    "get_registry",
    "get_api",
    "get_intent_recognizer",
    "get_workflow_engine",
]
