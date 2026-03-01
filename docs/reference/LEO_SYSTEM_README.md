# Leo AI Agent System

**Leo的AI智能体系统** - Skills + Subagents 协同工作架构

---

## 🎯 系统概述

这是一个**统一的AI智能体系统**，将Claude Skills和Subagents有机结合，提供强大的自动化能力。

### 核心理念

```
┌─────────────────────────────────────────────────┐
│                  Leo Orchestrator               │
│              (统一编排器 - 大脑)                  │
└────────────┬────────────────────────────────────┘
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
┌──────────┐  ┌─────────────┐
│ Subagents│  │   Skills    │
│ (执行者)  │  │  (能力库)    │
└──────────┘  └─────────────┘
```

**Skills** = 能力提供者（做什么）
**Subagents** = 任务执行者（怎么做）
**Orchestrator** = 统一协调者（指挥）

---

## 📁 项目结构

```
leo_ai_system/
│
├── leo_skills/              # ✅ Skills能力库
│   ├── content_creation/    # 内容创作Skills
│   ├── tools/               # 工具框架Skills
│   ├── utilities/           # 工具Skills
│   ├── data_analysis/       # 数据分析Skills（待开发）
│   └── automation/          # 自动化Skills（待开发）
│
├── leo_subagents/           # 🆕 Subagents代理库
│   ├── agents/              # 各类Subagent
│   ├── skills_bridge/       # Skills桥接层
│   └── config/              # 配置文件
│
├── leo_orchestrator/        # 🆕 统一编排器
│   ├── registry.py          # 统一注册表
│   ├── api.py               # 统一API接口
│   └── coordinator/         # 协调器
│
├── projects/                # 🆕 实际项目源码
│   └── fission/             # 建华官员菜场小程序(裂变模块)
│
├── leo_workflows/           # 🆕 工作流定义
│   └── workflows/           # 预定义工作流
│
├── leo_config/              # 🆕 全局配置
│   └── settings/            # 配置文件
│
└── README.md                # 本文档
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install pyyaml
```

### 2. 自动发现并注册Skills

```python
from leo_orchestrator.api import leo

# 系统启动时自动发现所有Skills
# 无需手动配置！

# 查看已注册的内容
leo.stats()
```

### 3. 注册新的Skill

```python
# 方式1：使用API
leo.register(
    "skill",
    "my-new-skill",
    path="leo_skills/content-creation/my-new-skill",
    category="content-creation"
)

# 方式2：使用装饰器
from leo_orchestrator.registry import register_skill

@register_skill(
    name="my-skill",
    category="content-creation"
)
class MySkill:
    pass
```

### 4. 调用Skill执行任务

```python
# 直接调用Skill
result = leo.call(
    "content_layout_leo_skill",
    "layout",
    content="我的文章内容",
    style="data_driven"
)

# 使用Agent执行任务
result = leo.run_agent(
    "task-agent",
    "生成营销文档",
    project_info={"name": "菜市场项目"}
)

# 运行完整工作流
result = leo.run_workflow(
    "content-pipeline",
    topic="房地产市场分析"
)
```

---

## 📊 当前状态

### Skills（6个已注册）

| 分类 | Skills | 状态 |
|------|--------|------|
| 📝 内容创作 | content_layout_leo_skill | 🟢 |
| 📝 内容创作 | realestate_news_publisher_skill | 🟢 |
| 🔧 工具 | research_assistant_skill | 🟢 |
| 🛠️ 工具框架 | agent_skill_creator_skill | 🟢 |
| 🛠️ 工具框架 | article_to_prototype_skill | 🟢 |
| 🛠️ 工具框架 | project_marketing_doc_generator_skill | 🟢 |

### Subagents（4个已注册）

| Agent | 类型 | 状态 |
|-------|------|------|
| task-agent | 执行者 | 🟢 |
| research-agent | 研究者 | 🟢 |
| analysis-agent | 分析者 | 🟡 |
| creative-agent | 创作者 | 🟢 |

### Workflows（3个已定义）

| Workflow | 说明 | 状态 |
|----------|------|------|
| content-pipeline | 内容生产线 | 🟢 |
| research-pipeline | 研究线 | 🟢 |
| analysis-pipeline | 分析线 | 🟢 |

---

## 🎓 使用场景

### 场景1：内容创作与发布

```python
# 完整的内容生产线
leo.run_workflow(
    "content-pipeline",
    topic="2026年宁波房地产市场分析"
)

# 等价于：
# 1. research-agent 收集信息
# 2. creative-agent 创作内容
# 3. task-agent 排版并发布
```

### 场景2：项目营销文档生成

```python
# 使用专门的生成器
leo.run_agent(
    "task-agent",
    "生成菜市场项目营销手册",
    project_type="农贸市场"
)
```

### 场景3：研究与报告

```python
# 研究线
leo.run_workflow(
    "research-pipeline",
    query="AI眼镜市场趋势2026",
    depth=3
)
```

---

## 🔧 配置管理

### 全局配置文件

位置：`leo_config/settings/config.yaml`

```yaml
# Skills配置
skills:
  - name: "content_layout_leo_skill"
    enabled: true

# Subagents配置
agents:
  - name: "task-agent"
    type: "executor"
    priority: 1

# Workflows配置
workflows:
  content-pipeline:
    steps: [...]
```

### 动态配置

```python
# 禁用某个Skill
leo.disable("skill", "content_layout_leo_skill")

# 启用某个Skill
leo.enable("skill", "content_layout_leo_skill")

# 查询配置
skill = leo.get("skill", "content_layout_leo_skill")
print(skill.enabled)  # True/False
```

---

## 📖 API文档

### 查询API

```python
# 列出所有Skills
leo.list("skills")

# 按分类筛选
leo.list("skills", category="content-creation")

# 列出所有Agents
leo.list("agents")
```

### 注册API

```python
# 注册Skill
leo.register("skill", name, path, category, **metadata)

# 注册Agent
leo.register("agent", name, type, priority, skills, **metadata)
```

### 调用API

```python
# 调用Skill
leo.call(skill_name, action, **kwargs)

# 运行Agent
leo.run_agent(agent_name, task, **kwargs)

# 运行Workflow
leo.run_workflow(workflow_name, **kwargs)
```

---

## 🛠️ 开发指南

### 创建新Skill

1. 在`leo_skills/`对应分类下创建目录
2. 添加`SKILL.md`和`README.md`
3. 系统自动发现并注册

### 创建新Subagent

1. 在`leo-subagents/agents/`下创建新目录
2. 实现Agent类
3. 在配置文件中注册

### 创建新Workflow

1. 在`leo_workflows/workflows/`下创建定义
2. 配置步骤和Agent映射
3. 通过API调用

---

## 🎯 未来计划

- [ ] Q1 2026: 完善Skills桥接层
- [ ] Q1 2026: 实现Agent调用逻辑
- [ ] Q2 2026: 添加更多Workflows
- [ ] Q2 2026: 性能优化和缓存
- [ ] Q3 2026: Web界面
- [ ] Q3 2026: 分布式执行

---

## 📞 支持

**创建者**: Leo Liu
**GitHub**: [@LinLiu2018](https://github.com/LinLiu2018)
**文档**: [leo_skills](https://github.com/LinLiu2018/Leo-skills)

---

**最后更新**: 2026-01-08
**版本**: 1.0.0
