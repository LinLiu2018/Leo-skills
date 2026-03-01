"""
Health check routines for Wingman.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict


def check_core_paths() -> Dict[str, bool]:
    paths = {
        "memory": Path("leo_wingman/memory").exists(),
        "executor": Path("leo_wingman/executor").exists(),
        "selfcare": Path("leo_wingman/selfcare").exists(),
        "orchestrator": Path("src/leo_orchestrator").exists(),
        "workflows": Path("src/leo_workflows/definitions").exists(),
    }
    return paths


def overall_status() -> Dict[str, str]:
    checks = check_core_paths()
    if all(checks.values()):
        return {"status": "healthy"}
    return {"status": "degraded"}
