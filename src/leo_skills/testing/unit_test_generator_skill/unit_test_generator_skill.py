"""
unit_test_generator_skill

单元测试生成技能
"""

from __future__ import annotations

import inspect
from typing import Any, Dict, Optional

from leo_skills.core.base_executor import BaseExecutor
from .scripts.main import UnitTestGenerator as _LegacyUnitTestGenerator


class UnitTestGenerator(BaseExecutor):
    """Executor wrapper for legacy UnitTestGenerator."""

    def __init__(self) -> None:
        self.name = "unit_test_generator_skill"
        self._delegate = _LegacyUnitTestGenerator()

    def execute(
        self,
        action: str = "run",
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(context or {})
        params.update(kwargs)
        result = self._invoke_delegate(action=action, params=params)

        if isinstance(result, dict):
            return result
        if hasattr(result, "to_dict") and callable(result.to_dict):
            return result.to_dict()
        return {"status": "success", "action": action, "data": result}

    def _invoke_delegate(self, action: str, params: Dict[str, Any]) -> Any:
        delegate = self._delegate

        if hasattr(delegate, "execute"):
            execute_fn = delegate.execute
            try:
                signature = inspect.signature(execute_fn)
                if "action" in signature.parameters and "action" not in params:
                    params["action"] = action
            except (TypeError, ValueError):
                pass
            try:
                return execute_fn(**params)
            except TypeError:
                return execute_fn()

        if hasattr(delegate, "run"):
            run_fn = delegate.run
            try:
                return run_fn(**params)
            except TypeError:
                return run_fn()

        if callable(delegate):
            try:
                return delegate(**params)
            except TypeError:
                return delegate()

        raise TypeError(f"Delegate {delegate.__class__.__name__} has no execute/run/call entrypoint")


__all__ = ["UnitTestGenerator"]
