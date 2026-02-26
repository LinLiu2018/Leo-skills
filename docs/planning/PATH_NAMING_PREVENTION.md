# 路径和命名问题预防机制

> **创建时间**: 2026-01-24
> **目的**: 防止项目中再次出现文件路径和命名不一致的问题

---

## 🎯 问题回顾

### 历史问题

1. **循环导入**：`leo_skills/core/__init__.py` 引用已归档的模块
2. **过时测试**：测试文件依赖已删除的模块
3. **路径错误**：`test_workflows.py` 使用 `leo-system.py`（连字符）而非 `leo_system.py`（下划线）

### 根本原因

- 目录重构后引用未更新
- 文件命名标准化后测试路径未同步
- 缺少自动化验证机制

---

## ✅ 已实施的预防措施

### 1. 统一命名规范 ⭐ 核心

**规则**：所有 Python 相关的目录和文件必须使用**下划线**，禁止使用连字符

✅ **正确**：

```
leo_system.py
leo_skills/
leo_subagents/
skill_evolution_assistant.py
```

❌ **错误**：

```
leo-system.py      ← 禁止
leo-skills/        ← 禁止
skill-evolution-assistant.py  ← 禁止
```

**文档位置**：[development_guide.md](../leo_knowledge/context/development_guide.md)

---

### 2. 路径常量管理

**文件**：`leo_system/paths.py`

**用途**：集中管理所有文件和目录路径，避免硬编码

**使用示例**：

```python
# ❌ 错误：硬编码路径
leo_system_path = "leo-system.py"

# ✅ 正确：使用路径常量
from leo_system.paths import LEO_SYSTEM_PY
leo_system_path = LEO_SYSTEM_PY
```

**可用常量**：

```python
PROJECT_ROOT          # 项目根目录
LEO_SKILLS           # leo_skills/
LEO_SUBAGENTS        # leo_subagents/
LEO_SYSTEM_PY        # leo_system.py
CLAUDE_MD            # CLAUDE.md
# ... 更多常量见 leo_system/paths.py
```

---

### 3. 自动化结构验证

**脚本**：`scripts/validate_structure.py`

**功能**：

- ✅ 检查目录命名规范（禁止连字符）
- ✅ 验证必需文件存在
- ✅ 检查技能结构完整性
- ✅ 发现遗留的旧命名文件

**使用方法**：

```bash
# 手动运行
python scripts/development/validate_structure.py

# 查看所有路径配置
python leo_system/paths.py
```

**输出示例**：

```
============================================================
项目结构验证
============================================================

[检查] 目录命名规范...
[检查] 必需文件...
[检查] 技能结构...
[检查] 遗留命名...

============================================================
验证报告
============================================================

[错误] 发现 2 个错误:
  - 目录使用连字符: leo-skills-old (应使用下划线)
  - 发现遗留文件: leo-system.py (应使用下划线命名)

[成功] 无错误，但有 3 个警告
============================================================
```

---

### 4. Pre-commit Hooks

**文件**：`.pre-commit-config.yaml`

**自动检查**：

- ✅ 结构验证（每次提交前自动运行）
- ✅ 代码格式化（black, isort）
- ✅ 代码质量检查（flake8）
- ✅ 技能验证

**安装**：

```bash
# 安装 pre-commit
pip install pre-commit

# 安装 hooks
pre-commit install

# 手动运行所有检查
pre-commit run --all-files
```

**提交时自动运行**：

```bash
git commit -m "feat: add new feature"
# 自动运行：
# 1. 结构验证
# 2. 代码格式化
# 3. 代码质量检查
# 4. 技能验证
```

---

### 5. 更新的开发指南

**文件**：`leo_knowledge/context/development_guide.md`

**新增内容**：

- ✅ 明确的命名规范
- ✅ 路径引用规范
- ✅ 验证命令说明
- ✅ 正确/错误示例对比

---

## 🔄 日常工作流程

### 开发新功能时

1. **创建文件/目录**：

   ```bash
   # ✅ 正确
   mkdir leo_new_module
   touch leo_new_module/main.py

   # ❌ 错误
   mkdir leo-new-module  # 禁止使用连字符
   ```

2. **引用路径**：

   ```python
   # ✅ 正确：使用路径常量
   from leo_system.paths import LEO_SKILLS, PROJECT_ROOT

   # ❌ 错误：硬编码路径
   skills_path = "leo-skills"  # 禁止
   ```

3. **提交前验证**：

   ```bash
   # 手动验证（可选）
   python scripts/development/validate_structure.py

   # Git 提交（自动验证）
   git add .
   git commit -m "feat: add new feature"
   # pre-commit hooks 会自动运行验证
   ```

---

### 重构代码时

1. **重命名文件/目录**：

   ```bash
   # 1. 重命名
   mv leo-old-name leo_new_name

   # 2. 更新所有引用
   grep -r "leo-old-name" .
   # 手动更新所有引用

   # 3. 验证
   python scripts/development/validate_structure.py
   ```

2. **更新路径常量**：

   ```python
   # 在 leo_system/paths.py 中更新
   LEO_NEW_MODULE = PROJECT_ROOT / "leo_new_module"
   ```

3. **更新测试**：

   ```python
   # 使用路径常量
   from leo_system.paths import LEO_NEW_MODULE
   ```

---

## 🚨 错误处理

### 如果验证失败

```bash
$ python scripts/development/validate_structure.py

[错误] 发现 1 个错误:
  - 目录使用连字符: leo-old-name (应使用下划线)
```

**解决步骤**：

1. 重命名文件/目录：`mv leo-old-name leo_old_name`
2. 更新所有引用：`grep -r "leo-old-name" . | grep -v ".git"`
3. 重新验证：`python scripts/development/validate_structure.py`

---

### 如果 pre-commit 失败

```bash
$ git commit -m "feat: add feature"

Leo Structure Validation...Failed
- hook id: leo-structure-validation
- exit code: 1
```

**解决步骤**：

1. 查看错误信息
2. 修复问题
3. 重新提交：`git commit -m "feat: add feature"`

---

## 📋 检查清单

### 创建新文件/目录时

- [ ] 使用下划线而非连字符
- [ ] 更新 `leo_system/paths.py`（如果是重要路径）
- [ ] 运行 `python scripts/development/validate_structure.py`

### 重构代码时

- [ ] 更新所有文件引用
- [ ] 更新测试文件
- [ ] 更新路径常量
- [ ] 运行验证脚本
- [ ] 运行测试：`pytest tests/`

### 提交代码前

- [ ] 运行 `python scripts/development/validate_structure.py`
- [ ] 运行 `pytest tests/test_system_basics.py`
- [ ] 提交（pre-commit hooks 会自动验证）

---

## 🎯 成功标准

### 必须达成

- ✅ 所有目录使用下划线命名
- ✅ 所有路径引用使用路径常量
- ✅ 验证脚本通过
- ✅ Pre-commit hooks 配置正确

### 持续维护

- ✅ 每次提交前自动验证
- ✅ 每周运行一次完整验证
- ✅ 新成员入职时学习命名规范

---

## 📚 相关文档

- [开发指南](../leo_knowledge/context/development_guide.md) - 命名规范
- [路径常量](../leo_system/paths.py) - 路径管理
- [验证脚本](../scripts/validate_structure.py) - 结构验证
- [Pre-commit配置](../.pre-commit-config.yaml) - 自动化检查

---

**维护人**: Claude Opus 4.5
**最后更新**: 2026-01-24
**状态**: ✅ 已实施并测试

