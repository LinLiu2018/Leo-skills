# Leo Subagents - Subagent代理库

**Leo的Subagent代理集合** - 与Claude Skills协同工作的智能代理系统

---

## 🎯 设计理念

Subagents与Skills的关系：
- **Skills（技能）**：提供具体能力和功能
- **Subagents（代理）**：使用Skills完成复杂任务的执行者

```
┌─────────────┐
│  Orchestrator   │  ← 任务编排
└──────┬──────┘
       │
       ├─→ ┌─────────────┐
       │   │ Subagents   │  ← 任务执行
       │   └──────┬──────┘
       │          │
       └─→ ┌─────┴─────┐
           │  Skills    │  ← 能力提供
           └────────────┘
```

---

## 📁 目录结构

```
leo-subagents/
├── agents/                    # Subagent代理
│   ├── task-agent/           # 任务执行代理
│   ├── research-agent/       # 研究代理
│   ├── analysis-agent/       # 分析代理
│   └── creative-agent/       # 创作代理
├── skills-bridge/            # Skills桥接层
│   └── skill_adapter.py     # 技能适配器
├── config/                   # 配置文件
│   └── agents.yaml          # 代理配置
└── README.md                 # 本文档
```

---

## 🤖 Subagent类型

### 1. Task Agent（任务代理）
**职责**：执行具体任务，调用相关Skills
- 调用content-layout-leo-cskill进行内容排版
- 调用realestate-news-publisher-cskill发布资讯
- 调用project-marketing-doc-generator-cskill生成文档

**激活词**："执行任务"、"运行流程"

### 2. Research Agent（研究代理）
**职责**：信息收集、文献调研、知识整理
- 调用research-assistant-cskill进行研究
- 整合多个信息源
- 生成研究报告

**激活词**："帮我研究"、"调研"

### 3. Analysis Agent（分析代理）
**职责**：数据分析、趋势分析、报告生成
- 处理结构化数据
- 生成分析报告
- 提供决策建议

**激活词**："分析数据"、"生成报告"

### 4. Creative Agent（创作代理）
**职责**：内容创作、文案生成、创意输出
- 使用article-to-prototype-cskill
- 使用content-layout-leo-cskill
- 生成营销文案

**激活词**："创作内容"、"生成文案"

---

## 🔗 Skills桥接层

**技能适配器**（skills-bridge/skill_adapter.py）负责：
- 发现可用的Skills
- 加载Skill配置
- 调用Skill功能
- 返回结果标准化

---

## ⚙️ 配置文件

**config/agents.yaml**定义：
- 每个Subagent的能力
- 可调用的Skills列表
- 执行参数和优先级

---

## 🚀 使用方式

### 方式一：直接调用Subagent
```python
from leo_subagents.agents.task_agent import TaskAgent

agent = TaskAgent()
result = agent.execute("生成营销文档", project_info)
```

### 方式二：通过Orchestrator编排
```python
from leo_orchestrator.orchestrator import Orchestrator

orchestrator = Orchestrator()
result = orchestrator.run_workflow("content-pipeline")
```

---

## 📊 与Skills的对应关系

| Subagent | 使用的Skills |
|----------|-------------|
| Task Agent | 所有工具框架Skills |
| Research Agent | research-assistant-cskill |
| Analysis Agent | 待开发数据分析Skills |
| Creative Agent | content-layout-leo-cskill, article-to-prototype-cskill |

---

## 🎯 发展路线图

### Phase 1（当前）
- ✅ 基础架构搭建
- ⏳ Skills桥接层实现
- ⏳ 基础Subagents实现

### Phase 2（Q1 2026）
- ⏳ Workflow集成
- ⏳ Orchestrator实现
- ⏳ 实际业务场景测试

### Phase 3（Q2 2026）
- ⏳ 性能优化
- ⏳ 新Subagent开发
- ⏳ 多Agent协作

---

**创建时间**：2026-01-08
**最后更新**：2026-01-08
**维护者**：Leo Liu
