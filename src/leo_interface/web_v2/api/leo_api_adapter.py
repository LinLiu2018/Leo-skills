"""
Leo API 统一适配器。
所有 Web 请求通过此适配器转发到 LeoAPI，确保入口唯一。
"""

from pathlib import Path

from leo_orchestrator.api import LeoAPI

_api_instance = None


def get_leo_api() -> LeoAPI:
    """获取 LeoAPI 单例。"""
    global _api_instance
    if _api_instance is None:
        project_root = Path(__file__).parent.parent.parent.parent.parent
        _api_instance = LeoAPI(str(project_root / "src"))
    return _api_instance

