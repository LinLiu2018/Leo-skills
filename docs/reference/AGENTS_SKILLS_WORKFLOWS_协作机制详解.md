# Leo AI Agent System - Agents、Skills、Workflows协作机制详解

**日期**: 2026-01-09
**版本**: 1.0.0

---

## 📋 目录

1. [系统架构概览](#系统架构概览)
2. [三大核心组件](#三大核心组件)
3. [3个Workflows详解](#3个workflows详解)
4. [协作机制](#协作机制)
5. [使用示例](#使用示例)
6. [当前状态](#当前状态)

---

## 🏗️ 系统架构概览

Leo AI Agent System采用三层架构：

```
┌─────────────────────────────────────────┐
│           Workflows (工作流层)           │
│  定义多Agent协作的完整业务流程           │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│            Agents (代理层)              │
│  智能代理，负责任务规划和执行            │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│            Skills (技能层)              │
│  具体功能实现，可被Agents调用            │
└─────────────────────────────────────────┘
```

---

## 🧩 三大核心组件

### 1. Skills (技能)

**定义**: 最小的功能单元，提供具体的能力实现

**特点**:

- 单一职责，专注一个功能
- 可被多个Agents复用
- 独立开发和测试
- 配置化管理

**当前系统中的8个Skills**:

| Skill名称 | 分类 | 功能 |
|----------|------|------|
| content_layout_leo_skill | content-creation | 智能内容排版 |
| realestate_news_publisher_skill | content-creation | 房产资讯发布 |
| research_assistant_skill | utilities | 智能研究助手 |
| web_search_skill | utilities | 网络搜索 |
| data_analyzer_skill | data-analysis | 数据分析 |
| agent_skill_creator_skill | tools | 技能创建元技能 |
| article_to_prototype_skill | tools | 文章转代码原型 |
| project_marketing_doc_generator_skill | tools | 项目营销文档生成 |

**Skill结构**:

```python
class Skill:
    def __init__(self, config):
        """初始化配置"""
        pass

    def execute(self, **kwargs):
        """执行具体功能"""
        pass

    def get_help(self):
        """获取帮助信息"""
        pass
```

### 2. Agents (代理)

**定义**: 智能代理，负责任务理解、规划和执行

**特点**:

- 具有专业领域知识
- 可以调用多个Skills
- 自动选择合适的Skill
- 支持任务分解和规划

**当前系统中的5个Agents**:

| Agent名称 | 类型 | 优先级 | Skills数量 | 专业领域 |
|----------|------|--------|-----------|---------|
| task-agent | executor | 1 | 3 | 任务执行 |
| research-agent | researcher | 2 | 3 | 信息研究 |
| analysis-agent | analyzer | 3 | 1 | 数据分析 |
| creative-agent | creator | 4 | 2 | 内容创作 |
| realestate-agent | realestate | 5 | 4 | 房地产业务 |

**Agent能力映射**:

```yaml
task-agent:
  skills:
    - content_layout_leo_skill
    - realestate_news_publisher_skill
    - project_marketing_doc_generator_skill

research-agent:
  skills:
    - research_assistant_skill
    - web_search_skill          # 🆕 新增
    - article_to_prototype_skill

analysis-agent:
  skills:
    - data_analyzer_skill       # 🆕 新增

creative-agent:
  skills:
    - content_layout_leo_skill
    - article_to_prototype_skill

realestate-agent:
  skills:
    - project_marketing_doc_generator_skill
    - realestate_news_publisher_skill
    - web_search_skill
    - research_assistant_skill
```

**Agent工作流程**:

```
1. 接收任务 → 2. 理解任务 → 3. 规划步骤 → 4. 调用Skills → 5. 返回结果
```

### 3. Workflows (工作流)

**定义**: 多Agent协作的完整业务流程

**特点**:

- 定义Agent执行顺序
- 支持数据传递
- 可配置化管理
- 适合复杂业务场景

---

## 🔄 3个Workflows详解

### Workflow 1: content-pipeline (内容生产线)

**用途**: 研究→创作→发布的完整内容生产流程

**配置**:

```yaml
content-pipeline:
  name: "内容生产线"
  description: "研究→创作→发布的完整流程"
  enabled: true
  steps:
    - name: "research"
      agent: "research-agent"
      description: "信息收集和研究"
    - name: "create"
      agent: "creative-agent"
      description: "内容创作"
    - name: "publish"
      agent: "task-agent"
      description: "发布和推广"
```

**执行流程**:

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Research     │ →  │ Creative     │ →  │ Task         │
│ Agent        │    │ Agent        │    │ Agent        │
├──────────────┤    ├──────────────┤    ├──────────────┤
│ • 搜索信息   │    │ • 撰写内容   │    │ • 排版优化   │
│ • 收集资料   │    │ • 生成文案   │    │ • 发布推广   │
│ • 整理数据   │    │ • 创意输出   │    │ • 渠道分发   │
└──────────────┘    └──────────────┘    └──────────────┘
```

**应用场景**:

- 房地产市场分析文章生成
- 项目营销内容创作
- 行业报告撰写

**使用示例**:

```python
# 运行内容生产线
result = system.run_workflow(
    "content-pipeline",
    topic="2026年宁波房地产市场趋势分析"
)

# 执行过程:
# Step 1: research-agent搜索市场信息
# Step 2: creative-agent撰写分析文章
# Step 3: task-agent优化排版并发布
```

### Workflow 2: research-pipeline (研究线)

**用途**: 收集→分析的纯研究流程

**配置**:

```yaml
research-pipeline:
  name: "研究线"
  description: "收集→分析的纯研究流程"
  enabled: true
  steps:
    - name: "collect"
      agent: "research-agent"
      description: "信息收集"
    - name: "analyze"
      agent: "analysis-agent"
      description: "数据分析"
```

**执行流程**:

```
┌──────────────┐    ┌──────────────┐
│ Research     │ →  │ Analysis     │
│ Agent        │    │ Agent        │
├──────────────┤    ├──────────────┤
│ • 搜索数据   │    │ • 统计分析   │
│ • 抓取内容   │    │ • 趋势识别   │
│ • 提取信息   │    │ • 生成报告   │
└──────────────┘    └──────────────┘
```

**应用场景**:

- 市场调研
- 竞品分析
- 数据收集和分析

**使用示例**:

```python
# 运行研究线
result = system.run_workflow(
    "research-pipeline",
    topic="智慧农贸市场竞品分析"
)

# 执行过程:
# Step 1: research-agent收集竞品信息
# Step 2: analysis-agent分析数据并生成报告
```

### Workflow 3: analysis-pipeline (分析线)

**用途**: 分析→报告的纯分析流程

**配置**:

```yaml
analysis-pipeline:
  name: "分析线"
  description: "分析→报告的纯分析流程"
  enabled: true
  steps:
    - name: "analyze"
      agent: "analysis-agent"
      description: "执行分析"
    - name: "report"
      agent: "task-agent"
      description: "生成报告"
```

**执行流程**:

```
┌──────────────┐    ┌──────────────┐
│ Analysis     │ →  │ Task         │
│ Agent        │    │ Agent        │
├──────────────┤    ├──────────────┤
│ • 数据分析   │    │ • 报告生成   │
│ • 趋势预测   │    │ • 格式优化   │
│ • 对比评估   │    │ • 文档输出   │
└──────────────┘    └──────────────┘
```

**应用场景**:

- 销售数据分析
- 业绩报告生成
- 趋势预测报告

**使用示例**:

```python
# 运行分析线
result = system.run_workflow(
    "analysis-pipeline",
    data=[100, 120, 110, 130, 150],
    title="月度销售分析报告"
)

# 执行过程:
# Step 1: analysis-agent分析销售数据
# Step 2: task-agent生成格式化报告
```

---

## 🤝 协作机制

### 1. Skills → Agents (技能被代理调用)

**调用方式**:

```python
# Agent内部调用Skill
class ResearchAgent(BaseAgent):
    def execute(self, task, **kwargs):
        # 调用web_search_skill
        results = self.use_skill("web_search_skill", "search", query=task)
        return results
```

**数据流**:

```
Task → Agent → Skill → Result → Agent → Final Result
```

### 2. Agents → Workflows (代理被工作流编排)

**编排方式**:

```yaml
workflow:
  steps:
    - agent: "research-agent"  # 第1步
    - agent: "creative-agent"  # 第2步
    - agent: "task-agent"      # 第3步
```

**数据传递**:

```
Step 1 Output → Step 2 Input → Step 2 Output → Step 3 Input
```

### 3. 完整协作流程

**示例：生成房地产市场分析文章**

```
用户请求: "生成宁波房地产市场分析文章"
    ↓
Workflow: content-pipeline
    ↓
┌─────────────────────────────────────────┐
│ Step 1: Research Agent                  │
│ ├─ 调用 web_search_skill              │
│ │  └─ 搜索"宁波房地产市场"             │
│ ├─ 调用 research_assistant_skill      │
│ │  └─ 整理搜索结果                     │
│ └─ 输出: 市场数据和信息                │
└─────────────────────────────────────────┘
    ↓ (数据传递)
┌─────────────────────────────────────────┐
│ Step 2: Creative Agent                  │
│ ├─ 接收: 市场数据                      │
│ ├─ 调用 article_to_prototype_skill    │
│ │  └─ 生成文章结构                     │
│ └─ 输出: 文章草稿                      │
└─────────────────────────────────────────┘
    ↓ (数据传递)
┌─────────────────────────────────────────┐
│ Step 3: Task Agent                      │
│ ├─ 接收: 文章草稿                      │
│ ├─ 调用 content_layout_leo_skill      │
│ │  └─ 优化排版                         │
│ ├─ 调用 realestate_news_publisher_skill│
│ │  └─ 发布文章                         │
│ └─ 输出: 最终发布结果                  │
└─────────────────────────────────────────┘
    ↓
返回给用户: 完整的分析文章
```

### 4. 智能路由机制

**自动Agent选择**:

```python
# 系统根据任务自动选择最合适的Agent
def _select_agent(self, task: str):
    best_agent = None
    best_score = 0.0

    for agent in self.agents.values():
        score = agent.can_handle(task)  # 每个Agent评估自己的能力
        if score > best_score:
            best_score = score
            best_agent = agent

    return best_agent if best_score > 0.3 else None
```

**示例**:

```python
# 用户输入: "分析房地产市场数据"
# 系统评分:
# - research-agent: 0.5 (包含"分析"关键词)
# - analysis-agent: 0.8 (包含"分析"+"数据"关键词)
# - realestate-agent: 0.7 (包含"房地产"关键词)
#
# 选择: analysis-agent (得分最高)
```

---

## 💻 使用示例

### 示例1: 直接调用Agent

```python
from leo_system import LeoSystem

system = LeoSystem()

# 方式1: 指定Agent
result = system.execute_task(
    "分析宁波房地产市场",
    agent_name="realestate-agent"
)

# 方式2: 自动选择Agent
result = system.execute_task(
    "分析销售数据",
    data=[100, 120, 110, 130, 150]
)
```

### 示例2: 直接调用Skill

```python
# 调用web_search_skill
result = system.call_skill(
    "web_search_skill",
    "search",
    query="人工智能发展趋势",
    max_results=10
)

# 调用data_analyzer_skill
result = system.call_skill(
    "data_analyzer_skill",
    "analyze",
    data=[100, 120, 110, 130, 150],
    analysis_type="trend"
)
```

### 示例3: 运行Workflow (待实现)

```python
# 运行内容生产线
result = system.run_workflow(
    "content-pipeline",
    topic="2026年房地产市场趋势"
)

# 运行研究线
result = system.run_workflow(
    "research-pipeline",
    topic="智慧农贸市场分析"
)

# 运行分析线
result = system.run_workflow(
    "analysis-pipeline",
    data=[100, 120, 110, 130, 150]
)
```

---

## 📊 当前状态

### ✅ 已实现

1. **Skills层** - 100%完成
   - ✅ 8个Skills全部实现
   - ✅ 统一接口设计
   - ✅ 配置化管理

2. **Agents层** - 100%完成
   - ✅ 5个Agents全部实现
   - ✅ 智能任务路由
   - ✅ Skills调用机制
   - ✅ 任务规划能力

3. **Workflows层** - 50%完成
   - ✅ 3个Workflows已配置
   - ✅ Workflow注册机制
   - ⚠️ Workflow执行逻辑待实现

### ⚠️ Workflows当前状态

**已完成**:

- ✅ Workflow配置定义（config.yaml）
- ✅ Workflow注册到Registry
- ✅ Workflow查询接口

**待实现**:

- ⏳ Workflow执行引擎
- ⏳ Agent间数据传递
- ⏳ 错误处理和重试
- ⏳ 执行状态跟踪

**代码位置**:

```python
# leo_orchestrator/api.py:218-242
def run_workflow(self, workflow_name: str, **kwargs):
    workflow = self.registry.get_workflow(workflow_name)

    if not workflow:
        print(f"❌ Workflow不存在: {workflow_name}")
        return None

    # TODO: 实现实际的工作流执行逻辑
    print(f"🔄 运行工作流: {workflow_name}")
    return f"执行{workflow_name}工作流（待实现）"
```

### 🎯 Workflow实现计划

**需要实现的功能**:

1. **Workflow执行引擎**

```python
class WorkflowEngine:
    def execute(self, workflow, **kwargs):
        results = []
        context = kwargs  # 初始上下文

        for step in workflow['steps']:
            agent = self.get_agent(step['agent'])
            result = agent.execute(step['name'], **context)
            results.append(result)
            context.update(result)  # 更新上下文

        return results
```

2. **数据传递机制**

```python
# Step 1输出 → Step 2输入
step1_output = research_agent.execute(...)
step2_input = {**kwargs, **step1_output}
step2_output = creative_agent.execute(**step2_input)
```

3. **错误处理**

```python
try:
    result = agent.execute(...)
except Exception as e:
    # 记录错误
    # 决定是否重试或跳过
    pass
```

---

## 🚀 下一步行动

### 立即可用

**当前可以使用**:

1. ✅ 直接调用任何Agent
2. ✅ 直接调用任何Skill
3. ✅ 自动Agent选择

**使用方式**:

```python
system = LeoSystem()

# 使用Agent
system.execute_task("分析数据", agent_name="analysis-agent")

# 使用Skill
system.call_skill("web_search_skill", "search", query="...")
```

### 需要开发

**Workflow执行**:

- 需要实现WorkflowEngine
- 预计开发时间: 2-3小时
- 优先级: 中

---

## 📝 总结

### 系统优势

1. **模块化设计**: Skills、Agents、Workflows三层分离
2. **高度复用**: Skills可被多个Agents使用
3. **智能路由**: 自动选择最合适的Agent
4. **配置驱动**: 通过YAML配置管理所有组件
5. **易于扩展**: 新增组件只需实现接口

### 协作关系

```
Workflows (业务流程)
    ↓ 编排
Agents (智能代理)
    ↓ 调用
Skills (功能实现)
```

### 当前能力

- ✅ **Skills**: 8个，全部可用
- ✅ **Agents**: 5个，全部可用
- ⚠️ **Workflows**: 3个，已配置但执行逻辑待实现

---

**文档版本**: 1.0.0
**最后更新**: 2026-01-09
**维护者**: Leo Liu
