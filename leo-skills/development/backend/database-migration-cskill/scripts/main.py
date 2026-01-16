"""
数据库迁移脚本生成器 Skill
========================
生成数据库迁移脚本（支持Alembic/Flask-Migrate）
"""

from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class DatabaseMigrationGenerator:
    """数据库迁移脚本生成器"""

    def __init__(self, output_dir: str = "."):
        self.output_dir = Path(output_dir)

    def generate(
        self,
        changes_description: str,
        migration_type: str = "alembic",
        changes: List[Dict] = None
    ) -> Dict[str, str]:
        """
        生成数据库迁移脚本

        Args:
            changes_description: 变更描述
            migration_type: 迁移工具类型 (alembic/flask-migrate/raw)
            changes: 变更列表

        Returns:
            生成的迁移脚本字典
        """
        changes = changes or []

        if migration_type == 'alembic':
            return self._generate_alembic(changes_description, changes)
        elif migration_type == 'flask-migrate':
            return self._generate_flask_migrate(changes_description, changes)
        else:
            return self._generate_raw_sql(changes_description, changes)

    def _generate_alembic(self, description: str, changes: List[Dict]) -> Dict[str, str]:
        """生成Alembic迁移脚本"""
        revision_id = datetime.now().strftime('%Y%m%d%H%M%S')
        slug = description.lower().replace(' ', '_')[:30]

        upgrade_ops = []
        downgrade_ops = []

        for change in changes:
            op_type = change.get('type', 'add_column')
            table = change.get('table', '')
            column = change.get('column', '')
            column_type = change.get('column_type', 'String(255)')
            nullable = change.get('nullable', True)

            if op_type == 'add_column':
                upgrade_ops.append(
                    f"    op.add_column('{table}', sa.Column('{column}', sa.{column_type}, nullable={nullable}))"
                )
                downgrade_ops.append(
                    f"    op.drop_column('{table}', '{column}')"
                )
            elif op_type == 'drop_column':
                upgrade_ops.append(
                    f"    op.drop_column('{table}', '{column}')"
                )
                downgrade_ops.append(
                    f"    op.add_column('{table}', sa.Column('{column}', sa.{column_type}, nullable={nullable}))"
                )
            elif op_type == 'create_table':
                columns = change.get('columns', [])
                col_defs = []
                for col in columns:
                    col_name = col.get('name', 'id')
                    col_type = col.get('type', 'Integer')
                    col_nullable = col.get('nullable', True)
                    col_pk = col.get('primary_key', False)
                    if col_pk:
                        col_defs.append(f"        sa.Column('{col_name}', sa.{col_type}, primary_key=True)")
                    else:
                        col_defs.append(f"        sa.Column('{col_name}', sa.{col_type}, nullable={col_nullable})")
                cols_str = ',\n'.join(col_defs)
                upgrade_ops.append(
                    f"    op.create_table('{table}',\n{cols_str}\n    )"
                )
                downgrade_ops.append(
                    f"    op.drop_table('{table}')"
                )
            elif op_type == 'drop_table':
                upgrade_ops.append(
                    f"    op.drop_table('{table}')"
                )
                # downgrade需要重建表，这里简化处理
                downgrade_ops.append(
                    f"    # TODO: Recreate table '{table}'"
                )
            elif op_type == 'add_index':
                index_name = change.get('index_name', f'ix_{table}_{column}')
                upgrade_ops.append(
                    f"    op.create_index('{index_name}', '{table}', ['{column}'])"
                )
                downgrade_ops.append(
                    f"    op.drop_index('{index_name}', table_name='{table}')"
                )
            elif op_type == 'alter_column':
                new_type = change.get('new_type', column_type)
                upgrade_ops.append(
                    f"    op.alter_column('{table}', '{column}', type_=sa.{new_type})"
                )
                downgrade_ops.append(
                    f"    op.alter_column('{table}', '{column}', type_=sa.{column_type})"
                )

        upgrade_str = '\n'.join(upgrade_ops) if upgrade_ops else '    pass'
        downgrade_str = '\n'.join(downgrade_ops) if downgrade_ops else '    pass'

        migration_script = f'''"""\n{description}\n\nRevision ID: {revision_id}\nRevises: \nCreate Date: {datetime.now().isoformat()}\n\n"""\nfrom alembic import op\nimport sqlalchemy as sa\n\n\n# revision identifiers, used by Alembic.\nrevision = '{revision_id}'\ndown_revision = None\nbranch_labels = None\ndepends_on = None\n\n\ndef upgrade():\n    """Upgrade database schema."""\n{upgrade_str}\n\n\ndef downgrade():\n    """Downgrade database schema."""\n{downgrade_str}\n'''

        return {
            'migration': migration_script,
            'filename': f'{revision_id}_{slug}.py'
        }

    def _generate_flask_migrate(self, description: str, changes: List[Dict]) -> Dict[str, str]:
        """生成Flask-Migrate迁移脚本"""
        # Flask-Migrate本质上是Alembic的封装，格式相同
        result = self._generate_alembic(description, changes)

        # 添加Flask-Migrate特定的命令提示
        result['commands'] = '''# Flask-Migrate 命令\n# 初始化迁移目录（首次）\nflask db init\n\n# 生成迁移脚本\nflask db migrate -m "{description}"\n\n# 应用迁移\nflask db upgrade\n\n# 回滚迁移\nflask db downgrade\n'''

        return result

    def _generate_raw_sql(self, description: str, changes: List[Dict]) -> Dict[str, str]:
        """生成原始SQL迁移脚本"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

        upgrade_sql = []
        downgrade_sql = []

        for change in changes:
            op_type = change.get('type', 'add_column')
            table = change.get('table', '')
            column = change.get('column', '')
            column_type = change.get('column_type', 'VARCHAR(255)')
            nullable = change.get('nullable', True)
            null_str = 'NULL' if nullable else 'NOT NULL'

            if op_type == 'add_column':
                upgrade_sql.append(
                    f"ALTER TABLE {table} ADD COLUMN {column} {column_type} {null_str};"
                )
                downgrade_sql.append(
                    f"ALTER TABLE {table} DROP COLUMN {column};"
                )
            elif op_type == 'drop_column':
                upgrade_sql.append(
                    f"ALTER TABLE {table} DROP COLUMN {column};"
                )
                downgrade_sql.append(
                    f"ALTER TABLE {table} ADD COLUMN {column} {column_type} {null_str};"
                )
            elif op_type == 'create_table':
                columns = change.get('columns', [])
                col_defs = []
                for col in columns:
                    col_name = col.get('name', 'id')
                    col_type = col.get('type', 'INT')
                    col_nullable = 'NULL' if col.get('nullable', True) else 'NOT NULL'
                    col_pk = 'PRIMARY KEY' if col.get('primary_key', False) else ''
                    col_defs.append(f"    {col_name} {col_type} {col_nullable} {col_pk}".strip())
                cols_str = ',\n'.join(col_defs)
                upgrade_sql.append(
                    f"CREATE TABLE {table} (\n{cols_str}\n);"
                )
                downgrade_sql.append(
                    f"DROP TABLE IF EXISTS {table};"
                )
            elif op_type == 'add_index':
                index_name = change.get('index_name', f'ix_{table}_{column}')
                upgrade_sql.append(
                    f"CREATE INDEX {index_name} ON {table} ({column});"
                )
                downgrade_sql.append(
                    f"DROP INDEX {index_name};"
                )

        upgrade_script = f'''-- Migration: {description}\n-- Generated: {datetime.now().isoformat()}\n-- Direction: UP\n\n''' + '\n'.join(upgrade_sql)

        downgrade_script = f'''-- Migration: {description}\n-- Generated: {datetime.now().isoformat()}\n-- Direction: DOWN\n\n''' + '\n'.join(downgrade_sql)

        return {
            'upgrade': upgrade_script,
            'downgrade': downgrade_script,
            'upgrade_filename': f'{timestamp}_upgrade.sql',
            'downgrade_filename': f'{timestamp}_downgrade.sql'
        }

    def save_migration(self, results: Dict[str, str], migrations_dir: str = "migrations/versions") -> Dict[str, Path]:
        """保存迁移文件"""
        saved = {}
        migrations_path = self.output_dir / migrations_dir
        migrations_path.mkdir(parents=True, exist_ok=True)

        if 'migration' in results:
            filename = results.get('filename', 'migration.py')
            file_path = migrations_path / filename
            file_path.write_text(results['migration'], encoding='utf-8')
            saved['migration'] = file_path

        if 'upgrade' in results:
            filename = results.get('upgrade_filename', 'upgrade.sql')
            file_path = migrations_path / filename
            file_path.write_text(results['upgrade'], encoding='utf-8')
            saved['upgrade'] = file_path

        if 'downgrade' in results:
            filename = results.get('downgrade_filename', 'downgrade.sql')
            file_path = migrations_path / filename
            file_path.write_text(results['downgrade'], encoding='utf-8')
            saved['downgrade'] = file_path

        return saved


def main():
    """示例用法"""
    generator = DatabaseMigrationGenerator(output_dir="./output")

    # 示例变更
    changes = [
        {
            'type': 'create_table',
            'table': 'users',
            'columns': [
                {'name': 'id', 'type': 'Integer', 'primary_key': True},
                {'name': 'username', 'type': 'String(50)', 'nullable': False},
                {'name': 'email', 'type': 'String(120)', 'nullable': False},
                {'name': 'created_at', 'type': 'DateTime', 'nullable': True}
            ]
        },
        {
            'type': 'add_index',
            'table': 'users',
            'column': 'email',
            'index_name': 'ix_users_email'
        }
    ]

    results = generator.generate(
        changes_description='create users table',
        migration_type='alembic',
        changes=changes
    )

    print("生成完成！")
    print(f"文件名: {results.get('filename')}")
    print("\n=== 迁移脚本预览 ===")
    print(results['migration'][:500])


if __name__ == '__main__':
    main()
