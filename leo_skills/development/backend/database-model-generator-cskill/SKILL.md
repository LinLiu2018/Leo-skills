# 数据库模型生成器 Skill

## 技能描述

自动生成数据库模型代码，支持SQLAlchemy和Peewee ORM，包含模型定义、关系映射和迁移脚本。

## 激活词

- "生成数据库模型"
- "创建数据模型"
- "database model"
- "数据库表"

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| entity_name | string | 是 | 实体名称（如：User, Lead, Activity） |
| fields | list | 是 | 字段定义列表 |
| relationships | list | 否 | 关系定义（一对多、多对多等） |
| orm | string | 否 | ORM类型（sqlalchemy/peewee），默认sqlalchemy |
| indexes | list | 否 | 索引定义 |

## 字段类型支持

| 类型 | 说明 | SQLAlchemy | Peewee |
|------|------|------------|--------|
| string | 字符串 | String(n) | CharField |
| text | 长文本 | Text | TextField |
| integer | 整数 | Integer | IntegerField |
| float | 浮点数 | Float | FloatField |
| boolean | 布尔值 | Boolean | BooleanField |
| datetime | 日期时间 | DateTime | DateTimeField |
| json | JSON数据 | JSON | JSONField |

## 输出

- `models/{entity}.py` - 模型定义
- `migrations/xxx_create_{entity}.py` - 迁移脚本（可选）

## 使用示例

### 示例1：生成线索模型

```
生成数据库模型，实体名称：Lead
字段：
- name: 字符串，必填，最大100字符
- phone: 字符串，必填，最大20字符
- parent_id: 整数，可选，外键关联Lead
- status: 字符串，默认'new'
- depth: 整数，默认0
关系：
- parent: 自关联，多对一
- children: 自关联，一对多
```

### 示例2：生成活动模型

```
生成数据库模型，实体名称：Activity
字段：
- title: 字符串，必填
- description: 长文本
- start_time: 日期时间
- end_time: 日期时间
- config: JSON
- status: 字符串，枚举(draft/active/ended)
索引：
- status
- start_time
```

## 版本

- 版本: 1.0.0
- 作者: Leo Liu
- 更新: 2026-01-12
