# Development Guide - Leo AI System

## 0. 核心原则 (Core Principles) ⚠️ 最重要

### 确认用户意图规则

**在执行任何重大改动前，必须先确认用户意图。**

重大改动包括：
- 目录/文件重命名
- 架构调整
- 批量修改
- 删除操作
- 配置变更

**执行流程**：

1. 分析改动影响范围
2. 列出所有受影响的文件/配置
3. 明确说明改动内容
4. **等待用户确认后再执行**

```
❌ 错误：直接执行改动
✅ 正确：先确认 → 用户同意 → 再执行
```

---

## 1. 常用命令 (Commands)

### 系统运行

```bash
# 运行主系统
python leo_system.py  # 注意：使用下划线

# 验证项目结构
python scripts/development/validate_structure.py

# 自动发现并更新 Manifest
python scripts/maintenance/update_manifests.py

# 运行测试
python tests/verify_setup.py
pytest tests/
```

### P1/P2 新功能命令

```bash
# 更新能力索引（自动生成 capability_index.md）
python scripts/maintenance/update_capability_index.py

# 测试所有 P1/P2 功能
python scripts/testing/quick_test.py

# 标准化 SKILL.md 格式（预览模式）
python scripts/development/standardize_skills.py --dry-run

# 执行标准化
python scripts/development/standardize_skills.py
```

### 依赖管理

```bash
pip install -r requirements.txt
```

---

## 2. 代码规范 (Coding Standards)

### Python (3.9+)

- **Naming**:
  - Class: `PascalCase` (e.g., `TaskAgent`)
  - Function/Var: `snake_case` (e.g., `run_workflow`)
  - Private: `_prefix` (e.g., `_internal_logic`)
- **Structure**:
  - 使用 Type Hints。
  - 复杂逻辑必须包含**中文注释**。

### 目录和文件命名规范 ⚠️ 全局唯一规范

**统一使用下划线 (underscore)，禁止使用连字符 (hyphen)**

此规范适用于：
- 项目根目录
- 所有子目录
- 所有 Python 文件
- 所有 Skill 目录
- 所有 Agent 目录

✅ **正确示例**：

- `leo_ai_system/` (项目根目录)
- `leo_system.py`
- `leo_skills/`
- `leo_subagents/`
- `web_search_skill/`
- `skill_evolution_assistant_skill/`

❌ **错误示例**：

- `leo-ai-system/`  ← 禁止
- `leo-system.py`   ← 禁止
- `leo-skills/`     ← 禁止
- `web-search-cskill/` ← 禁止（旧规范，已废弃）

**原因**：

1. Python 模块导入要求使用下划线
2. 避免路径引用错误
3. 保持项目命名一致性
4. 支持直接 `from xxx_skill import ...`

**验证**：

```bash
# 运行结构验证脚本
python scripts/development/validate_structure.py
```

### Skill 开发规范

- **命名**: `{function}_{type}_skill` (e.g., `web_search_skill`)
  - 统一使用下划线
  - 统一以 `_skill` 结尾
- **结构**: 必须包含 `SKILL.md` (定义) 和 `scripts/main.py` (入口)。

**Skill 目录结构**：

```
{skill_name}_skill/
├── __init__.py           # 包初始化
├── {skill_name}_skill.py # 主类（可选）
├── SKILL.md              # 技能定义文档
├── README.md             # 使用说明
├── scripts/
│   └── main.py           # 入口脚本
└── config/               # 配置文件（可选）
```

### 路径引用规范

**使用路径常量而非硬编码**：

```python
# ❌ 错误：硬编码路径
from leo_system import LeoSystem

# ✅ 正确：使用路径常量
from leo_system.paths import LEO_SYSTEM_PY, LEO_SKILLS
```

**导入路径常量**：

```python
from leo_system.paths import (
    PROJECT_ROOT,
    LEO_SKILLS,
    LEO_SYSTEM_PY,
    CLAUDE_MD,
)
```

---

## 3. Git 协作规范

| Prefix | Usage | Example |
| :--- | :--- | :--- |
| `feat` | 新功能 | `feat: add mobile agent` |
| `fix` | 修复BUG | `fix: manifest path error` |
| `docs` | 文档更新 | `docs: update user profile` |
| `refactor`| 代码重构 | `refactor: modularize claude.md` |

**分支策略**:

- `master`: 稳定生产分支
- `feature/*`: 功能开发

---

## 4. 命名规范速查表

| 类型 | 格式 | 示例 |
|-----|------|------|
| 项目目录 | `snake_case` | `leo_ai_system` |
| Python模块 | `snake_case` | `leo_system.py` |
| Python类 | `PascalCase` | `TaskAgent` |
| Python函数 | `snake_case` | `run_workflow` |
| Skill目录 | `{name}_skill` | `web_search_skill` |
| Agent目录 | `{name}_agent` | `research_agent` |
| 配置文件 | `snake_case` | `config.yaml` |

**禁止使用**：
- 连字符 `-` (hyphen)
- 空格
- 大写字母（目录/文件名）

---

## 5. 最佳实践标准（强制）

> **必须遵循**: [system_architecture.md](system_architecture.md#6-最佳实践标准-best-practice-standards)

### 快速参考

| 类型 | 必须文件 | 推荐文件 | 参考 |
|-----|---------|---------|------|
| **Skill** | SKILL.md (含frontmatter) | `__init__.py`, `config/config.yaml`, `evolution.json` | [标准结构](system_architecture.md#61-标准技能结构) |
| **Agent** | AGENT.md | `__init__.py`, `evolution.json` | [标准结构](system_architecture.md#62-标准代理结构) |
| **Workflow** | workflow.yaml | `__init__.py`, README.md | [标准结构](system_architecture.md#63-标准工作流结构) |

### 验证命令

```bash
# 验证技能结构
python scripts/development/validate_skills.py

# 验证命名规范
python scripts/development/validate_naming.py

# 检查重复技能
python scripts/development/check_duplicates.py
```

### 新建技能模板

```bash
# 使用模板创建新技能
python scripts/development/create_skill.py --name my_new_skill --category tools
```

---

## 6. 去重与规范化机制（强制）

> **参考**: [system_architecture.md#7-去重与规范化机制](system_architecture.md#7-去重与规范化机制-deduplication--standardization)

### 6.1 新增前检查清单

- [ ] 功能重复检查（搜索 skill_index）
- [ ] 命名冲突检查
- [ ] 能力重叠评估

### 6.2 命名规范速查

| 类型 | 格式 | 示例 |
|-----|------|------|
| 技能目录 | `{功能}_{类型}_skill` | `web_search_skill` |
| 代理目录 | `{领域}_agent` | `research_agent` |
| 工作流目录 | `{业务}_pipeline` | `content_pipeline` |

**禁止使用**: `-`, 空格, 大写字母开头, 中文

### 6.3 目录规范化状态

| 状态 | 原名称 | 新名称 |
|---------|------|---------|
| ✅ 已完成 | `剪口播` | `cut_speech_skill` |
| ✅ 已完成 | `剪辑` | `video_editing_skill` |
| ✅ 已完成 | `字幕` | `subtitle_skill` |
| ✅ 已完成 | `安装` | `install_skill` |
| ✅ 已完成 | `自更新` | `auto_update_skill` |

---

## 7. P1/P2 功能使用指南

### 7.1 意图识别引擎

**用途**: 自动识别用户意图，路由到合适的 Agent 或 Skill

```python
from leo_orchestrator import get_intent_recognizer

recognizer = get_intent_recognizer()

# 识别意图
match = recognizer.recognize("帮我研究量子计算")
print(match.intent_type)  # 'agent'
print(match.target)         # 'research_agent'
print(match.confidence)     # 0.9

# 获取路由决策
routing = recognizer.route("分析销售数据")
# routing = {
#   "action": "delegate_to_agent",
#   "target": "analysis_agent",
#   "params": {...}
# }
```

### 7.2 Workflow 引擎

**用途**: 编排多步骤、多 Agent 协作流程

```python
from leo_orchestrator import get_workflow_engine

# 创建引擎
engine = get_workflow_engine(agents_dict)

# 从 YAML 加载并执行
result = engine.execute_from_yaml(
    'src/leo_workflows/definitions/content_pipeline.yaml',
    topic="AI发展趋势"
)

# 或使用 Python 字典定义
workflow_def = {
    "name": "simple-flow",
    "steps": [
        {"name": "research", "agent": "research_agent"},
        {"name": "create", "agent": "creative_agent"},
    ]
}
result = engine.execute(workflow_def)
```

**工作流定义 YAML 格式**:
```yaml
name: content-pipeline
description: 内容生产流水线
version: "1.0"

inputs:
  topic:
    type: string
    required: true

steps:
  - name: research
    type: sequential
    agent: research_agent
    retries: 2
    timeout: 120

  - name: parallel_analysis
    type: parallel
    parallel_steps:
      - name: market_analysis
        agent: analysis_agent
      - name: trend_analysis
        agent: analysis_agent

  - name: create
    type: sequential
    agent: creative_agent
```

### 7.3 共享记忆系统

**用途**: 跨会话持久化用户偏好、项目上下文等信息

```python
from leo_memory import get_shared_memory

memory = get_shared_memory()

# 记住信息
memory.remember(
    key="user_name",
    value="张三",
    category="user_profile",
    importance=4,
    expires_in_days=365  # 可选：过期时间
)

# 回忆信息
entry = memory.recall("user_name")
print(entry.value)  # "张三"

# 搜索记忆
results = memory.search("用户偏好")

# 获取统计
stats = memory.get_stats()
```

**记忆存储位置**: `leo_knowledge/context/shared_memory.md`

### 7.4 能力索引自动更新

**用途**: 自动扫描并生成所有 Skills、Agents、Workflows 的索引文档

```bash
# 手动执行
python scripts/maintenance/update_capability_index.py

# 输出位置
# leo_knowledge/context/capability_index.md
```

**定时任务已配置**: `capability_index_daily` (每天 06:00 自动执行)

### 7.5 SKILL.md 标准化

**用途**: 统一所有 SKILL.md 文件格式（添加 YAML frontmatter）

```bash
# 预览（不实际修改）
python scripts/development/standardize_skills.py --dry-run

# 执行标准化
python scripts/development/standardize_skills.py

# 指定目录
python scripts/development/standardize_skills.py --path src/leo_skills/custom_category
```

**标准 SKILL.md 格式**:
```markdown
---
name: skill_name
version: 1.0.0
category: tools
description: 技能描述
triggers:
  - "触发词1"
  - "触发词2"
inputs:
  - name: input
    type: string
    required: true
outputs:
  - name: output
    type: string
author: Leo Liu
---

# Skill Title

技能详细说明...
```

---

## 8. Superpowers 开发工作流 (v4.2.0)

> 集成自 [obra/superpowers](https://github.com/obra/superpowers)，提供 14 个开发工作流技能

### 8.1 核心工作流

**推荐的开发流程**：

```
brainstorming → writing_plans → executing_plans → finishing_work
     ↓               ↓               ↓                ↓
  头脑风暴       编写计划        执行计划          完成收尾
```

### 8.2 关键规则

| 规则 | 说明 |
|------|------|
| **Git 工作树隔离** | 执行计划前**必须**使用 `using_git_worktrees_skill` 创建隔离工作区 |
| **主分支保护** | 未经用户明确同意，不得在 main/master 分支上直接开发 |
| **TDD 优先** | 使用 `tdd_skill` 先写测试再写实现 |
| **代码审查** | 完成后使用 `requesting_code_review_skill` 请求审查 |

### 8.3 Superpowers 与 Leo 技能对照

| Superpowers (英文原版) | Leo 系统 (中文版) | 使用场景 |
|------------------------|-------------------|----------|
| brainstorming | brainstorming_skill | 需求分析、方案探索 |
| writing-plans | writing_plans_skill | 编写实施计划 |
| executing-plans | executing_plans_skill | 执行计划中的任务 |
| tdd | tdd_skill | 测试驱动开发 |
| debugging | debugging_skill | 系统化调试 |
| using-git-worktrees | using_git_worktrees_skill | Git 工作树隔离 |
| finishing-work | finishing_work_skill | 完成收尾、清理 |

### 8.4 SessionStart Hook

每次 Claude Code 会话启动时，自动注入 `using-superpowers` 技能上下文：

```json
// .claude/hooks.json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "startup|resume|clear|compact",
      "hooks": [{
        "type": "command",
        "command": "bash \"~/.claude/skills/superpowers/hooks/session-start.sh\"",
        "async": true
      }]
    }]
  }
}
```

### 8.5 文件位置

| 内容 | 路径 |
|------|------|
| Superpowers 原始技能 | `~/.claude/skills/superpowers/skills/` |
| Leo 中文版技能 | `src/leo_skills/` 各类别目录下 |
| 参考文档 | `docs/reference/superpowers/` |
| Hook 配置 | `.claude/hooks.json` |

