"""
Lead Schema
"""
from marshmallow import Schema, fields, validate


class LeadSchema(Schema):
    """
    Lead序列化Schema
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    phone = fields.Str(required=True)
    parent_id = fields.Int(required=False)
    status = fields.Str(required=False)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class LeadCreateSchema(Schema):
    """创建Lead的Schema"""
    name = fields.Str(required=True)
    phone = fields.Str(required=True)
    parent_id = fields.Int(required=False)
    status = fields.Str(required=False)


class LeadUpdateSchema(Schema):
    """更新Lead的Schema"""
    name = fields.Str(required=False)
    phone = fields.Str(required=False)
    parent_id = fields.Int(required=False)
    status = fields.Str(required=False)
