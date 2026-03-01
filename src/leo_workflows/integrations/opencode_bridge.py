"""
Bridge layer between leo_ai_system and an external OpenCode workflow repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from importlib import import_module
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional


SUCCESS_STATUSES = {"completed", "success", "ok", "done"}


def _normalize_status(value: Any) -> str:
    if value is None:
        return "unknown"
    return str(value).strip().lower()


def _is_success_status(status: Any) -> bool:
    return _normalize_status(status) in SUCCESS_STATUSES


def evaluate_scale_gate(
    workflow_results: List[Dict[str, Any]],
    gate: Dict[str, Any],
) -> Dict[str, Any]:
    """Evaluate whether pilot execution is ready for wider promotion."""
    min_success_rate = float(gate.get("min_success_rate", 1.0))
    required_workflows = list(gate.get("required_workflows", []))

    total = len(workflow_results)
    success = sum(1 for result in workflow_results if _is_success_status(result.get("status")))
    success_rate = (success / total) if total else 0.0

    status_by_workflow = {
        str(result.get("workflow_id", "")): _normalize_status(result.get("status"))
        for result in workflow_results
    }
    required_failures = [
        workflow_id
        for workflow_id in required_workflows
        if status_by_workflow.get(workflow_id) not in SUCCESS_STATUSES
    ]

    can_scale = success_rate >= min_success_rate and not required_failures

    return {
        "can_scale": can_scale,
        "success_rate": round(success_rate, 4),
        "minimum_success_rate": min_success_rate,
        "required_workflows": required_workflows,
        "required_failures": required_failures,
        "summary": "GO" if can_scale else "NO_GO",
    }


@dataclass
class OpenCodeWorkflowBridge:
    """
    Execute OpenCode workflow modules from a configured repository path.
    """

    opencode_root: str

    def __post_init__(self) -> None:
        self.root = Path(self.opencode_root).expanduser().resolve()
        self.workflows_dir = self.root / "workflows"
        self._validate_root()
        self._bootstrap_import_path()

    def _validate_root(self) -> None:
        if not self.root.exists():
            raise FileNotFoundError(f"OpenCode root does not exist: {self.root}")
        if not self.workflows_dir.exists():
            raise FileNotFoundError(f"OpenCode workflows directory missing: {self.workflows_dir}")

    def _bootstrap_import_path(self) -> None:
        root_str = str(self.root)
        if root_str not in sys.path:
            sys.path.insert(0, root_str)

    def list_available_workflows(self) -> List[str]:
        workflow_ids: List[str] = []
        for py_file in sorted(self.workflows_dir.glob("*.py")):
            workflow_id = py_file.stem
            if workflow_id.startswith("_") or workflow_id == "workflow_base":
                continue
            workflow_ids.append(workflow_id)
        return workflow_ids

    def execute_workflow(
        self,
        workflow_id: str,
        input_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a workflow factory from OpenCode repository.

        Expected naming convention:
        - module: workflows.<workflow_id>
        - factory: create_<workflow_id>_workflow()
        """
        started_at = datetime.now().isoformat()
        payload = input_data or {}
        try:
            module = import_module(f"workflows.{workflow_id}")
            factory_name = f"create_{workflow_id}_workflow"
            factory = getattr(module, factory_name, None)
            if factory is None:
                raise AttributeError(f"Factory function not found: {factory_name}")

            workflow = factory()
            context = workflow.execute(payload)

            step_results = []
            for step in getattr(context, "step_results", []):
                step_results.append(
                    {
                        "step_id": getattr(step, "step_id", ""),
                        "step_name": getattr(step, "step_name", ""),
                        "status": getattr(step, "status", ""),
                        "error": getattr(step, "error", ""),
                        "duration": getattr(step, "duration", 0.0),
                        "output": getattr(step, "output", {}),
                        "executed_at": getattr(step, "executed_at", ""),
                    }
                )

            return {
                "workflow_id": workflow_id,
                "status": getattr(context, "status", "unknown"),
                "started_at": started_at,
                "completed_at": getattr(context, "completed_at", ""),
                "error": getattr(context, "error", ""),
                "input": payload,
                "output": getattr(context, "output_data", {}),
                "step_results": step_results,
            }
        except Exception as exc:  # pragma: no cover - safety wrapper for external repo variability
            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "started_at": started_at,
                "completed_at": datetime.now().isoformat(),
                "error": str(exc),
                "input": payload,
                "output": {},
                "step_results": [],
            }

    def run_internal_pilot(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run pilot workflows and evaluate scale gate.
        """
        pilot_workflows = list(config.get("pilot_workflows", []))
        if not pilot_workflows:
            raise ValueError("pilot_workflows is empty in config")

        workflow_results: List[Dict[str, Any]] = []
        for item in pilot_workflows:
            workflow_id = str(item.get("id", "")).strip()
            if not workflow_id:
                continue
            input_data = item.get("input", {})
            workflow_results.append(self.execute_workflow(workflow_id, input_data))

        gate = evaluate_scale_gate(workflow_results, config.get("scale_gate", {}))
        return {
            "executed_at": datetime.now().isoformat(),
            "opencode_root": str(self.root),
            "available_workflows": self.list_available_workflows(),
            "workflow_results": workflow_results,
            "scale_gate_result": gate,
        }
