"""
database_model_generator_skill - 数据库模型生成技能

自动生成 SQLAlchemy / Peewee 数据库模型代码及对应的 Alembic 迁移脚本。
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from leo_skills.core.base_executor import BaseExecutor


class DatabaseModelGenerator(BaseExecutor):
    """数据库模型生成器 - 支持 SQLAlchemy 和 Peewee ORM"""

    def __init__(self, output_dir: str = ".", orm: str = "sqlalchemy") -> None:
        self.name = "database_model_generator_skill"
        self.output_dir = Path(output_dir)
        self.orm = orm.lower()

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
            generate - 生成模型代码（默认）
            save     - 生成并保存到磁盘

        参数（通过 context 或 kwargs 传入）:
            entity_name: str                - 实体名称（必填）
            fields: List[Dict]              - 字段定义列表（必填）
            relationships: List[Dict]       - 关系定义（可选）
            indexes: List[str]              - 索引字段列表（可选）
            orm: str                        - ORM 类型: sqlalchemy / peewee（可选）
            output_dir: str                 - 输出目录（可选）
        """
        params: Dict[str, Any] = dict(context or {})
        params.update(kwargs)

        if "output_dir" in params:
            self.output_dir = Path(params["output_dir"])
        if "orm" in params:
            self.orm = params["orm"].lower()

        if action == "generate":
            return self._action_generate(params)
        if action == "save":
            return self._action_save(params)

        return {"status": "error", "message": f"未知的 action: {action}"}

    # ------------------------------------------------------------------
    # action: generate
    # ------------------------------------------------------------------

    def _action_generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """生成模型代码并返回内容"""
        entity_name: str = params.get("entity_name", "")
        fields: List[Dict] = params.get("fields", [])
        relationships: List[Dict] = params.get("relationships", [])
        indexes: List[str] = params.get("indexes", [])

        if not entity_name:
            return {"status": "error", "message": "entity_name 参数不能为空"}
        if not fields:
            return {"status": "error", "message": "fields 参数不能为空"}

        result = self._generate(entity_name, fields, relationships, indexes)
        return {"status": "success", "action": "generate", "data": result}

    # ------------------------------------------------------------------
    # action: save
    # ------------------------------------------------------------------

    def _action_save(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """生成并保存模型文件"""
        entity_name: str = params.get("entity_name", "")
        fields: List[Dict] = params.get("fields", [])
        relationships: List[Dict] = params.get("relationships", [])
        indexes: List[str] = params.get("indexes", [])

        if not entity_name:
            return {"status": "error", "message": "entity_name 参数不能为空"}
        if not fields:
            return {"status": "error", "message": "fields 参数不能为空"}

        result = self._generate(entity_name, fields, relationships, indexes)
        saved = self._save_files(entity_name, result)
        return {
            "status": "success",
            "action": "save",
            "data": result,
            "saved_files": {k: str(v) for k, v in saved.items()},
        }

    # ------------------------------------------------------------------
    # 核心生成逻辑
    # ------------------------------------------------------------------

    def _generate(
        self,
        entity_name: str,
        fields: List[Dict],
        relationships: List[Dict],
        indexes: List[str],
    ) -> Dict[str, str]:
        """根据 ORM 类型生成模型代码"""
        results: Dict[str, str] = {}

        if self.orm == "sqlalchemy":
            results["model"] = self._generate_sqlalchemy_model(
                entity_name, fields, relationships, indexes
            )
            results["migration"] = self._generate_alembic_migration(
                entity_name, fields, indexes
            )
        else:
            results["model"] = self._generate_peewee_model(
                entity_name, fields, relationships
            )

        return results

    # ------------------------------------------------------------------
    # SQLAlchemy 模型生成
    # ------------------------------------------------------------------

    def _generate_sqlalchemy_model(
        self,
        entity_name: str,
        fields: List[Dict],
        relationships: List[Dict],
        indexes: List[str],
    ) -> str:
        """生成 SQLAlchemy 模型代码"""
        class_name = entity_name.capitalize()
        table_name = entity_name.lower() + "s"

        # 字段
        field_lines = [self._sqlalchemy_field(f) for f in fields]
        fields_str = "\n".join(field_lines)

        # 关系
        rel_lines = [
            self._sqlalchemy_relationship(r, class_name) for r in relationships
        ]
        rels_str = "\n".join(rel_lines) if rel_lines else ""

        # 索引
        index_lines = [
            f"    db.Index('ix_{table_name}_{idx}', '{idx}')," for idx in indexes
        ]
        indexes_str = "\n".join(index_lines) if index_lines else ""

        # to_dict 字段
        to_dict_fields = self._to_dict_str(fields)

        # 文档字符串中的字段说明
        docstring_fields = self._docstring_fields(fields)

        return f'''"""
{class_name} Model
==================
Generated by Leo Database Model Generator
"""
from datetime import datetime
from app import db


class {class_name}(db.Model):
    """
    {class_name}数据模型

    Attributes:
        id: 主键ID
{docstring_fields}
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = '{table_name}'

    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 字段
{fields_str}

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

{rels_str}
    # 索引
    __table_args__ = (
{indexes_str}
    )

    def to_dict(self) -> dict:
        """转换为字典"""
        return {{
            'id': self.id,
{to_dict_fields}
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }}

    @classmethod
    def from_dict(cls, data: dict) -> '{class_name}':
        """从字典创建实例"""
        return cls(**{{k: v for k, v in data.items() if hasattr(cls, k)}})

    def update_from_dict(self, data: dict) -> None:
        """从字典更新实例"""
        for key, value in data.items():
            if hasattr(self, key) and key not in ('id', 'created_at', 'updated_at'):
                setattr(self, key, value)

    def __repr__(self) -> str:
        return f'<{class_name} {{self.id}}>'
'''

    def _sqlalchemy_field(self, field: Dict) -> str:
        """生成单个 SQLAlchemy 字段定义"""
        name = field["name"]
        ftype = field.get("type", "string")
        required = field.get("required", False)
        unique = field.get("unique", False)
        default = field.get("default")
        max_length = field.get("max_length", 255)
        foreign_key = field.get("foreign_key")

        # 类型映射
        type_map = {
            "string": f"db.String({max_length})",
            "text": "db.Text",
            "integer": "db.Integer",
            "float": "db.Float",
            "boolean": "db.Boolean",
            "datetime": "db.DateTime",
            "date": "db.Date",
            "json": "db.JSON",
            "enum": f"db.Enum({', '.join(repr(v) for v in field.get('values', []))})",
        }
        col_type = type_map.get(ftype, "db.String(255)")

        parts = [f"db.Column({col_type}"]
        if foreign_key:
            parts.append(f", db.ForeignKey('{foreign_key}')")
        if unique:
            parts.append(", unique=True")
        parts.append(", nullable=False" if required else ", nullable=True")
        if default is not None:
            if isinstance(default, str):
                parts.append(f", default='{default}'")
            else:
                parts.append(f", default={default}")
        parts.append(")")

        return f"    {name} = {''.join(parts)}"

    def _sqlalchemy_relationship(self, rel: Dict, class_name: str) -> str:
        """生成 SQLAlchemy 关系定义"""
        name = rel["name"]
        rel_type = rel.get("type", "one_to_many")
        target = rel.get("target", class_name)
        back_ref = rel.get("back_ref", name)

        if rel_type == "self_referential":
            return f"    {name} = db.relationship('{class_name}', backref=db.backref('{back_ref}', remote_side=[id]))"
        elif rel_type == "one_to_many":
            return f"    {name} = db.relationship('{target}', backref='{back_ref}', lazy='dynamic')"
        elif rel_type == "many_to_many":
            return f"    {name} = db.relationship('{target}', secondary='{name}_association', backref='{back_ref}')"
        else:
            return f"    # {name}: {rel_type} relationship"

    # ------------------------------------------------------------------
    # Alembic 迁移脚本生成
    # ------------------------------------------------------------------

    def _generate_alembic_migration(
        self, entity_name: str, fields: List[Dict], indexes: List[str]
    ) -> str:
        """生成 Alembic 迁移脚本"""
        table_name = entity_name.lower() + "s"
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        col_lines = [self._migration_column(f) for f in fields]
        cols_str = ",\n        ".join(col_lines)

        idx_lines = [
            f"    op.create_index('ix_{table_name}_{idx}', '{table_name}', ['{idx}'])"
            for idx in indexes
        ]
        idx_str = "\n".join(idx_lines) if idx_lines else "    pass"

        return f'''"""
Create {entity_name} table

Revision ID: {timestamp}
Create Date: {datetime.now().isoformat()}
"""
from alembic import op
import sqlalchemy as sa

revision = '{timestamp}'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        '{table_name}',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        {cols_str},
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )

    # 创建索引
{idx_str}


def downgrade():
    op.drop_table('{table_name}')
'''

    def _migration_column(self, field: Dict) -> str:
        """生成迁移脚本中的列定义"""
        name = field["name"]
        ftype = field.get("type", "string")
        required = field.get("required", False)
        max_length = field.get("max_length", 255)

        type_map = {
            "string": f"sa.String({max_length})",
            "text": "sa.Text()",
            "integer": "sa.Integer()",
            "float": "sa.Float()",
            "boolean": "sa.Boolean()",
            "datetime": "sa.DateTime()",
            "json": "sa.JSON()",
        }
        col_type = type_map.get(ftype, "sa.String(255)")
        nullable = "False" if required else "True"

        return f"sa.Column('{name}', {col_type}, nullable={nullable})"

    # ------------------------------------------------------------------
    # Peewee 模型生成
    # ------------------------------------------------------------------

    def _generate_peewee_model(
        self,
        entity_name: str,
        fields: List[Dict],
        relationships: List[Dict],
    ) -> str:
        """生成 Peewee 模型代码"""
        class_name = entity_name.capitalize()
        field_lines = [self._peewee_field(f) for f in fields]
        fields_str = "\n".join(field_lines)

        return f'''"""
{class_name} Model (Peewee)
"""
from datetime import datetime
from peewee import *
from app import db


class {class_name}(Model):
    """
    {class_name}数据模型
    """
{fields_str}
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db
        table_name = '{entity_name.lower()}s'

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)
'''

    def _peewee_field(self, field: Dict) -> str:
        """生成单个 Peewee 字段定义"""
        name = field["name"]
        ftype = field.get("type", "string")
        required = field.get("required", False)
        default = field.get("default")
        max_length = field.get("max_length", 255)

        type_map = {
            "string": f"CharField(max_length={max_length}",
            "text": "TextField(",
            "integer": "IntegerField(",
            "float": "FloatField(",
            "boolean": "BooleanField(",
            "datetime": "DateTimeField(",
            "json": "JSONField(",
        }
        field_type = type_map.get(ftype, "CharField(")

        parts = [f"    {name} = {field_type}"]
        if not required:
            parts.append("null=True")
        if default is not None:
            if isinstance(default, str):
                parts.append(f"default='{default}'")
            else:
                parts.append(f"default={default}")

        return ", ".join(parts) + ")"

    # ------------------------------------------------------------------
    # 辅助方法
    # ------------------------------------------------------------------

    def _to_dict_str(self, fields: List[Dict]) -> str:
        """生成 to_dict 方法中的字段映射"""
        lines: List[str] = []
        for field in fields:
            name = field["name"]
            ftype = field.get("type", "string")
            if ftype == "datetime":
                lines.append(
                    f"            '{name}': self.{name}.isoformat() if self.{name} else None,"
                )
            else:
                lines.append(f"            '{name}': self.{name},")
        return "\n".join(lines)

    def _docstring_fields(self, fields: List[Dict]) -> str:
        """生成文档字符串中的字段说明"""
        lines: List[str] = []
        for field in fields:
            name = field["name"]
            ftype = field.get("type", "string")
            desc = field.get("description", name)
            lines.append(f"        {name}: {desc} ({ftype})")
        return "\n".join(lines)

    def _save_files(
        self, entity_name: str, results: Dict[str, str]
    ) -> Dict[str, Path]:
        """保存生成的文件到磁盘"""
        saved: Dict[str, Path] = {}

        # 保存模型
        models_dir = self.output_dir / "app" / "models"
        models_dir.mkdir(parents=True, exist_ok=True)
        model_path = models_dir / f"{entity_name.lower()}.py"
        model_path.write_text(results["model"], encoding="utf-8")
        saved["model"] = model_path

        # 保存迁移脚本
        if "migration" in results:
            migrations_dir = self.output_dir / "migrations" / "versions"
            migrations_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            migration_path = (
                migrations_dir / f"{timestamp}_create_{entity_name.lower()}.py"
            )
            migration_path.write_text(results["migration"], encoding="utf-8")
            saved["migration"] = migration_path

        return saved


__all__ = ["DatabaseModelGenerator"]
