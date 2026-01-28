# Subagent Creator Skill (代理创建器)

## 技能描述

**元技能 (Meta-Skill)** - 自动创建 Claude Subagent 的完整解决方案。

根据需求自动创建新的 Subagent，包括：
- Python 代码实现
- agents.yaml 配置
- Skill 绑定
- Workflow 集成

## 核心能力

- **需求分析**: 理解用户想要什么类型的 Agent
- **代码生成**: 自动生成 Agent Python 代码
- **配置生成**: 自动生成 agents.yaml 片段
- **技能绑定**: 自动绑定相关 Skills
- **注册集成**: 自动注册到系统

## 激活词

- "创建代理"
- "创建一个 agent"
- "开发新代理"
- "生成 subagent"
- "make me an agent"

## 使用方法

```python
from subagent_creator_skill import SubagentCreatorSkill

creator = SubagentCreatorSkill()

# 方式1: 从描述创建
result = creator.execute(
    action="create",
    agent_name="my_custom_agent",
    description="处理数据分析任务",
    agent_type="analyzer",
    skills=["data_analyzer_skill", "web_search_skill"]
)

# 方式2: 从模板创建
result = creator.execute(
    action="create_from_template",
    template="researcher",
    agent_name="advanced_researcher"
)

# 方式3: 分析需求并推荐
result = creator.execute(
    action="analyze_and_recommend",
    task_description="我需要一个人工智能新闻摘要助手"
)
```

## 创建流程

```
1. 需求分析
   ├─ 理解任务类型
   ├─ 推荐技能组合
   └─ 确定 Agent 类型

2. 代码生成
   ├─ 继承 BaseAgent
   ├─ 实现 can_handle()
   └─ 实现 execute()

3. 配置生成
   ├─ 生成 agents.yaml 片段
   ├─ 绑定 Skills
   └─ 设置优先级

4. 注册集成
   ├─ 更新 agents/__init__.py
   ├─ 注册到 AgentFactory
   └─ 测试可用性
```

## 配置文件

参考 `config/config.yaml`

## 进化机制

本技能支持自我进化能力：
- 根据创建经验优化代码模板
- 自动学习最佳技能组合
- 持续改进 Agent 架构设计
