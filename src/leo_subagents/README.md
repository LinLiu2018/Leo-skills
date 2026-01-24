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

- 调用content_layout_leo_skill进行内容排版
- 调用realestate_news_publisher_skill发布资讯
- 调用project_marketing_doc_generator_skill生成文档

**激活词**："执行任务"、"运行流程"

### 2. Research Agent（研究代理）

**职责**：信息收集、文献调研、知识整理

- 调用research_assistant_skill进行研究
- 整合多个信息源
- 生成研究报告

**激活词**："帮我研究"、"调研"

### 3. Analysis Agent（分析代理）

**职责**：数据分析、趋势分析、报告生成

- 处理结构化数据
- 生成分析报告
- 提供决策建议

**激活词**："分析数据"、"生成报告"

### 5. Architect Agent（架构设计代理）

**职责**：技术选型、系统设计、数据库设计

- 数据库模型设计
- API接口设计
- 技术架构选型

**激活词**："架构设计"、"技术选型"

### 6. Mobile Agent（移动开发代理）

**职责**：移动应用开发

- 小程序开发
- Flutter/React Native开发
- 移动端组件开发

**激活词**："小程序开发"、"移动开发"

### 7. Product Manager Agent（产品管理代理）

**职责**：需求分析、产品规划

- PRD编写
- 用户故事设计
- 竞品分析

**激活词**："分析需求"、"写PRD"

---

## 🔗 Skills桥接层

**技能适配器**（skills-bridge/skill_adapter.py）负责：

- 发现可用的Skills
- 加载Skill配置
- 调用Skill功能
- 返回结果标准化

---

## 🌊 Workflows 工作流

### 1. Analysis Pipeline (数据分析)

`leo_workflows.workflows.analysis_pipeline`

- 采集 -> 验证 -> 清洗 -> 并行分析 -> 报告

### 2. Content Pipeline (内容创作)

`leo_workflows.workflows.content_pipeline`

- 策划 -> 素材 -> 创作 -> 排版 -> 发布

### 3. Research Pipeline (研究调研)

`leo_workflows.workflows.research_pipeline`

- 搜集 -> 去重 -> 分类 -> 分析 -> 验证 -> 报告

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
from leo_subagents.agents import TaskAgent, ArchitectAgent

# 使用架构师代理
agent = ArchitectAgent(config)
result = agent.execute("设计用户系统数据库", design_type="database")
```

### 方式二：通过 Workflow 封装类（推荐）

```python
from leo_orchestrator.orchestrator import Orchestrator
from leo_workflows.workflows import content_pipeline

# 运行内容创作工作流
orchestrator = Orchestrator()
result = content_pipeline.run(orchestrator, {
    "topic": "AI发展趋势",
    "content_type": "article"
})
```

---

## 📊 与Skills的对应关系

| Subagent | 使用的Skills |
|----------|-------------|
| Task Agent | 所有工具框架Skills |
| Research Agent | research_assistant_skill, web_search_skill |
| Analysis Agent | data_analyzer_skill |
| Creative Agent | content_layout_leo_skill, article_to_prototype_skill |
| Architect Agent | database_model_generator_skill, api_doc_generator_skill |
| Mobile Agent | miniprogram-page/component/project-skills |
| Product Manager Agent | research_assistant_skill, web_search_skill |

---

## 🎯 发展路线图

### Phase 1（已完成）

- ✅ 基础架构搭建
- ✅ Skills桥接层实现
- ✅ 基础Subagents实现
- ✅ 项目结构优化

### Phase 2 (已完成)

- ✅ 三大核心Agent实现 (Architect, Mobile, PM)
- ✅ Agent配置和注册机制

### Phase 3 (已完成)

- ✅ 三大核心Workflow实现 (Analysis, Content, Research)
- ✅ Workflow Python封装层

### Phase 4（进行中）

- ⏳ 综合集成测试
- ⏳ 性能优化

---

**创建时间**：2026-01-08
**最后更新**：2026-01-08
**维护者**：Leo Liu
