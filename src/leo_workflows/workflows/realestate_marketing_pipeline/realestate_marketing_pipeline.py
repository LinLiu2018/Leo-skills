"""
RealEstate Marketing Pipeline implementation.
"""

from __future__ import annotations

from typing import Any, Dict

from leo_workflows.pipeline_base import PipelineBase


class RealEstateMarketingPipeline(PipelineBase):
    """Pipeline wrapper for realestate_marketing_pipeline definition."""

    yaml_name = "realestate_marketing_pipeline"

    def run(
        self,
        orchestrator,
        project_name: str,
        city: str = "Ningbo",
        segment: str = "villa",
        **kwargs,
    ) -> Dict[str, Any]:
        if not project_name:
            raise ValueError("missing required parameter: project_name")

        inputs = {
            "project_name": project_name,
            "city": city,
            "segment": segment,
        }
        inputs.update(kwargs)
        return orchestrator.run_workflow(self.config, inputs)


def create_pipeline() -> RealEstateMarketingPipeline:
    return RealEstateMarketingPipeline()
