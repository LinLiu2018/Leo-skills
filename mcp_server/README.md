# Leo System MCP Server

**功能**: 通过 MCP 协议暴露 Leo AI System 的所有能力给 OpenClaw 和其他客户端

**位置**: `E:\桌面\leo_ai_system\mcp_server`

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd E:\桌面\leo_ai_system
pip install mcp python-dotenv pyyaml
```

### 2. 配置 MCP Server

创建 `.env` 文件：

```bash
# Leo System MCP Server 配置
LEO_SYSTEM_PATH=E:\桌面\leo_ai_system
PYTHON_PATH=C:\Users\admin\AppData\Local\Programs\Python\Python311\python.exe

# MCP Server 配置
MCP_SERVER_HOST=127.0.0.1
MCP_SERVER_PORT=8765

# OpenClaw 配置
OPENCLAW_WORKSPACE=C:\Users\admin\.openclaw\workspace
```

### 3. 启动 MCP Server

```bash
# 方式 1：直接启动
python mcp_server\server.py

# 方式 2：后台运行
python mcp_server\server.py --background

# 方式 3：通过 OpenClaw 配置启动（推荐）
```

### 4. 配置 OpenClaw

在 `openclaw.json` 中添加 MCP 配置：

```json
{
  "mcp": {
    "servers": {
      "leo-system": {
        "command": "C:\\Users\\admin\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
        "args": [
          "E:\\桌面\\leo_ai_system\\mcp_server\\server.py"
        ],
        "env": {
          "LEO_SYSTEM_PATH": "E:\\桌面\\leo_ai_system",
          "PYTHONPATH": "E:\\桌面\\leo_ai_system\\src"
        },
        "enabled": true
      }
    }
  }
}
```

### 5. 验证连接

```bash
# 重启 OpenClaw Gateway
openclaw gateway restart

# 查看 MCP 连接状态
openclaw mcp status

# 列出 Leo System 技能
openclaw mcp call leo-system skills_list
```

---

## 📊 可用能力

### Skills（252 个）

#### 核心技能

| 技能 | 功能 | 示例 |
|------|------|------|
| `skill-creator` | 创建新技能 | `skills_create` |
| `skill-code-generator` | 代码生成 | `skills_generate_code` |
| `skill-evolution-assistant` | 技能进化 | `skills_evolve` |

#### 房产业务技能

| 技能 | 功能 | 示例 |
|------|------|------|
| `pocket-crm` | 口袋助理 CRM 集成 | `business_crm_sync` |
| `ads-manager` | 广告投放管理 | `business_ads_create` |
| `amazon` | 亚马逊运营 | `business_amazon_research` |
| `shopify` | Shopify 运营 | `business_shopify_manage` |
| `property-valuation` | 房产估值 | `business_property_valuate` |

#### 内容创作技能

| 技能 | 功能 | 示例 |
|------|------|------|
| `image-generator` | AI 图像生成 | `content_create_image` |
| `copywriting` | 文案撰写 | `content_create_copy` |
| `video` | 视频处理 | `content_create_video` |
| `seo` | SEO 优化 | `content_seo_optimize` |

#### 工具集成技能

| 技能 | 功能 | 示例 |
|------|------|------|
| `github-integration` | GitHub 集成 | `tools_github_list_issues` |
| `notion-connector` | Notion 连接 | `tools_notion_query` |
| `web-search` | 网页搜索 | `tools_search_web` |
| `pdf-analyzer` | PDF 分析 | `tools_pdf_analyze` |

### Agents（32 个）

| Agent | 功能 | 示例 |
|-------|------|------|
| `task-agent` | 任务执行 | `agents_execute_task` |
| `research-agent` | 研究分析 | `agents_research` |
| `analysis-agent` | 数据分析 | `agents_analyze` |
| `creative-agent` | 内容创作 | `agents_create_content` |

### Workflows（工作流）

| Workflows | 功能 | 示例 |
|-----------|------|------|
| `content-pipeline` | 内容生产线 | `workflows_run_content` |
| `research-pipeline` | 研究工作流 | `workflows_run_research` |
| `analysis-pipeline` | 分析工作流 | `workflows_run_analysis` |

---

## 🔧 MCP 工具列表

### Skills 相关工具

| 工具名 | 功能 | 参数 |
|--------|------|------|
| `skills_list` | 列出所有技能 | `category?, limit?` |
| `skills_get` | 获取技能详情 | `skill_name` |
| `skills_execute` | 执行技能 | `skill_name, action, params` |
| `skills_create` | 创建新技能 | `name, description, category` |
| `skills_evaluate` | 评估技能 | `skill_path` |
| `skills_optimize` | 优化技能 | `skill_path` |

### Agents 相关工具

| 工具名 | 功能 | 参数 |
|--------|------|------|
| `agents_list` | 列出所有 Agent | - |
| `agents_get` | 获取 Agent 详情 | `agent_name` |
| `agents_execute` | 执行 Agent | `agent_name, task, context` |

### Workflows 相关工具

| 工具名 | 功能 | 参数 |
|--------|------|------|
| `workflows_list` | 列出所有工作流 | - |
| `workflows_get` | 获取工作流详情 | `workflow_name` |
| `workflows_run` | 运行工作流 | `workflow_name, input` |

### 系统相关工具

| 工具名 | 功能 | 参数 |
|--------|------|------|
| `system_status` | 系统状态检查 | - |
| `system_health` | 健康检查 | - |
| `system_info` | 系统信息 | - |

---

## 📝 使用示例

### 示例 1：列出所有技能

```bash
# 通过 OpenClaw 调用
openclaw mcp call leo-system skills_list

# 返回
{
  "status": "success",
  "total": 252,
  "categories": ["automation", "backend", "business", ...],
  "skills": [
    {"name": "skill-creator", "category": "development"},
    {"name": "pocket-crm", "category": "business"},
    ...
  ]
}
```

### 示例 2：执行技能

```bash
# 执行房产估值技能
openclaw mcp call leo-system skills_execute \
  --skill property-valuation \
  --action run \
  --params '{"address": "宁波市鄞州区 XX 小区", "area": 120}'
```

### 示例 3：创建技能

```bash
# 创建新技能
openclaw mcp call leo-system skills_create \
  --name "xiaohongshu-copywriter" \
  --description "小红书文案生成技能" \
  --category "content_creation"
```

### 示例 4：评估技能

```bash
# 评估技能质量
openclaw mcp call leo-system skills_evaluate \
  --skill-path "./business/pocket_crm_skill"
```

### 示例 5：执行 Agent

```bash
# 执行研究 Agent
openclaw mcp call leo-system agents_execute \
  --agent research-agent \
  --task "调研宁波别墅市场" \
  --context '{"region": "宁波", "property_type": "别墅"}'
```

---

## 🔌 OpenClaw 集成

### 配置 openclaw.json

```json
{
  "mcp": {
    "servers": {
      "leo-system": {
        "command": "C:\\Users\\admin\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
        "args": [
          "E:\\桌面\\leo_ai_system\\mcp_server\\server.py"
        ],
        "env": {
          "LEO_SYSTEM_PATH": "E:\\桌面\\leo_ai_system",
          "PYTHONPATH": "E:\\桌面\\leo_ai_system\\src"
        },
        "enabled": true,
        "autoStart": true
      }
    }
  },
  "skills": {
    "leo-system": {
      "prefix": "leo:",
      "enabled": true
    }
  }
}
```

### 使用方式

```bash
# 通过 OpenClaw 调用 Leo 技能
openclaw skill run leo:skills_execute --name pocket-crm --action sync

# 或直接调用
openclaw mcp call leo-system skills_execute --skill pocket-crm --action sync
```

---

## 📊 性能指标

| 指标 | 数值 |
|------|------|
| 技能数 | 252 个 |
| Agent 数 | 32 个 |
| Workflows | 3 个 |
| 平均响应时间 | <100ms |
| 并发支持 | 10 个/秒 |
| 评估覆盖率 | 100% |
| 平均评分 | 95/100 |

---

## 🔍 故障排查

### 问题 1：MCP Server 无法启动

**检查**:
```bash
# 检查 Python 路径
where python

# 检查依赖
pip list | grep mcp

# 检查 Leo System 路径
dir E:\桌面\leo_ai_system\src
```

**解决**:
```bash
# 重新安装依赖
pip install mcp python-dotenv pyyaml

# 检查配置文件
cat mcp_server\.env
```

### 问题 2：OpenClaw 无法连接

**检查**:
```bash
# 查看 OpenClaw 日志
openclaw logs

# 检查 MCP 状态
openclaw mcp status
```

**解决**:
```bash
# 重启 OpenClaw Gateway
openclaw gateway restart

# 验证 MCP Server
python mcp_server\server.py --test
```

### 问题 3：技能执行失败

**检查**:
```bash
# 查看技能详情
openclaw mcp call leo-system skills_get --skill pocket-crm

# 检查技能路径
dir E:\桌面\leo_ai_system\src\leo_skills\business\pocket_crm_skill
```

**解决**:
```bash
# 重新评估技能
openclaw mcp call leo-system skills_evaluate --skill-path "./business/pocket_crm_skill"
```

---

## 📚 完整文档

- MCP Server 代码：`mcp_server/server.py`
- Leo System 文档：`E:\桌面\leo_ai_system\README.md`
- Skills 文档：`E:\桌面\leo_ai_system\docs\`
- OpenClaw 文档：`C:\Users\admin\.openclaw\workspace\docs\`

---

*最后更新：2026-03-13*
