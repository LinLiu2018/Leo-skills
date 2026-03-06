---
name: finishing_development_branch_skill
description: 【协作技能】完成开发分支。在实现完成、所有测试通过后使用 - 展示结构化选项用于合并、PR或清理。基于 obra/superpowers v4.3.1
---

# 完成开发分支（Finishing a Development Branch）

## 概述

指导完成开发工作，提供清晰的选项并处理选中的工作流。

**核心原则：** 验证测试 → 展示选项 → 执行选择 → 清理。

**开始时宣布：** "我正在使用 finishing_development_branch_skill 来完成这项工作。"

## 流程

### 步骤 1：验证测试

**在展示选项之前，验证测试通过：**

```bash
# 运行项目测试套件
npm test / cargo test / pytest / go test ./...
```

**如果测试失败：**
```
测试失败 (<N> 个失败)。必须修复后才能完成：

[显示失败]

在测试通过之前无法继续合并/PR。
```

停止。不要继续到步骤 2。

**如果测试通过：** 继续到步骤 2。

### 步骤 2：确定基础分支

```bash
# 尝试常见基础分支
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

或者询问："这个分支是从 main 分叉的——正确吗？"

### 步骤 3：展示选项

精确展示这 4 个选项：

```
实现完成。你想怎么做？

1. 本地合并回 <base-branch>
2. 推送并创建 Pull Request
3. 保持分支原样（稍后我来处理）
4. 丢弃这项工作

选择哪个选项？
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

# 验证合并后的测试
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
## 摘要
<2-3 个变更要点>

## 测试计划
- [ ] <验证步骤>
EOF
)"
```

然后：清理 worktree（步骤 5）

#### 选项 3：保持原样

报告："保持分支 <name>。Worktree 保留在 <path>。"

**不要清理 worktree。**

#### 选项 4：丢弃

**首先确认：**
```
这将永久删除：
- 分支 <name>
- 所有提交：<commit-list>
- Worktree 在 <path>

输入 'discard' 确认。
```

等待精确确认。

如果确认：
```bash
git checkout <base-branch>
git branch -D <feature-branch>
```

然后：清理 worktree（步骤 5）

### 步骤 5：清理 Worktree

**对于选项 1, 2, 4：**

检查是否在 worktree 中：
```bash
git worktree list | grep $(git branch --show-current)
```

如果是：
```bash
git worktree remove <worktree-path>
```

**对于选项 3：** 保留 worktree。

## 快速参考

| 选项 | 合并 | 推送 | 保留Worktree | 清理分支 |
|------|------|------|-------------|----------|
| 1. 本地合并 | ✓ | - | - | ✓ |
| 2. 创建PR | - | ✓ | ✓ | - |
| 3. 保持原样 | - | - | ✓ | - |
| 4. 丢弃 | - | - | - | ✓ (强制) |

## 常见错误

**跳过测试验证**
- **问题：** 合并损坏的代码，创建失败的 PR
- **修复：** 始终在展示选项前验证测试

**开放式问题**
- **问题：** "我接下来该做什么？" → 模糊
- **修复：** 展示精确的 4 个结构化选项

**自动清理 worktree**
- **问题：** 可能需要时删除 worktree（选项 2, 3）
- **修复：** 仅对选项 1 和 4 清理

**丢弃时不确认**
- **问题：** 意外删除工作
- **修复：** 要求输入 "discard" 确认

## 红旗

**永远不要：**
- 在测试失败时继续
- 不验证结果测试就合并
- 不确认就删除工作
- 不经明确要求就强制推送

**始终：**
- 在展示选项前验证测试
- 精确展示 4 个选项
- 对选项 4 获取输入的确认
- 仅对选项 1 和 4 清理 worktree

## 集成

**被调用：**
- **subagent_driven_development_skill**（步骤 7）- 所有任务完成后
- **executing_plans_skill**（步骤 5）- 所有批次完成后

**配合：**
- **using_git_worktrees_skill** - 清理该技能创建的 worktree

## 致谢

基于 [obra/superpowers](https://github.com/obra/superpowers) v4.3.1
