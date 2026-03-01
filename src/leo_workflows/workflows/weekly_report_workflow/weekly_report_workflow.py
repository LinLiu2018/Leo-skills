"""
Weekly report workflow implementation.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from leo_workflows.pipeline_base import PipelineBase


class WeeklyReportWorkflow(PipelineBase):
    """Pipeline wrapper for weekly_report_workflow definition."""

    yaml_name = "weekly_report_workflow"

    def run(
        self,
        orchestrator,
        week_start: Optional[str] = None,
        week_end: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        inputs = {
            "week_start": week_start,
            "week_end": week_end,
        }
        inputs.update(kwargs)
        return orchestrator.run_workflow(self.config, inputs)


def create_pipeline() -> WeeklyReportWorkflow:
    return WeeklyReportWorkflow()
