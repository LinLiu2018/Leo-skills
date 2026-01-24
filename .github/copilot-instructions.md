# Leo AI Agent System - Copilot Instructions

> 面向AI编码助手的项目指南 | Leo的智能体系统 - Skills + Subagents协同架构

---

## 🏗️ 核心架构

### 三层设计（Big Picture）

```
Orchestrator (编排层)
    ↓
Skills (能力库) + Subagents (执行者)
    ↓
Projects (实际应用)
```

**这不是普通的Python项目**—这是一个多智能体协作框架：

- **Skills** (`leo_skills/`): 模块化能力单元，每个是独立的Claude Code技能
  - 可独立使用，也可被Agent调用
  - YAML驱动配置，支持热加载
  - 例如：`content-layout-leo-cskill`（排版）、`realestate-news-publisher-cskill`（发布）

- **Subagents** (`leo-subagents/agents/`): 智能执行者，选择并协调Skills
  - `BaseAgent`: 抽象基类定义必须实现的接口（`can_handle()`、`execute()`）
  - 各类Agent（TaskAgent、ResearchAgent、CreativeAgent等）评估任务置信度
  - 通过`SkillLoader`和`SkillExecutor`调用Skills

- **Orchestrator** (`leo_orchestrator/`): 统一编排器
  - `UnifiedRegistry`: 动态注册Skills和Agents
  - `WorkflowEngine`: 多步骤工作流执行，支持Agent间数据传递
  - `LeoAPI`: 极简API（3行代码完成注册）

### 关键设计模式

**1. 自动发现机制** (`leo_orchestrator/api.py:auto_discover()`)

```python
# 无需手动配置，自动发现所有Skills
api = LeoAPI()  # 初始化自动发现
api.auto_discover()  # 扫描leo_skills/目录
```

**2. 置信度路由** (`leo-subagents/agents/base_agent.py`)

```
任务 → 所有Agent评分 → can_handle()返回置信度(0-1) → 选择最高分Agent执行
```

**3. 去AI化处理** (`leo_config/guidelines/deaiifier.py`)

- 将AI生成内容转换为真人口吻（创意模式/严谨模式）
- 用于营销文案、技术文档等场景
- 双模式：`creative`（口语）vs `formal`（客观）

---

## 📂 目录结构速查

| 路径 | 用途 | 关键文件 |
|------|------|---------|
| `leo_skills/` | 能力库（6个活跃技能） | `*/scripts/main.py` |
| `leo-subagents/agents/` | Agent实现 | `base_agent.py` (继承) |
| `leo_orchestrator/` | 编排器 | `api.py`, `registry.py`, `workflow_engine.py` |
| `leo_config/settings/` | 全局配置 | `config.yaml` (Skills列表) |
| `leo_config/guidelines/` | 指南库 | `deaiifier.py` (去AI化), `deaiification_guide.yaml` |
| `leo_workflows/` | 工作流定义 | YAML工作流配置 |
| `projects/` | 实际项目 | 房产小程序、菜场等 |

---

## 🔑 必读文件

1. **[CLAUDE.md](CLAUDE.md)** - 项目背景和Leo的战略目标
2. **[LEO_SYSTEM_README.md](LEO_SYSTEM_README.md)** - 系统架构详解
3. **[leo_orchestrator/api.py](leo_orchestrator/api.py)** - 极简API示例
4. **[leo-subagents/agents/task_agent.py](leo-subagents/agents/task_agent.py)** - Agent实现模板
5. **[leo_config/settings/config.yaml](leo_config/settings/config.yaml)** - Skills注册表

---

## 🛠️ 常用开发模式

### 模式1: 创建新的Skill

**目录结构** (遵循严格的约定)

```
leo_skills/{category}/{skill-name}-cskill/
├── scripts/
│   ├── main.py              # 入口
│   ├── collectors/          # 数据收集
│   ├── analyzers/           # 数据分析
│   ├── generators/          # 内容生成
│   └── publishers/          # 内容发布
├── config/
│   ├── config.yaml
│   └── *.yaml               # 特定配置（sources, styles等）
├── requirements.txt
├── README.md
├── SKILL.md
└── .claude-plugin/
    └── marketplace.json
```

**命名规范**:

- 目录: `{功能}-{分类}-cskill` (例: `content-layout-leo-cskill`)
- Python模块: 蛇形命名法 (例: `content_layout.py`)
- 配置键: 蛇形或kebab-case (例: `activation_keywords`)

### 模式2: 创建新的Agent

**继承`BaseAgent`，实现两个方法**:

```python
from leo-subagents.agents.base_agent import BaseAgent, AgentConfig

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
api.register("agent", "my-agent",
    type="executor",
    priority=1,
    skills=["skill1", "skill2"])
```

### 模式3: 定义工作流

**工作流YAML** (`leo_workflows/workflows/`):

```yaml
name: "文章发布流程"
description: "排版→发布→追踪"
steps:
  - name: "排版"
    agent: "task-agent"
    skill: "content-layout-leo-cskill"
    input:
      content: "{{ input.content }}"
      style: "story_telling"

  - name: "发布"
    agent: "task-agent"
    skill: "realestate-news-publisher-cskill"
    input:
      content: "{{ steps.排版.output }}"
```

**执行工作流**:

```python
from leo_orchestrator import LeoAPI
api = LeoAPI()
result = api.execute_workflow("文章发布流程", content="...")
```

---

## 🎯 常见任务模式

### 任务1: 添加新能力到系统

```python
# 步骤1: 在leo_skills/{category}/中创建{name}-cskill目录
# 步骤2: 在scripts/main.py中实现能力逻辑
# 步骤3: 配置config.yaml
# 步骤4: 在leo_config/settings/config.yaml中注册

api = LeoAPI()
api.auto_discover()  # 自动扫描注册
```

### 任务2: 让Agent支持新Skill

```python
# 在Agent的__init__中添加到capabilities
self.capabilities["new_ability"] = "skill-name"

# 在can_handle()中检测并加分
if "关键词" in task_lower:
    capability_score += 0.3

# 在execute()中调用
result = self.skill_executor.execute("skill-name", **params)
```

### 任务3: 新增Agent类型

```python
# 1. 创建 leo-subagents/agents/{name}-agent/agent.py
# 2. 继承BaseAgent，实现can_handle()和execute()
# 3. 在agents.yaml中配置
# 4. 通过api.register()或自动发现注册
```

---

## ⚙️ 配置管理

### 全局配置优先级

1. **环境变量** (最高): `SKILL_MODE=creative`
2. **`.env` 文件**: 本地私密配置
3. **`config.yaml`**: 项目级配置
4. **Skill内置** (最低): 技能默认配置

### 常见配置

**YAML配置示例** (`leo_skills/content-creation/content-layout-leo-cskill/config/style_profiles.yaml`):

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

## 🧪 测试和调试

### 本地测试流程

```bash
# 1. 安装依赖
pip install pyyaml

# 2. 运行Skill单元测试
cd leo_skills/content-creation/content-layout-leo-cskill
python -m pytest tests/ -v

# 3. 测试Agent
python leo-subagents/agents/test_agents.py

# 4. 运行工作流
python tests/run_ningbo_workflow.py
```

### 关键测试文件

- [tests/test_workflows.py](tests/test_workflows.py) - 工作流测试
- [leo_skills/test_evolution.py](leo_skills/test_evolution.py) - 技能进化测试
- `leo_skills/*/test_*.py` - 各Skill单元测试

---

## 🚫 常见陷阱

1. **配置文件路径**: 使用相对路径时从项目根目录计算

   ```python
   # ✅ 正确
   config_path = Path(__file__).parent / "config.yaml"

   # ❌ 错误
   config_path = "config.yaml"  # 依赖当前工作目录
   ```

2. **Skill命名**: 必须以`-cskill`结尾，否则自动发现失败

   ```
   ✅ my-skill-cskill
   ❌ my-skill / my_skill
   ```

3. **Agent置信度**: 总分应该在0-1范围，避免返回超过1.0的分数

   ```python
   # ✅ 正确
   return min(1.0, calculated_score)

   # ❌ 错误
   return calculated_score  # 可能超过1.0
   ```

4. **Skills调用**: 必须通过`SkillExecutor`，不要直接import

   ```python
   # ✅ 正确
   result = self.skill_executor.execute(skill_name, **params)

   # ❌ 错误
   from leo_skills.content_creation import my_skill
   ```

5. **工作流数据传递**: 使用`{{ steps.step_name.output }}`而非直接变量

   ```yaml
   # ✅ 正确
   input: "{{ steps.排版.output }}"

   # ❌ 错误
   input: content_from_previous_step
   ```

---

## 📚 项目特色约定

### 去AI化处理

所有面向用户的内容应调用`DeAIifier`确保真人口吻：

```python
from leo_config.guidelines.deaiifier import DeAIifier

deaiifier = DeAIifier(mode="creative")  # 营销文案
content = deaiifier.process(ai_generated_text)
```

**模式选择**:

- `creative`: 营销文案、直播脚本、社交内容
- `formal`: 技术文档、数据分析报告、正式公文

### 技能进化框架

Skills可自动学习优化（见[SKILL_EVOLUTION_IMPLEMENTATION_REPORT.md](docs/system/SKILL_EVOLUTION_IMPLEMENTATION_REPORT.md)):

```python
# Skill可记录执行反馈，自动调整策略
skill.record_feedback(rating=0.8, reason="用户满意")
skill.evolve()  # 自动改进
```

---

## 🎓 学习顺序

**新Agent开发者的学习路径**:

1. 阅读本文 (5分钟)
2. 理解 [BaseAgent](leo-subagents/agents/base_agent.py) (15分钟)
3. 研究 [TaskAgent](leo-subagents/agents/task_agent.py) 实现 (20分钟)
4. 查看 [config.yaml](leo_config/settings/config.yaml) 中的注册机制 (10分钟)
5. 创建第一个Agent类 (30分钟)
6. 添加到 `agents.yaml` 并自动发现 (5分钟)

**新Skill开发者的学习路径**:

1. 研究 [content-layout-leo-cskill](leo_skills/content-creation/content-layout-leo-cskill/) 目录结构 (10分钟)
2. 理解 `scripts/main.py` 入口模式 (15分钟)
3. 学习YAML配置驱动方式 (10分钟)
4. 创建第一个Skill目录和main.py (30分钟)
5. 在 `config.yaml` 中注册 (5分钟)

---

## 🔗 关键术语速查

| 术语 | 定义 | 例子 |
|------|------|------|
| **Skill** | 独立的能力单元，可用于多个Agent | `content-layout-leo-cskill` |
| **Subagent** | 智能执行者，选择和协调Skill | `TaskAgent`, `ResearchAgent` |
| **Orchestrator** | 统一编排器，协调Skill和Agent | `LeoAPI`, `WorkflowEngine` |
| **Workflow** | 多步骤流程，Agent串联执行 | 排版→发布→追踪 |
| **Registry** | 动态注册表，记录所有Skill和Agent | `UnifiedRegistry` |
| **Placement** | 置信度评分机制 | `can_handle(task)` 返回0-1 |
| **DeAI化** | 将AI文本转为真人口吻 | `DeAIifier.process()` |

---

## 📞 快速参考

```python
# 导入核心API
from leo_orchestrator.api import LeoAPI
from leo_subagents.agents.base_agent import BaseAgent, AgentConfig

# 初始化系统
api = LeoAPI()

# 注册Skill
api.register("skill", "my-skill", path="leo_skills/category/my-skill")

# 注册Agent
api.register("agent", "my-agent", type="executor", priority=1)

# 执行Skill
result = api.execute_skill("skill-name", param1="value")

# 执行工作流
result = api.execute_workflow("workflow-name", input_data=...)

# 列出所有资源
api.list_skills()
api.list_agents()
api.list_workflows()
```

---

**最后更新**: 2026-01-20 | **维护者**: Leo Liu | **反馈**: 提交Issue或PR改进本指南
