"""
User Schema
"""
from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    """
    User序列化Schema
    """
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Str(required=True)
    password_hash = fields.Str(required=True)
    phone = fields.Str(required=False)
    status = fields.Str(required=False)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class UserCreateSchema(Schema):
    """创建User的Schema"""
    username = fields.Str(required=True)
    email = fields.Str(required=True)
    password_hash = fields.Str(required=True)
    phone = fields.Str(required=False)
    status = fields.Str(required=False)


class UserUpdateSchema(Schema):
    """更新User的Schema"""
    username = fields.Str(required=False)
    email = fields.Str(required=False)
    password_hash = fields.Str(required=False)
    phone = fields.Str(required=False)
    status = fields.Str(required=False)
