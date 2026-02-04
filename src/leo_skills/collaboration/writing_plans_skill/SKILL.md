---
name: writing_plans_skill
version: "1.0.0"
description: |
  【协作技能】编写详细的实施计划。当你有多步骤任务的规格或需求时，在接触代码之前使用。
  核心理念：假设工程师对代码库零上下文，文档化他们需要知道的一切。提供小步任务粒度。
  基于 obra/superpowers 的 writing-plans 技能。
category: collaboration
author: Leo AI System (基于 obra/superpowers)
user-invocable: true
priority: 1
activation_keywords:
  - 写计划
  - 制定计划
  - 创建计划
  - 实施计划
  - writing-plans
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

# 编写计划（Writing Plans）

## 概述

编写全面的实施计划，假设工程师对我们的代码库零上下文且品味有待商榷。文档化他们需要知道的一切：每个任务要接触哪些文件、代码、测试、可能需要检查的文档、如何测试。将整个计划提供为小步任务。DRY。YAGNI。TDD。频繁提交。

假设他们是有技能的开发者，但对我们的工具集或问题领域几乎一无所知。假设他们不太了解好的测试设计。

**开始时宣布**："我正在使用 writing-plans 技能来创建实施计划。"

**上下文**：这应该在专用 worktree 中运行（由头脑风暴技能创建）。

**保存计划到**：`docs/plans/YYYY-MM-DD-<功能名>.md`

## 小步任务粒度

**每个步骤是一个动作（2-5 分钟）**：
- "写失败的测试" - 步骤
- "运行它确保失败" - 步骤
- "编写最少代码让测试通过" - 步骤
- "运行测试确保通过" - 步骤
- "提交" - 步骤

## 计划文档头部

**每个计划必须以此头部开始**：

```markdown
# [功能名] 实施计划

> **For Claude:** REQUIRED SUB-SKILL: 使用 executing_plans_skill 逐任务实施此计划。

**目标**：[一句话描述构建什么]

**架构**：[关于方法的 2-3 句话]

**技术栈**：[关键技术和库]

---
```

## 任务结构

```markdown
### 任务 N：[组件名]

**文件**：
- 创建：`exact/path/to/file.py`
- 修改：`exact/path/to/existing.py:123-145`
- 测试：`tests/exact/path/to/test.py`

**步骤 1：编写失败的测试**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**步骤 2：运行测试验证失败**

运行：`pytest tests/path/test.py::test_name -v`
预期：FAIL "function not defined"

**步骤 3：编写最少实现**

```python
def function(input):
    return expected
```

**步骤 4：运行测试验证通过**

运行：`pytest tests/path/test.py::test_name -v`
预期：PASS

**步骤 5：提交**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
```

## 记住

- 始终使用精确的文件路径
- 计划中提供完整代码（不是"添加验证"）
- 提供精确命令和预期输出
- 使用 @ 语法引用相关技能
- DRY、YAGNI、TDD、频繁提交

## 执行交接

保存计划后，提供执行选择：

**"计划完成并保存到 `docs/plans/<filename>.md`。两种执行方式：**

**1. 子代理驱动（此会话）** - 我为每个任务分派新的子代理，任务间审查，快速迭代

**2. 并行会话（独立）** - 打开新会话使用 executing-plans，批量执行带检查点

**选择哪种方式？**

**如果选择子代理驱动**：
- **必需子技能**：使用 subagent_driven_development_skill
- 保持在此会话中
- 每个任务新子代理 + 代码审查

**如果选择并行会话**：
- 指导他们打开新会话中的 worktree
- **必需子技能**：新会话使用 executing_plans_skill

## 工作流程集成

### 与 TDD 集成

每个任务应遵循 TDD 模式：

1. 编写失败的测试
2. 验证测试失败
3. 编写最少实现
4. 验证测试通过
5. 重构（如需要）
6. 提交

### 与三阶段工作流集成

**计划阶段**：
- 使用 writing_plans_skill 创建 EXECUTION_PLAN.md
- 使用 phase_prep_skill 检查准备情况

**执行阶段**：
- 使用 phase_start_skill 执行任务
- 使用 executing_plans_skill（批量执行）

**检查阶段**：
- 使用 phase_checkpoint_skill 验证

## 示例计划

### 示例：用户认证功能

```markdown
# 用户认证功能 实施计划

> **For Claude:** REQUIRED SUB-SKILL: 使用 executing_plans_skill 逐任务实施此计划。

**目标**：实现用户登录、注册和登出功能

**架构**：使用 JWT 进行会话管理，密码 bcrypt 加密

**技术栈**：Python, FastAPI, JWT, bcrypt

---

### 任务 1：用户模型

**文件**：
- 创建：`src/models/user.py`
- 测试：`tests/models/test_user.py`

**步骤 1：编写失败的测试**

```python
def test_user_creation():
    user = User(email="test@example.com", password="plainpassword")
    assert user.email == "test@example.com"
```

**步骤 2：运行测试验证失败**

运行：`pytest tests/models/test_user.py::test_user_creation -v`
预期：FAIL "User not defined"

**步骤 3：编写最少实现**

```python
class User:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
```

**步骤 4：运行测试验证通过**

运行：`pytest tests/models/test_user.py::test_user_creation -v`
预期：PASS

**步骤 5：提交**

```bash
git add src/models/user.py tests/models/test_user.py
git commit -m "feat: add User model"
```

---

### 任务 2：密码加密

（继续详细的任务步骤...）
```

## 相关技能

- **executing_plans_skill** - 执行计划
- **test_driven_development_skill** - TDD 实践
- **phase_prep_skill** - 阶段准备
- **phase_start_skill** - 阶段执行
- **phase_checkpoint_skill** - 阶段检查点
- **subagent_driven_development_skill** - 子代理开发

## 致谢

基于 [obra/superpowers](https://github.com/obra/superpowers) 项目
