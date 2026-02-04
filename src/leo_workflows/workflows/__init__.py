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
