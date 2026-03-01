"""
Execution layer that wires intent/perception/cognition into one pipeline.
"""

from __future__ import annotations

from typing import Any, Dict

from .intent_parser import IntentParser
from .monitor import SystemMonitor
from .strategy_engine import StrategyEngine


class AutoEvolutionPipeline:
    """Four-layer auto-evolution pipeline implementation."""

    def __init__(self):
        self.intent_parser = IntentParser()
        self.monitor = SystemMonitor()
        self.strategy_engine = StrategyEngine()

    def run_cycle(self, request_text: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        context = context or {}
        parsed = self.intent_parser.parse(request_text)

        self.monitor.record_event(
            event_type="intent_parsed",
            status="success",
            latency_ms=80,
            detail={"category": parsed.category},
        )

        metrics = self.monitor.get_metrics()
        strategy = self.strategy_engine.generate_strategy(
            intent={
                "category": parsed.category,
                "confidence": parsed.confidence,
                "goals": parsed.goals,
                "entities": parsed.entities,
            },
            metrics=metrics,
        )

        execution_plan = {
            "request": request_text,
            "category": parsed.category,
            "goals": parsed.goals,
            "strategy": strategy,
            "context": context,
        }

        self.monitor.record_event(
            event_type="strategy_generated",
            status="success",
            latency_ms=60,
            detail={"mode": strategy["mode"]},
        )

        return {
            "status": "success",
            "intent": {
                "category": parsed.category,
                "confidence": parsed.confidence,
                "goals": parsed.goals,
                "entities": parsed.entities,
            },
            "metrics": self.monitor.get_metrics(),
            "execution_plan": execution_plan,
        }
