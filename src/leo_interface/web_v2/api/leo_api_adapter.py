"""
Leo API 统一适配器。
所有 Web 请求通过此适配器转发到 LeoAPI，确保入口唯一。
"""

from pathlib import Path

from leo_orchestrator.api import LeoAPI

_api_instance = None


def _find_project_root() -> Path:
    """从当前文件向上查找包含 pyproject.toml 的目录作为项目根。"""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise RuntimeError("无法定位项目根目录（未找到 pyproject.toml）")


def get_leo_api() -> LeoAPI:
    """获取 LeoAPI 单例。"""
    global _api_instance
    if _api_instance is None:
        project_root = _find_project_root()
        _api_instance = LeoAPI(str(project_root / "src"))
    return _api_instance
