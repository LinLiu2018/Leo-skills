# Leo AI System API 参考

## 概述

Leo AI System 提供 RESTful API，支持以下功能：
- Skills 管理与执行
- Agents 管理与运行
- Workflows 管理与执行
- 记忆系统操作
- 意图识别与路由

## 基础信息

| 项目 | 值 |
|------|-----|
| 基础 URL | `http://localhost:8000` |
| API 版本 | v2.0.0 |
| 认证方式 | Token (Header) |

## 认证

### 请求头

```http
Authorization: Bearer <token>
```

### 权限角色

| 角色 | 权限 |
|------|------|
| admin | read, write, execute, admin |
| operator | read, write, execute |
| executor | read, execute |
| viewer | read |

## API 端点

### 系统

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/` | 根端点 |
| GET | `/api/system/stats` | 系统统计 |
| GET | `/api/system/health` | 健康检查 |
| POST | `/api/system/reload` | 重载系统 |

### Skills

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/skills` | 获取所有 Skills |
| GET | `/api/skills/{skill_id}` | 获取单个 Skill |
| POST | `/api/skills/{skill_id}/execute` | 执行 Skill |
| GET | `/api/skills/{skill_id}/methods` | 获取 Skill 方法 |

### Agents

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/agents` | 获取所有 Agents |
| GET | `/api/agents/{agent_id}` | 获取单个 Agent |
| POST | `/api/agents/{agent_id}/execute` | 执行 Agent |

### Workflows

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/workflows` | 获取所有 Workflows |
| GET | `/api/workflows/{workflow_id}` | 获取单个 Workflow |
| POST | `/api/workflows/{workflow_id}/execute` | 执行 Workflow |
| POST | `/api/workflows/validate` | 验证 Workflow |

### 记忆系统

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/memory` | 获取记忆列表 |
| GET | `/api/memory/search` | 搜索记忆 |
| GET | `/api/memory/stats` | 记忆统计 |
| POST | `/api/memory` | 创建记忆 |

### 意图识别

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/intent/recognize` | 识别意图 |
| POST | `/api/intent/route` | 路由请求 |
| POST | `/api/intent/test` | 测试意图 |

## 请求/响应示例

### 执行 Skill

**请求**:
```bash
curl -X POST http://localhost:8000/api/skills/content_layout_leo_skill/execute \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"action": "layout", "content": "测试内容", "style": "data_driven"}'
```

**响应**:
```json
{
  "success": true,
  "data": {
    "result": "排版后的内容..."
  },
  "error": null
}
```

### 获取 Skills 列表

**请求**:
```bash
curl -X GET http://localhost:8000/api/skills \
  -H "Authorization: Bearer <token>"
```

**响应**:
```json
{
  "success": true,
  "data": {
    "skills": [
      {
        "name": "content_layout_leo_skill",
        "category": "content-creation",
        "enabled": true
      }
    ]
  }
}
```

## OpenAPI 文档

完整的 OpenAPI 规范可在以下地址获取：
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`
