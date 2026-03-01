# 审查后修复计划 v2（Claude Code 审查 → Codex 执行）

> 基于 Codex 二次检测发现的 3 个问题，按优先级排列。

---

## 任务 1：修复 validate_structure.py 过时规则

文件：`scripts/development/validate_structure.py`

当前脚本检查的是根目录下的旧路径，与 `src/` 结构不一致，导致 3 个误报。

### 修改点

**第 75-81 行** — `validate_required_files` 中移除 `leo_system.py`：

```python
# 修改前
required_files = [
    "README.md",
    "CLAUDE.md",
    ".gitignore",
    "requirements.txt",
    "leo_system.py",  # 注意：使用下划线
]

# 修改后
required_files = [
    "README.md",
    "CLAUDE.md",
    ".gitignore",
    "pyproject.toml",
]
```

说明：`leo_system.py` 已不存在于根目录，`requirements.txt` 已被 `pyproject.toml` 取代。

**第 92 行** — `validate_skill_structure` 中修正路径：

```python
# 修改前
skills_dir = self.project_root / "leo_skills"

# 修改后
skills_dir = self.project_root / "src" / "leo_skills"
```

**第 64-69 行** — `validate_naming_convention` 中增加跳过规则，忽略 `src`、`projects`、`output`、`leo_knowledge`、`reports`、`leo-skills-old`：

```python
skip_patterns = [
    ".",           # 隐藏目录
    "archive",
    "docs",
    "tests",
    "scripts",
    "examples",
    "src",
    "projects",
    "output",
    "reports",
    "leo_knowledge",
    "__pycache__",
    "node_modules",
    ".egg-info",
    "demo-",
]
```

**提交信息**：`fix: 更新 validate_structure.py 适配 src/ 目录结构`

---

## 任务 2：修复 .gitignore 编码乱码

文件：`.gitignore`

第 74-94 行的中文注释出现乱码（`改造补�?`、`数据库文�?`、`临时生成的源�?`、`�ɻع�������`、`����ɼ���Ŀ¼����������`）。

**操作**：将第 73 行到文件末尾替换为以下内容（UTF-8 编码）：

```gitignore
# Deep research scripts (temporary)
deep_research_*.py

# === 2026-02-25 改造补充 ===

# 数据库文件
*.db
*.sqlite
*.sqlite3

# 输出目录
output/

# 临时生成的源码
scripts/src/

# Web 前端产物
src/leo_interface/web_v2/node_modules/
src/leo_interface/web_v2/.env
src/leo_interface/web_v2/api/.env
src/leo_interface/web_v2/api/*.db

# 可回滚清理区
.trash/

# 旧版遗留目录
leo-skills-old/
```

注意：确保文件以 UTF-8 无 BOM 编码保存。

**提交信息**：`fix: 修复 .gitignore 中文注释编码乱码`

---

## 任务 3：提交当前工作区未提交的变更

当前有以下文件被修改但未提交：
- `scripts/development/validate_naming.py`（已加排除规则）
- `src/leo_interface/web_v2/api/leo_api_adapter.py`（已加固路径查找）
- `leo_knowledge/context/capability_index.md`（二次检测时重新生成）

**操作**：
```bash
git add scripts/development/validate_naming.py src/leo_interface/web_v2/api/leo_api_adapter.py leo_knowledge/context/capability_index.md
git commit -m "chore: 提交审查期间的修改（排除规则、路径加固、索引更新）"
```

**提交信息**：`chore: 提交审查期间的修改（排除规则、路径加固、索引更新）`

---

## 执行顺序

```
任务 3（先提交已有变更）→ 任务 2（修复 .gitignore）→ 任务 1（修复 validate_structure.py）
```

每个任务单独提交。任务 1 完成后运行验证：
```bash
python scripts/development/validate_structure.py
python scripts/development/validate_naming.py
```

预期结果：两个脚本都应该 0 错误、0 违规。
