# Leo AI Agent System - 下一步工作清单

> 创建时间：2026-01-23
> 当前分支：refactor/standardize-structure
> 状态：目录重命名已完成，准备实现新功能

---

## 📋 待完成任务

### 第一优先级：实现 3 个新 Agent

#### 1. Architect Agent（架构设计代理）

**文件位置**：

- 主文件：`leo_subagents/agents/architect_agent/architect_agent.py`
- 文档：`leo_subagents/agents/architect_agent/AGENT.md`（已存在）
- 配置：`leo_subagents/config/agents.yaml`

**功能需求**：

- 系统架构设计
- 技术选型建议
- 数据库模型设计
- API 接口设计
- 技术文档编写

**关联 Skills**：

- research-assistant-cskill（技术调研）
- data-analyzer-cskill（数据建模）
- project-marketing-doc-generator-cskill（文档生成）

**激活关键词**：

- 架构设计、技术选型、系统设计、数据库设计、API设计

**实现参考**：

- 参考现有 Agent：`leo_subagents/agents/research_agent/research_agent.py`
- 基类：`leo_subagents/agents/base_agent.py`

---

#### 2. Mobile Agent（移动开发代理）

**文件位置**：

- 主文件：`leo_subagents/agents/mobile_agent/mobile_agent.py`
- 文档：`leo_subagents/agents/mobile_agent/AGENT.md`（已存在）
- 配置：`leo_subagents/config/agents.yaml`

**功能需求**：

- 微信小程序开发
- React Native 应用开发
- Flutter 应用开发
- 移动端 UI 组件开发
- 跨平台适配

**关联 Skills**：

- miniprogram-page-generator-cskill
- miniprogram-component-generator-cskill
- miniprogram-project-scaffold-cskill

**激活关键词**：

- 小程序、移动、React Native、Flutter、微信、移动端、跨平台、app

---

#### 3. Product Manager Agent（产品管理代理）

**文件位置**：

- 主文件：`leo_subagents/agents/product_manager_agent/product_manager_agent.py`
- 文档：`leo_subagents/agents/product_manager_agent/AGENT.md`（已存在）
- 配置：`leo_subagents/config/agents.yaml`

**功能需求**：

- 需求分析
- 产品规划
- 用户故事编写
- 功能优先级排序
- 产品文档生成

**关联 Skills**：

- research-assistant-cskill（市场调研）
- project-marketing-doc-generator-cskill（文档生成）
- data-analyzer-cskill（数据分析）

**激活关键词**：

- 需求分析、产品规划、用户故事、功能设计、产品文档

---

### 第二优先级：实现 3 个工作流

#### 1. Analysis Pipeline（数据分析工作流）

**文件位置**：

- 配置文件：`leo_workflows/workflows/analysis-pipeline/workflow.yaml`
- 说明文档：`leo_workflows/workflows/analysis-pipeline/README.md`（已存在）

**工作流步骤**：

1. 数据采集（research-agent）
2. 数据验证（条件分支）
3. 数据清洗（analysis-agent）
4. 并行分析（统计分析、趋势分析、相关性分析）
5. 结果汇总（analysis-agent）
6. 报告生成（task-agent）

**配置示例**：

```yaml
name: "data-analysis-pipeline"
description: "完整的数据分析工作流：采集→清洗→分析→报告"
enabled: true
steps:
  - name: "data_collection"
    agent: "research-agent"
    description: "从多个数据源采集数据"
  # ... 其他步骤
```

---

#### 2. Content Pipeline（内容创作工作流）

**文件位置**：

- 配置文件：`leo_workflows/workflows/content-pipeline/workflow.yaml`
- 说明文档：`leo_workflows/workflows/content-pipeline/README.md`（已存在）

**工作流步骤**：

1. 内容策划（research-agent）
2. 素材收集（并行：文字、数据、参考案例）
3. 内容创作（creative-agent）
4. 内容排版（task-agent）
5. 去AI化处理（creative-agent）
6. 质量检查（条件分支）
7. 内容发布（task-agent）

**集成 Skills**：

- content-layout-leo-cskill（智能排版）
- realestate-news-publisher-cskill（房产资讯发布）

---

#### 3. Research Pipeline（研究调研工作流）

**文件位置**：

- 配置文件：`leo_workflows/workflows/research-pipeline/workflow.yaml`
- 说明文档：`leo_workflows/workflows/research-pipeline/README.md`（已存在）

**工作流步骤**：

1. 多源信息搜集（并行：网络、数据库、文档）
2. 信息去重（research-agent）
3. 资料分类整理（research-agent）
4. 信息质量评估（条件分支）
5. 补充搜索（如果需要）
6. 深度分析（analysis-agent）
7. 交叉验证（analysis-agent）
8. 研究报告生成（creative-agent）
9. 同步到知识库（task-agent）

**集成 Skills**：

- research-assistant-cskill（研究助手）
- web-search-cskill（网页搜索）
- obsidian-sync-cskill（Obsidian 同步）

---

## 🔧 实现指南

### Agent 实现步骤

1. **创建 Agent 文件**

   ```bash
   # 文件路径示例
   leo_subagents/agents/architect_agent/architect_agent.py
   ```

2. **继承 BaseAgent 类**

   ```python
   from leo_subagents.agents.base_agent import BaseAgent, AgentConfig, AgentFactory

   class ArchitectAgent(BaseAgent):
       ACTIVATION_KEYWORDS = ["架构", "设计", ...]

       def __init__(self, config: AgentConfig):
           super().__init__(config)
           self.capabilities = {...}

       def can_handle(self, task: str) -> float:
           # 判断是否能处理任务
           pass

       def execute(self, task: str, **kwargs) -> Dict[str, Any]:
           # 执行任务
           pass
   ```

3. **注册到 AgentFactory**

   ```python
   AgentFactory.register_agent_class("designer", ArchitectAgent)
   ```

4. **更新 agents.yaml 配置**

   ```yaml
   architect-agent:
     name: "Architect Agent"
     type: "designer"
     priority: 2
     skills: [...]
   ```

5. **测试 Agent**

   ```bash
   python leo_system.py
   # 验证 Agent 是否成功注册
   ```

---

### 工作流实现步骤

1. **创建 workflow.yaml 文件**

   ```bash
   # 文件路径示例
   leo_workflows/workflows/analysis-pipeline/workflow.yaml
   ```

2. **定义工作流配置**

   ```yaml
   name: "workflow-name"
   description: "工作流描述"
   enabled: true
   steps:
     - name: "step_name"
       agent: "agent-name"
       description: "步骤描述"
       retries: 3
       timeout: 60
   ```

3. **测试工作流**

   ```python
   from leo_orchestrator.api import leo

   result = leo.run_workflow(
       "workflow-name",
       agents=system.agents,
       **params
   )
   ```

---

## 📚 参考资料

### 现有 Agent 实现

- `leo_subagents/agents/research_agent/research_agent.py` - 研究代理
- `leo_subagents/agents/creative_agent/creative_agent.py` - 创作代理
- `leo_subagents/agents/analysis_agent/analysis_agent.py` - 分析代理

### 工作流引擎

- `leo_orchestrator/workflow_engine.py` - 工作流引擎实现
- `leo_config/settings/config.yaml` - 全局配置（包含工作流示例）

### 基类和工具

- `leo_subagents/agents/base_agent.py` - Agent 基类
- `leo_subagents/skills_bridge/skill_loader.py` - Skill 加载器
- `leo_subagents/skills_bridge/skill_executor.py` - Skill 执行器

---

## ✅ 验证清单

完成每个 Agent 后：

- [ ] Agent 文件创建完成
- [ ] 继承 BaseAgent 并实现必需方法
- [ ] 注册到 AgentFactory
- [ ] 更新 agents.yaml 配置
- [ ] 运行 leo_system.py 验证注册成功
- [ ] 测试 can_handle() 方法
- [ ] 测试 execute() 方法

完成每个工作流后：

- [ ] workflow.yaml 文件创建完成
- [ ] 工作流步骤定义清晰
- [ ] 关联的 Agent 都已实现
- [ ] 测试工作流执行
- [ ] 验证步骤间数据传递
- [ ] 测试错误处理和重试机制

---

## 🚀 开始新会话的方法

### 方法 1：直接开始（推荐）

在新会话中，直接说：

```
请继续实现 Leo AI Agent System 的下一步工作。
查看 TODO_NEXT_STEPS.md 文件了解待办事项。
当前需要实现 3 个新 Agent 和 3 个工作流。
```

Claude Code 会自动读取 CLAUDE.md 和 TODO_NEXT_STEPS.md，了解项目状态。

### 方法 2：指定具体任务

```
请实现 Architect Agent（架构设计代理）。
参考 TODO_NEXT_STEPS.md 中的实现指南。
```

### 方法 3：查看当前状态

```
查看项目当前状态和待办事项。
```

---

## 📝 注意事项

1. **当前分支**：`refactor/standardize-structure`
2. **目录命名**：已统一使用下划线（leo_skills, leo_config, leo_workflows, leo_orchestrator）
3. **系统状态**：运行正常，所有现有 Skills 和 Agents 成功注册
4. **Git 状态**：已提交所有更改，工作区干净

---

*创建时间：2026-01-23*
*创建者：Claude Opus 4.5*
