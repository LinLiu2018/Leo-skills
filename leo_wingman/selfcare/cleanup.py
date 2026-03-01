"""
Cleanup routines for Wingman.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List


def cleanup_old_logs(base_dir: str, keep_latest: int = 20) -> Dict[str, List[str]]:
    root = Path(base_dir)
    if not root.exists():
        return {"removed": [], "status": "missing_dir"}

    files = sorted([f for f in root.glob("*.log") if f.is_file()], key=lambda p: p.stat().st_mtime, reverse=True)
    to_remove = files[keep_latest:]
    removed: List[str] = []
    for item in to_remove:
        item.unlink(missing_ok=True)
        removed.append(str(item))
    return {"removed": removed, "status": "success"}
