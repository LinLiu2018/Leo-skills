"""
Reward Schema
"""
from marshmallow import Schema, fields, validate


class RewardSchema(Schema):
    """
    Reward序列化Schema
    """
    id = fields.Int(dump_only=True)
    lead_id = fields.Int(required=True)
    reward_type = fields.Str(required=True)
    amount = fields.Float(required=True)
    status = fields.Str(required=False)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class RewardCreateSchema(Schema):
    """创建Reward的Schema"""
    lead_id = fields.Int(required=True)
    reward_type = fields.Str(required=True)
    amount = fields.Float(required=True)
    status = fields.Str(required=False)


class RewardUpdateSchema(Schema):
    """更新Reward的Schema"""
    lead_id = fields.Int(required=False)
    reward_type = fields.Str(required=False)
    amount = fields.Float(required=False)
    status = fields.Str(required=False)
