# OpenClaw Workspace 隔离配置

**创建时间**: 2026-02-27  
**目的**: 7 大业务板块独立 Workspace，实现完全隔离

---

## Workspace 规划

| 业务板块 | Workspace 路径 | Agents | Skills |
|----------|---------------|--------|--------|
| 房产经纪 | ~/.openclaw/workspace-realestate | villa, residential, commercial_sales, commercial_lease | web_search, summarize, memory_enhanced |
| 商业地产 | ~/.openclaw/workspace-commercial | commercial, investment | project_evaluation, investment_calculator |
| 贷款金融 | ~/.openclaw/workspace-loan | loan, bank_product | loan_calculator, credit_assessment, bank_product_db |
| 跨境电商 | ~/.openclaw/workspace-ecommerce | product, operation, logistics | competitor_scraper, logistics_calculator |
| AI 开发 | ~/.openclaw/workspace-dev | memory, self_improving, proactive | github_integration, skill_vetter |
| 内容创意 | ~/.openclaw/workspace-content | distribution | content_layout, video_monitor |
| 中央控制 | ~/.openclaw/workspace-main | task, research, analysis, creative | 核心系统 Skills |

---

## 配置示例

### openclaw.json

```json
{
  "agents": {
    "realestate": {
      "workspace": "~/.openclaw/workspace-realestate",
      "channels": ["feishu"],
      "skills": ["villa_agent", "residential_agent", "commercial_sales_agent", "commercial_lease_agent"],
      "model": "qwen3.5-plus"
    },
    "commercial": {
      "workspace": "~/.openclaw/workspace-commercial",
      "channels": ["feishu"],
      "skills": ["commercial_agent", "investment_agent"],
      "model": "qwen3.5-plus"
    },
    "loan": {
      "workspace": "~/.openclaw/workspace-loan",
      "channels": ["feishu"],
      "skills": ["loan_agent", "bank_product_agent"],
      "model": "qwen3.5-plus"
    },
    "ecommerce": {
      "workspace": "~/.openclaw/workspace-ecommerce",
      "channels": ["feishu"],
      "skills": ["product_agent", "operation_agent", "logistics_agent"],
      "model": "qwen3.5-plus"
    },
    "dev": {
      "workspace": "~/.openclaw/workspace-dev",
      "channels": ["feishu"],
      "skills": ["memory_agent", "self_improving_agent", "proactive_agent"],
      "model": "qwen3.5-plus"
    },
    "content": {
      "workspace": "~/.openclaw/workspace-content",
      "channels": ["feishu"],
      "skills": ["distribution_agent"],
      "model": "qwen3.5-plus"
    },
    "main": {
      "workspace": "~/.openclaw/workspace-main",
      "channels": ["feishu"],
      "skills": ["task_agent", "research_agent", "analysis_agent", "creative_agent"],
      "model": "qwen3.5-plus"
    }
  }
}
```

---

## 创建脚本

```bash
# 创建 Workspace 目录
mkdir -p ~/.openclaw/workspace-realestate
mkdir -p ~/.openclaw/workspace-commercial
mkdir -p ~/.openclaw/workspace-loan
mkdir -p ~/.openclaw/workspace-ecommerce
mkdir -p ~/.openclaw/workspace-dev
mkdir -p ~/.openclaw/workspace-content
mkdir -p ~/.openclaw/workspace-main

# 每个 Workspace 初始化基础文件
for ws in realestate commercial loan ecommerce dev content main; do
  mkdir -p ~/.openclaw/workspace-$ws/memory
  mkdir -p ~/.openclaw/workspace-$ws/sessions
  mkdir -p ~/.openclaw/workspace-$ws/config
done
```

---

## 验证

```bash
# 检查 Workspace 配置
openclaw config get agents

# 测试各 Workspace
openclaw agent --workspace ~/.openclaw/workspace-realestate --message "测试"
```

---

*配置完成时间：2026-02-27*
