"""
Flask API Generator Skill
=========================
自动生成Flask RESTful API代码
"""

from pathlib import Path
from typing import List, Dict, Optional
import json


class FlaskAPIGenerator:
    """Flask API代码生成器"""

    def __init__(self, output_dir: str = "."):
        self.output_dir = Path(output_dir)

    def generate(
        self,
        resource_name: str,
        fields: List[Dict],
        endpoints: Optional[List[Dict]] = None,
        auth_required: bool = False
    ) -> Dict[str, str]:
        """
        生成完整的Flask API代码

        Args:
            resource_name: 资源名称（如 lead, user）
            fields: 字段定义列表
            endpoints: 自定义端点（可选）
            auth_required: 是否需要认证

        Returns:
            生成的文件路径字典
        """
        results = {}

        # 生成Model
        model_code = self._generate_model(resource_name, fields)
        results['model'] = model_code

        # 生成Schema
        schema_code = self._generate_schema(resource_name, fields)
        results['schema'] = schema_code

        # 生成Service
        service_code = self._generate_service(resource_name)
        results['service'] = service_code

        # 生成Blueprint
        blueprint_code = self._generate_blueprint(resource_name, endpoints, auth_required)
        results['blueprint'] = blueprint_code

        return results

    def _generate_model(self, resource_name: str, fields: List[Dict]) -> str:
        """生成SQLAlchemy Model"""
        class_name = resource_name.capitalize()

        field_lines = []
        for field in fields:
            name = field['name']
            ftype = self._map_field_type(field.get('type', 'string'))
            nullable = not field.get('required', False)
            unique = field.get('unique', False)
            default = field.get('default')

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
{self._generate_to_dict_fields(fields)}
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }}

    def __repr__(self):
        return f'<{class_name} {{self.id}}>'
'''

    def _generate_schema(self, resource_name: str, fields: List[Dict]) -> str:
        """生成Marshmallow Schema"""
        class_name = resource_name.capitalize()

        field_lines = []
        for field in fields:
            name = field['name']
            ftype = self._map_schema_type(field.get('type', 'string'))
            required = field.get('required', False)

            line = f"    {name} = fields.{ftype}(required={required})"
            field_lines.append(line)

        fields_str = "\n".join(field_lines)

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
{self._generate_optional_fields(fields)}
'''

    def _generate_service(self, resource_name: str) -> str:
        """生成Service层"""
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

    def _generate_blueprint(
        self,
        resource_name: str,
        endpoints: Optional[List[Dict]] = None,
        auth_required: bool = False
    ) -> str:
        """生成Flask Blueprint"""
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

    def _map_field_type(self, field_type: str) -> str:
        """映射字段类型到SQLAlchemy类型"""
        type_map = {
            'string': 'db.String(255)',
            'text': 'db.Text',
            'integer': 'db.Integer',
            'float': 'db.Float',
            'boolean': 'db.Boolean',
            'datetime': 'db.DateTime',
            'date': 'db.Date',
            'json': 'db.JSON'
        }
        return type_map.get(field_type.lower(), 'db.String(255)')

    def _map_schema_type(self, field_type: str) -> str:
        """映射字段类型到Marshmallow类型"""
        type_map = {
            'string': 'Str',
            'text': 'Str',
            'integer': 'Int',
            'float': 'Float',
            'boolean': 'Bool',
            'datetime': 'DateTime',
            'date': 'Date',
            'json': 'Dict'
        }
        return type_map.get(field_type.lower(), 'Str')

    def _generate_to_dict_fields(self, fields: List[Dict]) -> str:
        """生成to_dict方法的字段"""
        lines = []
        for field in fields:
            name = field['name']
            lines.append(f"            '{name}': self.{name},")
        return "\n".join(lines)

    def _generate_optional_fields(self, fields: List[Dict]) -> str:
        """生成可选字段（用于更新Schema）"""
        lines = []
        for field in fields:
            name = field['name']
            ftype = self._map_schema_type(field.get('type', 'string'))
            lines.append(f"    {name} = fields.{ftype}(required=False)")
        return "\n".join(lines)

    def save_files(self, resource_name: str, results: Dict[str, str]) -> Dict[str, Path]:
        """保存生成的文件"""
        saved = {}

        # 创建目录
        dirs = ['models', 'schemas', 'services', 'blueprints']
        for d in dirs:
            (self.output_dir / 'app' / d).mkdir(parents=True, exist_ok=True)

        # 保存文件
        model_path = self.output_dir / 'app' / 'models' / f'{resource_name}.py'
        model_path.write_text(results['model'], encoding='utf-8')
        saved['model'] = model_path

        schema_path = self.output_dir / 'app' / 'schemas' / f'{resource_name}_schema.py'
        schema_path.write_text(results['schema'], encoding='utf-8')
        saved['schema'] = schema_path

        service_path = self.output_dir / 'app' / 'services' / f'{resource_name}_service.py'
        service_path.write_text(results['service'], encoding='utf-8')
        saved['service'] = service_path

        bp_path = self.output_dir / 'app' / 'blueprints' / f'{resource_name}_bp.py'
        bp_path.write_text(results['blueprint'], encoding='utf-8')
        saved['blueprint'] = bp_path

        return saved


def main():
    """示例用法"""
    generator = FlaskAPIGenerator(output_dir="./output")

    # 定义字段
    fields = [
        {'name': 'name', 'type': 'string', 'required': True},
        {'name': 'phone', 'type': 'string', 'required': True},
        {'name': 'parent_id', 'type': 'integer', 'required': False},
        {'name': 'status', 'type': 'string', 'default': 'new'}
    ]

    # 生成代码
    results = generator.generate(
        resource_name='lead',
        fields=fields,
        auth_required=False
    )

    # 保存文件
    saved = generator.save_files('lead', results)

    print("生成完成！")
    for name, path in saved.items():
        print(f"  {name}: {path}")


if __name__ == '__main__':
    main()
