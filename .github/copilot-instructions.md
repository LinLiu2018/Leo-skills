# Leo AI Agent System - Copilot Instructions

> 面向AI编码助手的项目指南 | Leo的智能体系统 - Skills + Subagents协同架构

---

## 核心架构

### 三层设计（Big Picture）

```
Orchestrator (编排层)
    ↓
Skills (能力库) + Subagents (执行者)
    ↓
Projects (实际应用)
```

**这不是普通的Python项目**---这是一个多智能体协作框架：

- **Skills** (`src/leo_skills/`): 模块化能力单元，每个是独立的Claude Code技能
  - 可独立使用，也可被Agent调用
  - YAML驱动配置，支持热加载
  - 99+ 技能，19 个类别
  - 例如：`content_layout_leo_skill`（排版）、`web_search_skill`（搜索）

- **Subagents** (`src/leo_subagents/agents/`): 智能执行者，选择并协调Skills
  - `BaseAgent`: 抽象基类定义必须实现的接口（`can_handle()`、`execute()`）
  - 9 个Agent（ResearchAgent、AnalysisAgent、CreativeAgent等）评估任务置信度
  - 通过`SkillLoader`和`SkillExecutor`调用Skills

- **Orchestrator** (`src/leo_orchestrator/`): 统一编排器
  - `UnifiedRegistry`: 动态注册Skills和Agents
  - `WorkflowEngine`: 多步骤工作流执行，支持Agent间数据传递
  - `IntentRecognizer`: 意图识别引擎，自动路由到合适的Agent
  - `LeoAPI`: 极简API（3行代码完成注册）

### 关键设计模式

**1. 自动发现机制** (`src/leo_orchestrator/api.py:auto_discover()`)

```python
# 无需手动配置，自动发现所有Skills
api = LeoAPI()  # 初始化自动发现
api.auto_discover()  # 扫描src/leo_skills/目录
```

**2. 置信度路由** (`src/leo_subagents/agents/base_agent.py`)

```
任务 → 所有Agent评分 → can_handle()返回置信度(0-1) → 选择最高分Agent执行
```

**3. 意图识别路由** (`src/leo_orchestrator/intent_recognizer.py`)

```python
from leo_orchestrator import get_intent_recognizer

recognizer = get_intent_recognizer()
match = recognizer.recognize("帮我研究量子计算")
# 返回: IntentMatch(intent_type='agent', target='research_agent', confidence=0.9)
```

---

## 目录结构速查

| 路径 | 用途 | 关键文件 |
|------|------|---------|
| `src/leo_skills/` | 能力库（99+ 技能，19 类别） | `*/scripts/main.py`, `*/SKILL.md` |
| `src/leo_subagents/agents/` | Agent实现（9 个） | `base_agent.py` (继承) |
| `src/leo_orchestrator/` | 编排器 | `api.py`, `registry.py`, `intent_recognizer.py`, `workflow_engine.py` |
| `src/leo_workflows/` | 工作流定义 | `definitions/*.yaml` |
| `src/leo_memory/` | 共享记忆系统 | `shared_memory.py` |
| `src/leo_interface/` | 接口层（CLI/Web） | `cli/`, `web/`, `web_v2/` |
| `leo_knowledge/context/` | 静态上下文 | `user_profile.md`, `development_guide.md` |
| `projects/` | 实际项目 | 房产小程序、菜场等 |

### 技能类别一览

```
src/leo_skills/
├── automation/          # 自动化
├── backend/             # 后端开发
├── business/            # 商业应用
├── collaboration/       # 协作技能
├── content_creation/    # 内容创作
├── core/                # 核心技能
├── debugging/           # 调试技能
├── development/         # 开发工具
├── devops/              # DevOps
├── evolution/           # 技能进化
├── frontend/            # 前端开发
├── intelligence/        # 情报分析
├── prompt_engineering/  # 提示工程
├── scaffold/            # 脚手架
├── security/            # 安全
├── testing/             # 测试
├── tools/               # 工具集
├── utilities/           # 实用工具
└── videocut_skills/     # 视频剪辑
```

### Agent 列表

| Agent | 类型 | 触发词 |
|-------|------|--------|
| `research_agent` | researcher | 研究、调研、分析 |
| `analysis_agent` | analyzer | 分析、统计、数据 |
| `creative_agent` | creator | 创作、生成、写作 |
| `architect_agent` | designer | 架构设计、技术选型 |
| `product_manager_agent` | planner | 需求分析、PRD |
| `mobile_agent` | developer | 小程序、移动开发 |
| `realestate_agent` | specialist | 房地产、房产 |
| `ecommerce_agent` | ecommerce | 电商、运营 |
| `ai_news_summary_agent` | intelligence | 新闻摘要、情报 |

---

## 必读文件

1. **[CLAUDE.md](../CLAUDE.md)** - 项目背景和Leo的战略目标
2. **[leo_knowledge/context/development_guide.md](../leo_knowledge/context/development_guide.md)** - 开发规范详解
3. **[leo_knowledge/context/system_architecture.md](../leo_knowledge/context/system_architecture.md)** - 系统架构
4. **[src/leo_orchestrator/api.py](../src/leo_orchestrator/api.py)** - 极简API示例
5. **[src/leo_subagents/agents/base_agent.py](../src/leo_subagents/agents/base_agent.py)** - Agent基类模板
6. **[leo_knowledge/context/capability_index.md](../leo_knowledge/context/capability_index.md)** - 能力索引（自动生成）

---

## 常用开发模式

### 模式1: 创建新的Skill

**目录结构** (遵循严格的约定)

```
src/leo_skills/{category}/{skill_name}_skill/
├── __init__.py           # 包初始化
├── {skill_name}_skill.py # 主类（可选）
├── SKILL.md              # 技能定义文档
├── scripts/
│   ├── main.py           # 入口
│   ├── collectors/       # 数据收集
│   ├── analyzers/        # 数据分析
│   ├── generators/       # 内容生成
│   └── publishers/       # 内容发布
├── config/
│   ├── config.yaml
│   └── *.yaml            # 特定配置（sources, styles等）
└── requirements.txt
```

**命名规范**:

- 目录: `{功能}_skill` (例: `web_search_skill`, `content_layout_leo_skill`)
- Python模块: snake_case (例: `web_search_skill.py`)
- 配置键: snake_case (例: `activation_keywords`)
- **禁止使用连字符 `-`，统一使用下划线 `_`**

### 模式2: 创建新的Agent

**继承`BaseAgent`，实现两个方法**:

```python
from leo_subagents.agents.base_agent import BaseAgent, AgentConfig

class MyAgent(BaseAgent):
    ACTIVATION_KEYWORDS = ["关键词1", "关键词2"]

    def can_handle(self, task: str) -> float:
        """返回置信度 0-1"""
        score = 0.0
        for kw in self.ACTIVATION_KEYWORDS:
            if kw in task.lower():
                score += 0.2
        return min(1.0, score)

    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """执行任务，返回结果字典"""
        # 1. 分析任务
        # 2. 调用Skills: self.skill_executor.execute(skill_name, **params)
        # 3. 返回结果
        return {"status": "success", "result": ...}
```

**注册Agent**:

```python
api.register("agent", "my_agent",
    type="executor",
    priority=1,
    skills=["web_search_skill", "content_layout_leo_skill"])
```

### 模式3: 定义工作流

**工作流YAML** (`src/leo_workflows/definitions/`):

```yaml
name: "文章发布流程"
description: "排版 -> 发布 -> 追踪"
steps:
  - name: "排版"
    agent: "creative_agent"
    skill: "content_layout_leo_skill"
    input:
      content: "{{ input.content }}"
      style: "story_telling"

  - name: "发布"
    agent: "ecommerce_agent"
    skill: "realestate_news_publisher_skill"
    input:
      content: "{{ steps.排版.output }}"
```

**执行工作流**:

```python
from leo_orchestrator import get_workflow_engine

engine = get_workflow_engine(agents)
result = engine.execute_from_yaml('src/leo_workflows/definitions/content_pipeline.yaml')
```

---

## 常见任务模式

### 任务1: 添加新能力到系统

```python
# 步骤1: 在src/leo_skills/{category}/中创建{name}_skill目录
# 步骤2: 在scripts/main.py中实现能力逻辑
# 步骤3: 编写SKILL.md定义文档
# 步骤4: 配置config/config.yaml

api = LeoAPI()
api.auto_discover()  # 自动扫描注册
```

### 任务2: 让Agent支持新Skill

```python
# 在Agent的__init__中添加到capabilities
self.capabilities["new_ability"] = "skill_name"

# 在can_handle()中检测并加分
if "关键词" in task_lower:
    capability_score += 0.3

# 在execute()中调用
result = self.skill_executor.execute("skill_name", **params)
```

### 任务3: 新增Agent类型

```python
# 1. 创建 src/leo_subagents/agents/{name}_agent/ 目录
# 2. 编写 AGENT.md 定义文档
# 3. 继承BaseAgent，实现can_handle()和execute()
# 4. 通过api.register()或自动发现注册
```

---

## 配置管理

### 全局配置优先级

1. **环境变量** (最高): `SKILL_MODE=creative`
2. **`.env` 文件**: 本地私密配置
3. **`config.yaml`**: 项目级配置
4. **Skill内置** (最低): 技能默认配置

### 常见配置

**YAML配置示例** (`src/leo_skills/content_creation/content_layout_leo_skill/config/style_profiles.yaml`):

```yaml
styles:
  story_telling:
    name: "故事叙述型"
    emoji_frequency: "high"
    paragraph_length: "medium"

  minimalist_professional:
    name: "极简专业型"
    emoji_frequency: "low"
    paragraph_length: "short"
```

**环境变量** (`.env`):

```
DEAI_MODE=creative
SKILL_LOG_LEVEL=DEBUG
WORKFLOW_TIMEOUT=300
```

---

## 测试和调试

### 本地测试流程

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行Skill单元测试
cd src/leo_skills/content_creation/content_layout_leo_skill
python -m pytest tests/ -v

# 3. 测试所有P1/P2功能
python scripts/testing/quick_test.py

# 4. 更新能力索引
python scripts/maintenance/update_capability_index.py

# 5. 验证项目结构
python scripts/development/validate_structure.py
```

### 关键测试文件

- `scripts/quick_test.py` - 全功能快速测试
- `scripts/validate_structure.py` - 项目结构验证
- `src/leo_skills/*/tests/` - 各Skill单元测试

---

## 常见陷阱

1. **配置文件路径**: 使用相对路径时从项目根目录计算

   ```python
   # 正确
   config_path = Path(__file__).parent / "config.yaml"

   # 错误
   config_path = "config.yaml"  # 依赖当前工作目录
   ```

2. **Skill命名**: 必须以`_skill`结尾，使用下划线，否则自动发现失败

   ```
   正确: web_search_skill
   正确: content_layout_leo_skill
   错误: my-skill-cskill  (旧规范，已废弃)
   错误: my-skill          (缺少_skill后缀)
   ```

3. **Agent置信度**: 总分应该在0-1范围，避免返回超过1.0的分数

   ```python
   # 正确
   return min(1.0, calculated_score)

   # 错误
   return calculated_score  # 可能超过1.0
   ```

4. **Skills调用**: 必须通过`SkillExecutor`，不要直接import

   ```python
   # 正确
   result = self.skill_executor.execute(skill_name, **params)

   # 错误
   from leo_skills.content_creation import my_skill
   ```

5. **工作流数据传递**: 使用`{{ steps.step_name.output }}`而非直接变量

   ```yaml
   # 正确
   input: "{{ steps.排版.output }}"

   # 错误
   input: content_from_previous_step
   ```

6. **目录命名**: 禁止使用连字符，统一使用下划线

   ```
   正确: src/leo_subagents/agents/research_agent/
   错误: leo-subagents/agents/research-agent/
   ```

---

## 项目特色约定

### 意图识别路由

所有用户请求通过意图识别引擎自动路由：

```python
from leo_orchestrator import get_intent_recognizer

recognizer = get_intent_recognizer()
routing = recognizer.route("帮我研究量子计算")
# routing = {
#   "intent": IntentMatch(...),
#   "action": "delegate_to_agent",
#   "target": "research_agent",
#   "params": {...}
# }
```

### 共享记忆系统

跨会话持久化记忆：

```python
from leo_memory import get_shared_memory

memory = get_shared_memory()
memory.remember("project_context", "Leo AI System优化", "project", importance=5)
entries = memory.search("优化")
```

### 技能进化框架

Skills可自动学习优化：

```python
# Skill可记录执行反馈，自动调整策略
skill.record_feedback(rating=0.8, reason="用户满意")
skill.evolve()  # 自动改进
```

---

## 学习顺序

**新Agent开发者的学习路径**:

1. 阅读本文 (5分钟)
2. 理解 [BaseAgent](../src/leo_subagents/agents/base_agent.py) (15分钟)
3. 研究任意Agent实现，如 [research_agent](../src/leo_subagents/agents/research_agent/) (20分钟)
4. 查看 [capability_index.md](../leo_knowledge/context/capability_index.md) 中的注册机制 (10分钟)
5. 创建第一个Agent类 (30分钟)
6. 编写 `AGENT.md` 并通过自动发现注册 (5分钟)

**新Skill开发者的学习路径**:

1. 研究 [web_search_skill](../src/leo_skills/utilities/web_search_skill/) 目录结构 (10分钟)
2. 理解 `scripts/main.py` 入口模式 (15分钟)
3. 学习YAML配置驱动方式 (10分钟)
4. 创建第一个Skill目录和main.py (30分钟)
5. 编写 `SKILL.md` 定义文档 (5分钟)

---

## 关键术语速查

| 术语 | 定义 | 例子 |
|------|------|------|
| **Skill** | 独立的能力单元，可用于多个Agent | `web_search_skill` |
| **Subagent** | 智能执行者，选择和协调Skill | `research_agent`, `creative_agent` |
| **Orchestrator** | 统一编排器，协调Skill和Agent | `LeoAPI`, `WorkflowEngine` |
| **Workflow** | 多步骤流程，Agent串联执行 | 排版 -> 发布 -> 追踪 |
| **Registry** | 动态注册表，记录所有Skill和Agent | `UnifiedRegistry` |
| **IntentRecognizer** | 意图识别引擎，自动路由请求 | `recognizer.recognize(task)` |
| **SharedMemory** | 跨会话持久化记忆系统 | `memory.remember(key, value)` |
| **Placement** | 置信度评分机制 | `can_handle(task)` 返回0-1 |

---

## 快速参考

```python
# 导入核心API
from leo_orchestrator.api import LeoAPI
from leo_orchestrator import get_intent_recognizer, get_workflow_engine
from leo_subagents.agents.base_agent import BaseAgent, AgentConfig
from leo_memory import get_shared_memory

# 初始化系统
api = LeoAPI()
api.auto_discover()

# 注册Skill
api.register("skill", "my_skill", path="src/leo_skills/category/my_skill")

# 注册Agent
api.register("agent", "my_agent", type="executor", priority=1)

# 执行Skill
result = api.execute_skill("web_search_skill", query="AI趋势")

# 意图识别路由
recognizer = get_intent_recognizer()
match = recognizer.recognize("帮我研究量子计算")

# 执行工作流
engine = get_workflow_engine(agents)
result = engine.execute_from_yaml("src/leo_workflows/definitions/content_pipeline.yaml")

# 共享记忆
memory = get_shared_memory()
memory.remember("key", "value", "category")

# 列出所有资源
api.list_skills()
api.list_agents()
api.list_workflows()
```

---

**最后更新**: 2026-02-08 | **维护者**: Leo Liu | **反馈**: 提交Issue或PR改进本指南

