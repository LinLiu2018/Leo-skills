# Flask API Generator Skill

## 技能描述

自动生成Flask RESTful API代码，包括Blueprint、Models、Schemas和CRUD操作。

## 激活词

- "生成Flask API"
- "创建API接口"
- "生成后端接口"
- "flask api"

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| resource_name | string | 是 | 资源名称（如：user, lead, product） |
| fields | list | 是 | 字段定义列表 |
| endpoints | list | 否 | 自定义端点列表 |
| auth_required | bool | 否 | 是否需要认证，默认false |

## 输出

- `blueprints/{resource}_bp.py` - Flask Blueprint
- `models/{resource}.py` - SQLAlchemy Model
- `schemas/{resource}_schema.py` - Marshmallow Schema
- `services/{resource}_service.py` - 业务逻辑层

## 使用示例

### 示例1：生成线索管理API

```
生成Flask API，资源名称：lead
字段：
- name: 姓名，字符串，必填
- phone: 手机号，字符串，必填
- parent_id: 推荐人ID，整数，可选
- status: 状态，字符串，默认'new'
```

### 示例2：生成用户API

```
生成Flask API，资源名称：user
字段：
- username: 用户名，字符串，必填，唯一
- email: 邮箱，字符串，必填
- password_hash: 密码哈希，字符串，必填
需要认证
```

## 生成的代码结构

```
app/
├── blueprints/
│   └── lead_bp.py      # API路由
├── models/
│   └── lead.py         # 数据模型
├── schemas/
│   └── lead_schema.py  # 序列化
└── services/
    └── lead_service.py # 业务逻辑
```

## 技术栈

- Flask 2.x
- Flask-SQLAlchemy
- Flask-Marshmallow
- Flask-JWT-Extended (可选)

## 版本

- 版本: 1.0.0
- 作者: Leo Liu
- 更新: 2026-01-12
