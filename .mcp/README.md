# OpenClaw + Leo MCP 集成指南

> 创建时间: 2026-02-03
> 作者: Leo AI System

---

## 🎯 概述

本指南描述如何将 Leo AI System 的所有能力通过 MCP (Model Context Protocol) 暴露给 OpenClaw，实现：

- ✅ **能力共享**: 在 VSCode 和飞书中使用同一套工具
- ✅ **自动同步**: 在 VSCode 开发的新 Skill/Agent 自动对 OpenClaw 可用
- ✅ **无需 API Key**: 本地进程通信，无需配置外部 API

---

## 🏗️ 架构

```
┌─────────────────────────────────────────────────────────────┐
│                     你的使用场景                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   VSCode + Claude Code                    飞书 + OpenClaw   │
│        │                                         │          │
│        │                                         │          │
│        ▼                                         ▼          │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              Leo AI System (Python)                 │   │
│   │                                                     │   │
│   │   Skills (46)  Agents (14)  Workflows (8)          │   │
│   │         │              │            │                │   │
│   └─────────┼──────────────┼────────────┼────────────────┘   │
│             │              │            │                     │
│             ▼              ▼            ▼                     │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              Leo MCP Server                         │   │
│   │              (.mcp/leo_mcp_server.py)               │   │
│   └────────────────────────┬────────────────────────────┘   │
│                            │                                 │
│                   MCP Protocol                               │
│                            │                                 │
│   ┌────────────────────────┼────────────────────────────┐   │
│   │              OpenClaw (Node.js)                     │   │
│   │              (通过 MCP 连接)                         │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 文件结构

```
leo_ai_system/
│
├── .mcp/
│   ├── leo_mcp_server.py      # ⭐ MCP Server 主程序
│   ├── capabilities.md        # 能力清单文档
│   ├── test_server.py         # 测试脚本
│   └── README.md              # 本文档
│
├── .mcp.json                  # MCP 配置（VSCode 用）
│
├── leo_config/
│   └── settings/
│       └── config.yaml        # Skills/Agents/Worflows 配置
│
├── leo_skills/                # 46 个 Skills
├── leo_subagents/             # 14 个 Agents
└── leo_workflows/             # 8 个 Workflows
```

---

## 🚀 快速开始

### 1. 测试 MCP Server

```bash
cd D:\桌面\leo_ai_system\.mcp
python test_server.py
```

预期输出:
```
🧪 测试 Leo MCP Server
...
🎉 所有测试通过！
```

### 2. 手动测试 MCP Server

```bash
cd D:\桌面\leo_ai_system\.mcp
python leo_mcp_server.py
```

Server 启动后，会监听标准输入的 JSON-RPC 请求。

### 3. 配置 OpenClaw 使用 Leo MCP

编辑 `C:\Users\刘方林\.openclaw\openclaw.json`:

```json
{
  "mcp": {
    "servers": {
      "leo-system": {
        "command": "python",
        "args": ["D:/桌面/leo_ai_system/.mcp/leo_mcp_server.py"],
        "env": {
          "PYTHONPATH": "D:/桌面/leo_ai_system/src",
          "PYTHONIOENCODING": "utf-8"
        }
      }
    }
  }
}
```

---

## 📋 可用工具

MCP Server 暴露以下工具:

### Skills (46 个)

| 工具名 | 描述 |
|--------|------|
| `leo_skill_content_layout_leo_skill` | 专业内容排版 |
| `leo_skill_realestate_news_publisher_skill` | 房产新闻发布 |
| `leo_skill_research_assistant_skill` | 研究助手 |
| `leo_skill_web_search_skill` | 网络搜索 |
| `leo_skill_data_analyzer_skill` | 数据分析 |
| ... | ... |

### Agents (14 个)

| 工具名 | 优先级 | 描述 |
|--------|--------|------|
| `leo_agent_realestate_agent` | 5 | ⭐ **房产市场分析** |
| `leo_agent_research_agent` | 2 | 市场调研 |
| `leo_agent_creative_agent` | 4 | 内容创作 |
| `leo_agent_analysis_agent` | 3 | 数据分析 |
| `leo_agent_task_agent` | 1 | 通用任务 |
| ... | ... |

### Workflows (8 个)

| 工具名 | 描述 |
|--------|------|
| `leo_workflow_realestate_pipeline` | ⭐ **房产市场情报工作流** |
| `leo_workflow_content_pipeline` | 内容创作工作流 |
| `leo_workflow_research_pipeline` | 研究工作流 |
| `leo_workflow_analysis_pipeline` | 分析工作流 |
| ... | ... |

---

## 💡 使用示例

### 示例 1: 分析宁波房产市场

在飞书中发送:
```
分析宁波房产市场情况
```

OpenClaw 会:
1. 接收消息
2. 通过 MCP 调用 `leo_agent_realestate_agent`
3. 执行分析
4. 返回结果到飞书

### 示例 2: 搜索网络信息

在飞书中发送:
```
搜索最新的房地产政策
```

OpenClaw 会:
1. 接收消息
2. 通过 MCP 调用 `leo_skill_web_search_skill`
3. 执行搜索
4. 返回结果到飞书

### 示例 3: 执行完整工作流

在飞书中发送:
```
生成宁波房产市场日报
```

OpenClaw 会:
1. 接收消息
2. 通过 MCP 调用 `leo_workflow_realestate_pipeline`
3. 执行完整工作流
4. 返回结果到飞书

---

## 🔧 常见问题

### Q1: MCP Server 启动失败？

检查:
```bash
# 测试 Python 导入
python -c "import sys; sys.path.insert(0, 'src'); from leo_orchestrator.registry import get_registry; r=get_registry(); print('OK')"
```

### Q2: 工具调用超时？

增大超时设置，或检查 Leo System 是否正常。

### Q3: 中文显示乱码？

确保设置了环境变量:
```bash
set PYTHONIOENCODING=utf-8
```

---

## 🎯 后续计划

- [ ] 完善 Skill 执行逻辑
- [ ] 实现 Agent 详细调用
- [ ] 添加 Workflow 编排支持
- [ ] 集成到 OpenClaw Agent Prompt
- [ ] 自动化测试和监控

---

## 📚 相关文档

- [Leo System 能力清单](./capabilities.md)
- [OpenClaw 文档](https://docs.openclaw.ai)
- [MCP Protocol](https://modelcontextprotocol.io)

---

**维护者**: Leo AI System
**最后更新**: 2026-02-03
