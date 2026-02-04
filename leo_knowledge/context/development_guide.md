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
python scripts/validate_structure.py

# 自动发现并更新 Manifest
python scripts/update_manifests.py

# 运行测试
python tests/verify_setup.py
pytest tests/
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
python scripts/validate_structure.py
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
python scripts/validate_skills.py

# 验证命名规范
python scripts/validate_naming.py

# 检查重复技能
python scripts/check_duplicates.py
```

### 新建技能模板

```bash
# 使用模板创建新技能
python scripts/create_skill.py --name my_new_skill --category tools
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
