"""
Execution pipeline for Wingman tasks.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from .task_parser import parse_task, to_dict


class WingmanPipeline:
    """Minimal pipeline for task parse -> execute -> summarize."""

    def __init__(self):
        self._steps: List[str] = []

    def run(self, task: str, handlers: Dict[str, Callable[[str], Any]] | None = None) -> Dict[str, Any]:
        handlers = handlers or {}
        parsed = parse_task(task)
        self._steps.append("parse")

        execution_results: Dict[str, Any] = {}
        for intent in parsed.intents:
            handler = handlers.get(intent)
            if handler is None:
                execution_results[intent] = {"status": "skipped", "reason": "no_handler"}
                continue
            execution_results[intent] = {"status": "success", "result": handler(task)}

        self._steps.append("execute")
        self._steps.append("summarize")

        return {
            "status": "success",
            "parsed": to_dict(parsed),
            "steps": list(self._steps),
            "results": execution_results,
        }
