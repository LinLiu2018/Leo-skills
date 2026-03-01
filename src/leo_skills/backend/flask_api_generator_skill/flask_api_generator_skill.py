"""
flask_api_generator_skill - Flask API 生成技能

自动生成 Flask RESTful API 代码，包含 Model、Schema、Service 和 Blueprint 四层。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from leo_skills.core.base_executor import BaseExecutor


class FlaskAPIGenerator(BaseExecutor):
    """Flask API 代码生成器 - 生成完整的 Model/Schema/Service/Blueprint 四层代码"""

    def __init__(self, output_dir: str = ".") -> None:
        self.name = "flask_api_generator_skill"
        self.output_dir = Path(output_dir)

    # ------------------------------------------------------------------
    # BaseExecutor 入口
    # ------------------------------------------------------------------

    def execute(
        self,
        action: str = "generate",
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """执行技能

        支持的 action:
            generate - 生成代码并返回（默认）
            save     - 生成代码并保存到磁盘

        参数（通过 context 或 kwargs 传入）:
            resource_name: str      - 资源名称，如 lead / user（必填）
            fields: List[Dict]      - 字段定义列表（必填）
            endpoints: List[Dict]   - 自定义端点（可选）
            auth_required: bool     - 是否需要 JWT 认证，默认 False
            output_dir: str         - 输出目录（可选）
        """
        params: Dict[str, Any] = dict(context or {})
        params.update(kwargs)

        if "output_dir" in params:
            self.output_dir = Path(params["output_dir"])

        if action == "generate":
            return self._action_generate(params)
        if action == "save":
            return self._action_save(params)

        return {"status": "error", "message": f"未知的 action: {action}"}

    # ------------------------------------------------------------------
    # action: generate
    # ------------------------------------------------------------------

    def _action_generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """生成代码并返回"""
        resource_name: str = params.get("resource_name", "")
        fields: List[Dict] = params.get("fields", [])
        endpoints: Optional[List[Dict]] = params.get("endpoints")
        auth_required: bool = params.get("auth_required", False)

        if not resource_name:
            return {"status": "error", "message": "resource_name 参数不能为空"}
        if not fields:
            return {"status": "error", "message": "fields 参数不能为空"}

        result = self._generate_all(resource_name, fields, endpoints, auth_required)
        return {"status": "success", "action": "generate", "data": result}

    # ------------------------------------------------------------------
    # action: save
    # ------------------------------------------------------------------

    def _action_save(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """生成代码并保存到磁盘"""
        resource_name: str = params.get("resource_name", "")
        fields: List[Dict] = params.get("fields", [])
        endpoints: Optional[List[Dict]] = params.get("endpoints")
        auth_required: bool = params.get("auth_required", False)

        if not resource_name:
            return {"status": "error", "message": "resource_name 参数不能为空"}
        if not fields:
            return {"status": "error", "message": "fields 参数不能为空"}

        result = self._generate_all(resource_name, fields, endpoints, auth_required)
        saved = self._save_files(resource_name, result)
        return {
            "status": "success",
            "action": "save",
            "data": result,
            "saved_files": {k: str(v) for k, v in saved.items()},
        }

    # ------------------------------------------------------------------
    # 核心生成逻辑
    # ------------------------------------------------------------------

    def _generate_all(
        self,
        resource_name: str,
        fields: List[Dict],
        endpoints: Optional[List[Dict]],
        auth_required: bool,
    ) -> Dict[str, str]:
        """生成完整的四层代码"""
        return {
            "model": self._generate_model(resource_name, fields),
            "schema": self._generate_schema(resource_name, fields),
            "service": self._generate_service(resource_name),
            "blueprint": self._generate_blueprint(
                resource_name, endpoints, auth_required
            ),
        }

    # ------------------------------------------------------------------
    # Model 层
    # ------------------------------------------------------------------

    def _generate_model(self, resource_name: str, fields: List[Dict]) -> str:
        """生成 SQLAlchemy Model 代码"""
        class_name = resource_name.capitalize()

        field_lines: List[str] = []
        for field in fields:
            name = field["name"]
            ftype = self._map_field_type(field.get("type", "string"))
            nullable = not field.get("required", False)
            unique = field.get("unique", False)
            default = field.get("default")

            line = f"    {name} = db.Column({ftype}"
            if unique:
                line += ", unique=True"
            if not nullable:
                line += ", nullable=False"
            if default is not None:
                if isinstance(default, str):
                    line += f", default='{default}'"
                else:
                    line += f", default={default}"
            line += ")"
            field_lines.append(line)

        fields_str = "\n".join(field_lines)
        to_dict_fields = self._to_dict_fields(fields)

        return f'''"""
{class_name} Model
"""
from datetime import datetime
from app import db


class {class_name}(db.Model):
    """
    {class_name}数据模型
    """
    __tablename__ = '{resource_name}s'

    id = db.Column(db.Integer, primary_key=True)
{fields_str}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {{
            'id': self.id,
{to_dict_fields}
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }}

    def __repr__(self):
        return f'<{class_name} {{self.id}}>'
'''

    # ------------------------------------------------------------------
    # Schema 层
    # ------------------------------------------------------------------

    def _generate_schema(self, resource_name: str, fields: List[Dict]) -> str:
        """生成 Marshmallow Schema 代码"""
        class_name = resource_name.capitalize()

        field_lines: List[str] = []
        for field in fields:
            name = field["name"]
            ftype = self._map_schema_type(field.get("type", "string"))
            required = field.get("required", False)
            field_lines.append(f"    {name} = fields.{ftype}(required={required})")

        fields_str = "\n".join(field_lines)
        optional_fields = self._optional_fields(fields)

        return f'''"""
{class_name} Schema
"""
from marshmallow import Schema, fields, validate


class {class_name}Schema(Schema):
    """
    {class_name}序列化Schema
    """
    id = fields.Int(dump_only=True)
{fields_str}
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class {class_name}CreateSchema(Schema):
    """创建{class_name}的Schema"""
{fields_str}


class {class_name}UpdateSchema(Schema):
    """更新{class_name}的Schema"""
{optional_fields}
'''

    # ------------------------------------------------------------------
    # Service 层
    # ------------------------------------------------------------------

    def _generate_service(self, resource_name: str) -> str:
        """生成 Service 层代码"""
        class_name = resource_name.capitalize()

        return f'''"""
{class_name} Service
"""
from typing import List, Optional
from app import db
from app.models.{resource_name} import {class_name}


class {class_name}Service:
    """
    {class_name}业务逻辑层
    """

    @staticmethod
    def create(data: dict) -> {class_name}:
        """创建{class_name}"""
        item = {class_name}(**data)
        db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def get_by_id(item_id: int) -> Optional[{class_name}]:
        """根据ID获取"""
        return {class_name}.query.get(item_id)

    @staticmethod
    def get_all(page: int = 1, per_page: int = 20) -> List[{class_name}]:
        """获取列表（分页）"""
        return {class_name}.query.paginate(
            page=page, per_page=per_page, error_out=False
        )

    @staticmethod
    def update(item_id: int, data: dict) -> Optional[{class_name}]:
        """更新"""
        item = {class_name}.query.get(item_id)
        if not item:
            return None
        for key, value in data.items():
            if hasattr(item, key) and value is not None:
                setattr(item, key, value)
        db.session.commit()
        return item

    @staticmethod
    def delete(item_id: int) -> bool:
        """删除"""
        item = {class_name}.query.get(item_id)
        if not item:
            return False
        db.session.delete(item)
        db.session.commit()
        return True

    @staticmethod
    def filter_by(**kwargs) -> List[{class_name}]:
        """条件查询"""
        return {class_name}.query.filter_by(**kwargs).all()
'''

    # ------------------------------------------------------------------
    # Blueprint 层
    # ------------------------------------------------------------------

    def _generate_blueprint(
        self,
        resource_name: str,
        endpoints: Optional[List[Dict]],
        auth_required: bool,
    ) -> str:
        """生成 Flask Blueprint 代码"""
        class_name = resource_name.capitalize()

        auth_import = ""
        auth_decorator = ""
        if auth_required:
            auth_import = "from flask_jwt_extended import jwt_required\n"
            auth_decorator = "@jwt_required()\n    "

        return f'''"""
{class_name} API Blueprint
"""
from flask import Blueprint, request, jsonify
{auth_import}from app.models.{resource_name} import {class_name}
from app.schemas.{resource_name}_schema import {class_name}Schema, {class_name}CreateSchema
from app.services.{resource_name}_service import {class_name}Service

bp = Blueprint('{resource_name}', __name__, url_prefix='/api/{resource_name}s')

schema = {class_name}Schema()
schemas = {class_name}Schema(many=True)
create_schema = {class_name}CreateSchema()


@bp.route('', methods=['GET'])
{auth_decorator}def get_list():
    """获取{class_name}列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = {class_name}Service.get_all(page, per_page)

    return jsonify({{
        'success': True,
        'data': schemas.dump(pagination.items),
        'pagination': {{
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }}
    }})


@bp.route('/<int:item_id>', methods=['GET'])
{auth_decorator}def get_one(item_id):
    """获取单个{class_name}"""
    item = {class_name}Service.get_by_id(item_id)
    if not item:
        return jsonify({{'success': False, 'error': '未找到'}}), 404

    return jsonify({{
        'success': True,
        'data': schema.dump(item)
    }})


@bp.route('', methods=['POST'])
{auth_decorator}def create():
    """创建{class_name}"""
    data = request.get_json()

    errors = create_schema.validate(data)
    if errors:
        return jsonify({{'success': False, 'errors': errors}}), 400

    item = {class_name}Service.create(data)

    return jsonify({{
        'success': True,
        'data': schema.dump(item)
    }}), 201


@bp.route('/<int:item_id>', methods=['PUT'])
{auth_decorator}def update(item_id):
    """更新{class_name}"""
    data = request.get_json()

    item = {class_name}Service.update(item_id, data)
    if not item:
        return jsonify({{'success': False, 'error': '未找到'}}), 404

    return jsonify({{
        'success': True,
        'data': schema.dump(item)
    }})


@bp.route('/<int:item_id>', methods=['DELETE'])
{auth_decorator}def delete(item_id):
    """删除{class_name}"""
    success = {class_name}Service.delete(item_id)
    if not success:
        return jsonify({{'success': False, 'error': '未找到'}}), 404

    return jsonify({{'success': True, 'message': '删除成功'}})
'''

    # ------------------------------------------------------------------
    # 类型映射工具
    # ------------------------------------------------------------------

    @staticmethod
    def _map_field_type(field_type: str) -> str:
        """映射字段类型到 SQLAlchemy 类型"""
        type_map = {
            "string": "db.String(255)",
            "text": "db.Text",
            "integer": "db.Integer",
            "float": "db.Float",
            "boolean": "db.Boolean",
            "datetime": "db.DateTime",
            "date": "db.Date",
            "json": "db.JSON",
        }
        return type_map.get(field_type.lower(), "db.String(255)")

    @staticmethod
    def _map_schema_type(field_type: str) -> str:
        """映射字段类型到 Marshmallow 类型"""
        type_map = {
            "string": "Str",
            "text": "Str",
            "integer": "Int",
            "float": "Float",
            "boolean": "Bool",
            "datetime": "DateTime",
            "date": "Date",
            "json": "Dict",
        }
        return type_map.get(field_type.lower(), "Str")

    @staticmethod
    def _to_dict_fields(fields: List[Dict]) -> str:
        """生成 to_dict 方法中的字段映射"""
        lines: List[str] = []
        for field in fields:
            name = field["name"]
            lines.append(f"            '{name}': self.{name},")
        return "\n".join(lines)

    def _optional_fields(self, fields: List[Dict]) -> str:
        """生成可选字段（用于 UpdateSchema）"""
        lines: List[str] = []
        for field in fields:
            name = field["name"]
            ftype = self._map_schema_type(field.get("type", "string"))
            lines.append(f"    {name} = fields.{ftype}(required=False)")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # 文件保存
    # ------------------------------------------------------------------

    def _save_files(
        self, resource_name: str, results: Dict[str, str]
    ) -> Dict[str, Path]:
        """保存生成的代码文件到磁盘"""
        saved: Dict[str, Path] = {}

        # 创建目录
        for d in ("models", "schemas", "services", "blueprints"):
            (self.output_dir / "app" / d).mkdir(parents=True, exist_ok=True)

        # 保存各层文件
        file_map = {
            "model": f"app/models/{resource_name}.py",
            "schema": f"app/schemas/{resource_name}_schema.py",
            "service": f"app/services/{resource_name}_service.py",
            "blueprint": f"app/blueprints/{resource_name}_bp.py",
        }

        for key, rel_path in file_map.items():
            if key in results:
                file_path = self.output_dir / rel_path
                file_path.write_text(results[key], encoding="utf-8")
                saved[key] = file_path

        return saved


__all__ = ["FlaskAPIGenerator"]
