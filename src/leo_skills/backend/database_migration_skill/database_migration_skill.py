"""
database_migration_skill - 数据库迁移技能

生成数据库迁移脚本，支持 Alembic、Flask-Migrate 和原始 SQL 三种格式。
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from leo_skills.core.base_executor import BaseExecutor


class DatabaseMigration(BaseExecutor):
    """数据库迁移脚本生成器 - 支持 Alembic / Flask-Migrate / 原始 SQL"""

    def __init__(self, output_dir: str = ".") -> None:
        self.name = "database_migration_skill"
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
            generate  - 生成迁移脚本（默认）
            save      - 生成并保存迁移文件到磁盘

        参数（通过 context 或 kwargs 传入）:
            changes_description: str        - 变更描述（必填）
            migration_type: str             - 迁移类型: alembic / flask-migrate / raw，默认 alembic
            changes: List[Dict]             - 变更列表
            output_dir: str                 - 输出目录（可选）
            migrations_dir: str             - 迁移文件子目录，默认 "migrations/versions"
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
        """生成迁移脚本并返回内容"""
        description: str = params.get("changes_description", "")
        migration_type: str = params.get("migration_type", "alembic")
        changes: List[Dict] = params.get("changes", [])

        if not description:
            return {"status": "error", "message": "changes_description 参数不能为空"}

        result = self._generate(description, migration_type, changes)
        return {"status": "success", "action": "generate", "data": result}

    # ------------------------------------------------------------------
    # action: save
    # ------------------------------------------------------------------

    def _action_save(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """生成并保存迁移文件"""
        description: str = params.get("changes_description", "")
        migration_type: str = params.get("migration_type", "alembic")
        changes: List[Dict] = params.get("changes", [])
        migrations_dir: str = params.get("migrations_dir", "migrations/versions")

        if not description:
            return {"status": "error", "message": "changes_description 参数不能为空"}

        result = self._generate(description, migration_type, changes)
        saved = self._save_migration(result, migrations_dir)
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
        description: str,
        migration_type: str,
        changes: List[Dict],
    ) -> Dict[str, str]:
        """根据类型分发生成逻辑"""
        if migration_type == "alembic":
            return self._generate_alembic(description, changes)
        elif migration_type == "flask-migrate":
            return self._generate_flask_migrate(description, changes)
        else:
            return self._generate_raw_sql(description, changes)

    # ------------------------------------------------------------------
    # Alembic 迁移脚本
    # ------------------------------------------------------------------

    def _generate_alembic(
        self, description: str, changes: List[Dict]
    ) -> Dict[str, str]:
        """生成 Alembic 迁移脚本"""
        revision_id = datetime.now().strftime("%Y%m%d%H%M%S")
        slug = description.lower().replace(" ", "_")[:30]

        upgrade_ops: List[str] = []
        downgrade_ops: List[str] = []

        for change in changes:
            op_type = change.get("type", "add_column")
            table = change.get("table", "")
            column = change.get("column", "")
            column_type = change.get("column_type", "String(255)")
            nullable = change.get("nullable", True)

            if op_type == "add_column":
                upgrade_ops.append(
                    f"    op.add_column('{table}', sa.Column('{column}', sa.{column_type}, nullable={nullable}))"
                )
                downgrade_ops.append(
                    f"    op.drop_column('{table}', '{column}')"
                )

            elif op_type == "drop_column":
                upgrade_ops.append(
                    f"    op.drop_column('{table}', '{column}')"
                )
                downgrade_ops.append(
                    f"    op.add_column('{table}', sa.Column('{column}', sa.{column_type}, nullable={nullable}))"
                )

            elif op_type == "create_table":
                columns = change.get("columns", [])
                col_defs: List[str] = []
                for col in columns:
                    col_name = col.get("name", "id")
                    col_type = col.get("type", "Integer")
                    col_nullable = col.get("nullable", True)
                    col_pk = col.get("primary_key", False)
                    if col_pk:
                        col_defs.append(
                            f"        sa.Column('{col_name}', sa.{col_type}, primary_key=True)"
                        )
                    else:
                        col_defs.append(
                            f"        sa.Column('{col_name}', sa.{col_type}, nullable={col_nullable})"
                        )
                cols_str = ",\n".join(col_defs)
                upgrade_ops.append(
                    f"    op.create_table('{table}',\n{cols_str}\n    )"
                )
                downgrade_ops.append(f"    op.drop_table('{table}')")

            elif op_type == "drop_table":
                upgrade_ops.append(f"    op.drop_table('{table}')")
                downgrade_ops.append(
                    f"    # TODO: Recreate table '{table}'"
                )

            elif op_type == "add_index":
                index_name = change.get("index_name", f"ix_{table}_{column}")
                upgrade_ops.append(
                    f"    op.create_index('{index_name}', '{table}', ['{column}'])"
                )
                downgrade_ops.append(
                    f"    op.drop_index('{index_name}', table_name='{table}')"
                )

            elif op_type == "alter_column":
                new_type = change.get("new_type", column_type)
                upgrade_ops.append(
                    f"    op.alter_column('{table}', '{column}', type_=sa.{new_type})"
                )
                downgrade_ops.append(
                    f"    op.alter_column('{table}', '{column}', type_=sa.{column_type})"
                )

        upgrade_str = "\n".join(upgrade_ops) if upgrade_ops else "    pass"
        downgrade_str = "\n".join(downgrade_ops) if downgrade_ops else "    pass"

        now_iso = datetime.now().isoformat()
        migration_script = (
            f'"""\n{description}\n\nRevision ID: {revision_id}\n'
            f"Revises: \nCreate Date: {now_iso}\n\n"
            f'"""\nfrom alembic import op\nimport sqlalchemy as sa\n\n\n'
            f"# revision identifiers, used by Alembic.\n"
            f"revision = '{revision_id}'\n"
            f"down_revision = None\nbranch_labels = None\ndepends_on = None\n\n\n"
            f'def upgrade():\n    """Upgrade database schema."""\n{upgrade_str}\n\n\n'
            f'def downgrade():\n    """Downgrade database schema."""\n{downgrade_str}\n'
        )

        return {
            "migration": migration_script,
            "filename": f"{revision_id}_{slug}.py",
        }

    # ------------------------------------------------------------------
    # Flask-Migrate（本质是 Alembic 的封装）
    # ------------------------------------------------------------------

    def _generate_flask_migrate(
        self, description: str, changes: List[Dict]
    ) -> Dict[str, str]:
        """生成 Flask-Migrate 迁移脚本"""
        result = self._generate_alembic(description, changes)
        result["commands"] = (
            "# Flask-Migrate 命令\n"
            "# 初始化迁移目录（首次）\n"
            "flask db init\n\n"
            f'# 生成迁移脚本\nflask db migrate -m "{description}"\n\n'
            "# 应用迁移\nflask db upgrade\n\n"
            "# 回滚迁移\nflask db downgrade\n"
        )
        return result

    # ------------------------------------------------------------------
    # 原始 SQL 迁移脚本
    # ------------------------------------------------------------------

    def _generate_raw_sql(
        self, description: str, changes: List[Dict]
    ) -> Dict[str, str]:
        """生成原始 SQL 迁移脚本"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        upgrade_sql: List[str] = []
        downgrade_sql: List[str] = []

        for change in changes:
            op_type = change.get("type", "add_column")
            table = change.get("table", "")
            column = change.get("column", "")
            column_type = change.get("column_type", "VARCHAR(255)")
            nullable = change.get("nullable", True)
            null_str = "NULL" if nullable else "NOT NULL"

            if op_type == "add_column":
                upgrade_sql.append(
                    f"ALTER TABLE {table} ADD COLUMN {column} {column_type} {null_str};"
                )
                downgrade_sql.append(
                    f"ALTER TABLE {table} DROP COLUMN {column};"
                )

            elif op_type == "drop_column":
                upgrade_sql.append(
                    f"ALTER TABLE {table} DROP COLUMN {column};"
                )
                downgrade_sql.append(
                    f"ALTER TABLE {table} ADD COLUMN {column} {column_type} {null_str};"
                )

            elif op_type == "create_table":
                columns = change.get("columns", [])
                col_defs: List[str] = []
                for col in columns:
                    col_name = col.get("name", "id")
                    col_type = col.get("type", "INT")
                    col_nullable = "NULL" if col.get("nullable", True) else "NOT NULL"
                    col_pk = "PRIMARY KEY" if col.get("primary_key", False) else ""
                    col_defs.append(
                        f"    {col_name} {col_type} {col_nullable} {col_pk}".strip()
                    )
                cols_str = ",\n".join(col_defs)
                upgrade_sql.append(
                    f"CREATE TABLE {table} (\n{cols_str}\n);"
                )
                downgrade_sql.append(f"DROP TABLE IF EXISTS {table};")

            elif op_type == "add_index":
                index_name = change.get("index_name", f"ix_{table}_{column}")
                upgrade_sql.append(
                    f"CREATE INDEX {index_name} ON {table} ({column});"
                )
                downgrade_sql.append(f"DROP INDEX {index_name};")

        now_iso = datetime.now().isoformat()
        upgrade_script = (
            f"-- Migration: {description}\n"
            f"-- Generated: {now_iso}\n"
            f"-- Direction: UP\n\n"
            + "\n".join(upgrade_sql)
        )
        downgrade_script = (
            f"-- Migration: {description}\n"
            f"-- Generated: {now_iso}\n"
            f"-- Direction: DOWN\n\n"
            + "\n".join(downgrade_sql)
        )

        return {
            "upgrade": upgrade_script,
            "downgrade": downgrade_script,
            "upgrade_filename": f"{timestamp}_upgrade.sql",
            "downgrade_filename": f"{timestamp}_downgrade.sql",
        }

    # ------------------------------------------------------------------
    # 文件保存
    # ------------------------------------------------------------------

    def _save_migration(
        self, results: Dict[str, str], migrations_dir: str = "migrations/versions"
    ) -> Dict[str, Path]:
        """将迁移脚本保存到磁盘"""
        saved: Dict[str, Path] = {}
        migrations_path = self.output_dir / migrations_dir
        migrations_path.mkdir(parents=True, exist_ok=True)

        if "migration" in results:
            filename = results.get("filename", "migration.py")
            file_path = migrations_path / filename
            file_path.write_text(results["migration"], encoding="utf-8")
            saved["migration"] = file_path

        if "upgrade" in results:
            filename = results.get("upgrade_filename", "upgrade.sql")
            file_path = migrations_path / filename
            file_path.write_text(results["upgrade"], encoding="utf-8")
            saved["upgrade"] = file_path

        if "downgrade" in results:
            filename = results.get("downgrade_filename", "downgrade.sql")
            file_path = migrations_path / filename
            file_path.write_text(results["downgrade"], encoding="utf-8")
            saved["downgrade"] = file_path

        return saved


__all__ = ["DatabaseMigration"]
