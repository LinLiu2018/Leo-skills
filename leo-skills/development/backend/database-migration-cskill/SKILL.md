# 数据库迁移脚本生成器 Skill

## 技能描述

生成数据库迁移脚本，支持Alembic、Flask-Migrate和原始SQL格式。

## 激活词

- "生成迁移脚本"
- "数据库迁移"
- "数据库变更"

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| changes_description | string | 是 | 变更描述 |
| migration_type | string | 否 | 迁移类型(alembic/flask-migrate/raw) |
| changes | list | 否 | 变更列表 |

## 支持的变更类型

- add_column: 添加列
- drop_column: 删除列
- create_table: 创建表
- drop_table: 删除表
- add_index: 添加索引
- alter_column: 修改列类型

## 输出

- Alembic/Flask-Migrate: Python迁移脚本
- Raw: SQL升级和降级脚本

## 版本

- 版本: 1.0.0
- 作者: Leo Liu
