"""
Leo Workflows
=============
预定义的工作流集合
"""

from .analysis_pipeline import analysis_pipeline
from .content_pipeline import content_pipeline
from .research_pipeline import research_pipeline
from .ecommerce_pipeline import EcommercePipeline, create_pipeline as ecommerce_pipeline
from .realestate_pipeline import RealEstatePipeline, create_pipeline as realestate_pipeline
from .practice_to_knowledge_pipeline import practice_to_knowledge_pipeline
from .realestate_marketing_pipeline import (
    RealEstateMarketingPipeline,
    create_pipeline as realestate_marketing_pipeline,
)
from .weekly_report_workflow import (
    WeeklyReportWorkflow,
    create_pipeline as weekly_report_workflow,
)
