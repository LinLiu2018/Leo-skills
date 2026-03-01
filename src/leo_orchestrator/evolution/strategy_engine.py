"""
Cognition/strategy layer.
"""

from __future__ import annotations

from typing import Any, Dict


class StrategyEngine:
    """Generate next-step strategy from parsed intent and runtime metrics."""

    def generate_strategy(self, intent: Dict[str, Any], metrics: Dict[str, float]) -> Dict[str, Any]:
        category = intent.get("category", "general")
        error_rate = float(metrics.get("error_rate", 0.0))
        avg_latency = float(metrics.get("avg_latency_ms", 0.0))

        if error_rate > 0.2:
            mode = "stabilize"
            actions = [
                "reduce concurrent workload",
                "route critical tasks to known stable agents",
                "send warning report",
            ]
        elif avg_latency > 3000:
            mode = "optimize"
            actions = [
                "enable cached paths",
                "prefer lightweight models",
                "defer low-priority tasks",
            ]
        else:
            mode = "expand"
            actions = [
                "run standard pipeline",
                "apply domain-specific automation",
                "log outcomes for iterative improvement",
            ]

        return {
            "mode": mode,
            "category": category,
            "actions": actions,
            "confidence": intent.get("confidence", 0.5),
        }
