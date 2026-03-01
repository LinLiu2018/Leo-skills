"""Skill workflow orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Protocol


class SkillRunnable(Protocol):
    """Protocol for skill-like objects."""

    def execute(self, *args, **kwargs) -> Any: ...


@dataclass
class WorkflowStep:
    """Single workflow step."""

    skill_name: str
    executor: Any
    config: Dict[str, Any] = field(default_factory=dict)
    continue_on_error: bool = False
    context_builder: Optional[Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]] = None


class SkillWorkflow:
    """Simple workflow pipeline for chaining skills."""

    def __init__(self) -> None:
        self.steps: List[WorkflowStep] = []

    def add_step(
        self,
        skill_name: str,
        executor: Any,
        config: Optional[Dict[str, Any]] = None,
        continue_on_error: bool = False,
        context_builder: Optional[
            Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]
        ] = None,
    ) -> WorkflowStep:
        step = WorkflowStep(
            skill_name=skill_name,
            executor=executor,
            config=config or {},
            continue_on_error=continue_on_error,
            context_builder=context_builder,
        )
        self.steps.append(step)
        return step

    def execute(self, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context: Dict[str, Any] = dict(initial_context or {})
        history: List[Dict[str, Any]] = []

        for step in self.steps:
            step_context = (
                step.context_builder(context, step.config)
                if step.context_builder
                else self._merge_context(context, step.config)
            )

            try:
                result = self._run_step(step.executor, step_context)
            except Exception as exc:
                entry = {
                    "skill": step.skill_name,
                    "success": False,
                    "error": str(exc),
                }
                history.append(entry)
                if not step.continue_on_error:
                    return {
                        "success": False,
                        "error": str(exc),
                        "failed_step": step.skill_name,
                        "history": history,
                        "context": context,
                    }
                continue

            context = self._merge_context(context, self._to_dict(result))
            history.append({"skill": step.skill_name, "success": True, "result": result})

        return {"success": True, "history": history, "context": context}

    def _run_step(self, executor: Any, context: Dict[str, Any]) -> Any:
        if hasattr(executor, "run"):
            return executor.run(context=context, auto_notify=False)
        if hasattr(executor, "execute"):
            try:
                return executor.execute(context=context)
            except TypeError:
                return executor.execute(**context)
        if callable(executor):
            return executor(context)
        raise TypeError(f"Unsupported workflow executor type: {type(executor)}")

    def _to_dict(self, value: Any) -> Dict[str, Any]:
        if value is None:
            return {}
        if hasattr(value, "to_dict") and callable(value.to_dict):
            return value.to_dict()
        if isinstance(value, dict):
            return value
        return {"result": value}

    def _merge_context(self, base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(base)
        for key, value in updates.items():
            if isinstance(merged.get(key), dict) and isinstance(value, dict):
                child = dict(merged[key])
                child.update(value)
                merged[key] = child
            else:
                merged[key] = value
        return merged
