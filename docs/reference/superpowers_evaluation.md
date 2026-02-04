# obra/superpowers 技能库评估

> 评估日期: 2026-01-29
> 来源: https://github.com/obra/superpowers

---

## 概览

**obra/superpowers** 是一个专业的 Claude Code 技能库，专注于软件开发工作流的系统化实践。由 Keybase 创始人 Jesse Vincent 开发维护，包含 **13个核心技能**。

### 安装方式

```bash
# Claude Code
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

---

## 技能清单与分类

### 1. 测试驱动开发 (Test-Driven Development)

| 技能 | 用途 |
|------|------|
| **test-driven-development** | RED-GREEN-REFACTOR 循环，包含测试反模式参考 |

### 2. 调试类 (Debugging)

| 技能 | 用途 |
|------|------|
| **systematic-debugging** | 四阶段根因分析（根因追踪、纵深防御、条件等待技术） |
| **verification-before-completion** | 确保问题真正修复 |

### 3. 协作类 (Collaboration)

| 技能 | 用途 |
|------|------|
| **brainstorming** | 苏格拉底式设计精炼 |
| **writing-plans** | 详细实施计划 |
| **executing-plans** | 分批执行与检查点 |
| **dispatching-parallel-agents** | 并发子代理工作流 |
| **requesting-code-review** | 预审清单 |
| **receiving-code-review** | 响应反馈 |
| **using-git-worktrees** | 并行开发分支 |
| **finishing-a-development-branch** | 合并/PR决策工作流 |
| **subagent-driven-development** | 两阶段审查（规范符合性→代码质量） |

### 4. 元技能 (Meta-Skills)

| 技能 | 用途 |
|------|------|
| **writing-skills** | 创建新技能最佳实践 |
| **using-superpowers** | 技能系统介绍 |

---

## 核心工作流

```
brainstorming → using-git-worktrees → writing-plans → executing-plans
     ↓                                            ↓
test-driven-development              finishing-a-development-branch
```

**代理在每个任务前自动检查相关技能**，这是强制工作流而非建议。

---

## 与 Leo System 的互补性分析

### Leo System 现有技能

| 分类 | 技能 |
|------|------|
| **核心** | planning_with_files_skill, fresh_start_skill, phase_* |
| **测试** | code_verification_skill, auto_verify_skill, unit_test_generator_skill |
| **脚手架** | bootstrap_skill, setup_skill, fullstack_project_scaffold_skill |

### obra/superpowers 补充价值

| 缺失领域 | superpowers 解决方案 |
|----------|---------------------|
| TDD 实践 | `test-driven-development` |
| 系统化调试 | `systematic-debugging` (四阶段根因分析) |
| 协作审代码 | `requesting-code-review`, `receiving-code-review` |
| Git 工作流 | `using-git-worktrees`, `finishing-a-development-branch` |
| 子代理开发 | `subagent-driven-development`, `dispatching-parallel-agents` |
| 技能创建 | `writing-skills` |

---

## 详细技能评估

### ⭐ 强烈推荐集成 (Top Priority)

#### 1. systematic-debugging (系统化调试)
**评估**: ⭐⭐⭐⭐⭐

**亮点**:
- 四阶段流程：根因调查 → 模式分析 → 假设验证 → 实施修复
- "铁律"：没有根因调查就不允许修复
- 包含高级技术：根因追踪、纵深防御、条件等待
- 实测数据：首次修复率 95% vs 40%，新 bug 引入接近零

**与 Leo System 集成**: 可直接使用，或整合到现有 `security_scan_skill`

#### 2. test-driven-development (测试驱动开发)
**评估**: ⭐⭐⭐⭐⭐

**亮点**:
- RED-GREEN-REFACTOR 循环
- 包含测试反模式参考
- 与 `unit_test_generator_skill` 互补

**与 Leo System 集成**: 增强现有测试技能

#### 3. writing-plans (编写计划)
**评估**: ⭐⭐⭐⭐⭐

**亮点**:
- 详细的实施计划模板
- "小步任务"粒度（每步2-5分钟）
- 精确文件路径、完整代码示例、预期输出
- 支持两种执行模式：子代理驱动 / 并行会话

**与 Leo System 集成**: 可与 `planning_with_files_skill` 互补

### ⭐ 推荐集成

#### 4. executing-plans (执行计划)
**评估**: ⭐⭐⭐⭐

**亮点**:
- 批量执行 + 检查点审查
- 清晰的停止和求助时机
- 与 writing-plans 形成完整闭环

#### 5. using-git-worktrees (Git 工作树)
**评估**: ⭐⭐⭐⭐

**亮点**:
- 并行开发分支管理
- 避免污染主分支

#### 6. finishing-a-development-branch (完成开发分支)
**评估**: ⭐⭐⭐⭐

**亮点**:
- 合并/PR 决策工作流
- 自动化测试验证

### ⭐ 可选集成

#### 7-13. 其他协作技能
- brainstorming: 设计头脑风暴
- requesting-code-review: 代码审查请求
- receiving-code-review: 代码审查响应
- dispatching-parallel-agents: 并发子代理
- subagent-driven-development: 子代理开发
- verification-before-completion: 完成前验证
- writing-skills: 技能编写

---

## 集成建议

### 方案 A：完整集成 (推荐)

将所有 13 个技能复制到 Leo System 技能目录：

```bash
src/leo_skills/testing/test_driven_development_skill/
src/leo_skills/debugging/systematic_debugging_skill/
src/leo_skills/debugging/verification_before_completion_skill/
src/leo_skills/collaboration/brainstorming_skill/
src/leo_skills/collaboration/writing_plans_skill/
src/leo_skills/collaboration/executing_plans_skill/
src/leo_skills/collaboration/dispatching_parallel_agents_skill/
src/leo_skills/collaboration/requesting_code_review_skill/
src/leo_skills/collaboration/receiving_code_review_skill/
src/leo_skills/collaboration/using_git_worktrees_skill/
src/leo_skills/collaboration/finishing_development_branch_skill/
src/leo_skills/collaboration/subagent_driven_development_skill/
src/leo_skills/meta/writing_skills_skill/
```

### 方案 B：选择性集成

只集成最核心的 3-5 个技能：
- systematic-debugging
- test-driven-development
- writing-plans
- executing-plans
- using-git-worktrees

---

## 推荐行动计划

1. **立即集成** (Phase 1):
   - systematic-debugging → `src/leo_skills/debugging/systematic_debugging_skill/`
   - test-driven-development → `src/leo_skills/testing/test_driven_development_skill/`

2. **核心工作流** (Phase 2):
   - writing-plans → `src/leo_skills/collaboration/writing_plans_skill/`
   - executing-plans → `src/leo_skills/collaboration/executing_plans_skill/`

3. **Git 工作流** (Phase 3):
   - using-git-worktrees → `src/leo_skills/devops/using_git_worktrees_skill/`
   - finishing-development-branch → `src/leo_skills/devops/finishing_development_branch_skill/`

4. **可选扩展** (Phase 4):
   - 剩余协作技能

---

## 风险与注意事项

1. **学习曲线**: 部分技能有严格的流程要求，需要时间适应
2. **流程强制**: 代理会自动检查相关技能，可能与现有习惯冲突
3. **Git 依赖**: using-git-worktrees 依赖 Git worktrees 功能
4. **文件路径**: writing-plans 要求精确的文件路径，可能增加规划时间

---

## 结论

** obra/superpowers ** 是高质量的专业技能库，特别适合：
- 追求代码质量的团队
- 需要系统化调试流程的项目
- 重视 TDD 和代码审查的工作流

**与 Leo System 高度互补**，建议完整集成以增强系统的专业开发能力。
