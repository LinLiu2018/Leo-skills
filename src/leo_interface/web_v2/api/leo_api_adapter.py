"""Lazy adapter to LeoAPI."""

from pathlib import Path

_api_instance = None


def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / 'src').exists() and (current / 'leo_knowledge').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parents[4]


def get_leo_api():
    global _api_instance
    if _api_instance is None:
        from leo_orchestrator.api import LeoAPI

        project_root = _find_project_root()
        _api_instance = LeoAPI(str(project_root / 'src'))
    return _api_instance
