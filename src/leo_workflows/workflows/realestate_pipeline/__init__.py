"""
RealEstate Pipeline - 房产营销工作流
"""

from .realestate_pipeline import RealEstatePipeline, create_pipeline

# 别名支持
RealestatePipeline = RealEstatePipeline

__all__ = ["RealEstatePipeline", "RealestatePipeline", "create_pipeline"]
