---
name: finishing-development-branch-skill
description: 【DevOps技能】完成开发分支。当实现完成、所有测试通过，需要决定如何集成工作时使用。
核心理念：验证测试 → 呈现选项 → 执行选择 → 清理。
基于 obra/superpowers 的 finishing-a-development-branch 技能。
 [优化第5轮：提升了触发准确率]

  核心理念：验证测试 → 呈现选项 → 执行选择 → 清理。

  基于 obra/superpowers 的 finishing-a-development-branch 技能。

  '
category: devops
author: Leo AI System (基于 obra/superpowers)
metadata:
  version: 1.0.0
  user-invocable: true
  priority: 1
  activation_keywords:
  - 完成分支
  - 合并分支
  - 推送代码
  - finishing-branch
  allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
license: MIT
---

# 完成开发分支（Finishing a Development Branch）

## 概述

通过呈现清晰的选项和处理选定的工作流来指导完成开发工作。

**核心理念**：验证测试 → 呈现选项 → 执行选择 → 清理。

**开始时宣布**："我正在使用 finishing-deveopment-branch 技能来完成这项工作。"

## 流程

### 步骤 1：验证测试

**在呈现选项之前，验证测试通过**：

```bash
# 运行项目测试套件
npm test / cargo test / pytest / go test ./...
```

**如果测试失败**：
```
测试失败（<N> 个失败）。必须在完成之前修复：

[显示失败]

在测试通过之前不能继续合并/PR。
```

停止。不要进入步骤 2。

**如果测试通过**：继续步骤 2。

### 步骤 2：确定基础分支

```bash
# 尝试常见基础分支
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

或询问："这个分支从 main 分叉出来 - 正确吗？"

### 步骤 3：呈现选项

呈现 exactly 这 4 个选项：

```
实现完成。您想做什么？

1. 在本地合并回 <base-branch>
2. 推送并创建 Pull Request
3. 保持分支原样（我之后处理）
4. 放弃此工作

哪个选项？
```

**不要添加解释** - 保持选项简洁。

### 步骤 4：执行选择

#### 选项 1：本地合并

```bash
# 切换到基础分支
git checkout <base-branch>

# 拉取最新
git pull

# 合并功能分支
git merge <feature-branch>

# 验证合并结果的测试
<test command>

# 如果测试通过
git branch -d <feature-branch>
```

然后：清理 worktree（步骤 5）

#### 选项 2：推送并创建 PR

```bash
# 推送分支
git push -u origin <feature-branch>

# 创建 PR
gh pr create --title "<title>" --body "$(cat <<'EOF'
## 总结
<2-3 个变更点>

## 测试计划
- [ ] <验证步骤>
EOF
)"
```

然后：清理 worktree（步骤 5）

#### 选项 3：保持原样

报告："保持分支 <name>。Worktree 保存在 <path>。"

**不要清理 worktree。**

#### 选项 4：放弃

**首先确认**：
```
这将永久删除：
- 分支 <name>
- 所有提交：<commit-list>
- <path> 处的 worktree

输入 'discard' 确认。
```

等待确切确认。

如果确认：
```bash
git checkout <base-branch>
git branch -D <feature-branch>
```

然后：清理 worktree（步骤 5）

### 步骤 5：清理 Worktree

**对于选项 1、2、4**：

检查是否在 worktree 中：
```bash
git worktree list | grep $(git branch --show-current)
```

如果是：
```bash
git worktree remove <worktree-path>
```

**对于选项 3**：保持 worktree。

## 快速参考

| 选项 | 合并 | 推送 | 保持 Worktree | 清理分支 |
|------|------|------|---------------|---------|
| 1. 本地合并 | ✓ | - | - | ✓ |
| 2. 创建 PR | - | ✓ | ✓ | - |
| 3. 保持原样 | - | - | ✓ | - |
| 4. 放弃 | - | - | - | ✓ (强制) |

## 常见错误

**跳过测试验证**
- **问题**：合并损坏的代码，创建失败的 PR
- **修复**：在提供选项之前始终验证测试

**开放式问题**
- **问题**："我接下来应该做什么？" → 歧义
- **修复**：呈现 exactly 4 个结构化选项

**自动清理 worktree**
- **问题**：当可能需要时移除 worktree（选项 2、3）
- **修复**：仅清理选项 1 和 4

**放弃时无确认**
- **问题**：意外删除工作
- **修复**：要求输入 "discard" 确认

## 红旗

**永远不要**：
- 继续失败的测试
- 不验证结果测试就合并
- 不确认就删除工作
- 未经明确请求强制推送

**始终**：
- 在提供选项之前验证测试
- 呈现 exactly 4 个选项
- 对选项 4 获取输入的确认
- 仅清理选项 1 和 4 的 worktree

## 集成

**被调用**：
- **subagent_driven_development_skill**（第7步）- 所有任务完成后
- **executing_plans_skill**（步骤5）- 所有批次完成后

**与以下配对**：
- **using_git_worktrees_skill** - 清理该技能创建的 worktree

## 工作流集成

```
使用 Git Worktrees (using_git_worktrees_skill)
        ↓
执行计划 (executing_plans_skill) 或 子代理开发 (subagent_driven_development_skill)
        ↓
完成开发分支 (finishing_development_branch_skill)
        ↓
合并/PR/清理
```

## 相关技能

- **using_git_worktrees_skill** - 创建工作树
- **executing_plans_skill** - 执行计划
- **subagent_driven_development_skill** - 子代理开发

## 致谢

基于 [obra/superpowers](https://github.com/obra/superpowers) 项目