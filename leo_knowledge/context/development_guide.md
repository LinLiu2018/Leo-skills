# Development Guide - Leo AI System

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

### Python (3.13+)
- **Naming**:
    - Class: `PascalCase` (e.g., `TaskAgent`)
    - Function/Var: `snake_case` (e.g., `run_workflow`)
    - Private: `_prefix` (e.g., `_internal_logic`)
- **Structure**:
    - 使用 Type Hints。
    - 复杂逻辑必须包含**中文注释**。

### 目录和文件命名规范 ⚠️ 重要

**统一使用下划线 (underscore)，禁止使用连字符 (hyphen)**

✅ **正确示例**：
- `leo_system.py`
- `leo_skills/`
- `leo_subagents/`
- `skill_evolution_assistant.py`

❌ **错误示例**：
- `leo-system.py`  ← 禁止
- `leo-skills/`    ← 禁止
- `skill-evolution-assistant.py`  ← 禁止

**原因**：
1. Python 模块导入要求使用下划线
2. 避免路径引用错误
3. 保持项目命名一致性

**验证**：
```bash
# 运行结构验证脚本
python scripts/validate_structure.py
```

### Skill 开发规范
- **命名**: `{function}-{type}-cskill` (e.g., `web-search-cskill`)
  - 注意：技能目录名可以使用连字符（历史原因）
  - 但内部 Python 文件必须使用下划线
- **结构**: 必须包含 `SKILL.md` (定义) 和 `scripts/main.py` (入口)。

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
