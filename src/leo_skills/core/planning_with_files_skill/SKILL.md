---
name: planning_with_files_skill
version: "1.0.0"
description: |
  【核心技能】Manus风格的持久化规划技能。通过三个Markdown文件（task_plan.md、findings.md、progress.md）
  实现任务规划、发现记录和进度跟踪。适用于复杂多步骤任务、研究项目或需要>5次工具调用的任务。
  核心理念：Context Window = RAM（易失、有限），Filesystem = Disk（持久、无限）
  这是Leo AI System的上下文工程基础设施，让整个系统具备"外部记忆"能力。
category: core
author: Leo AI System (基于 OthmanAdi/planning-with-files)
user-invocable: true
priority: 1
activation_keywords:
  - 规划任务
  - 创建计划
  - 任务规划
  - planning
  - 开始复杂任务
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - WebFetch
  - WebSearch
---

# Planning with Files Skill（持久化规划技能）

## 核心理念

```
Context Window = RAM（易失、有限）
Filesystem = Disk（持久、无限）

→ 任何重要信息都写入磁盘
```

这是 Meta 以 20 亿美元收购 Manus 背后的核心技术 —— **上下文工程**（Context Engineering）。

## 三文件模式

| 文件 | 用途 | 更新时机 |
|------|------|----------|
| `task_plan.md` | 阶段、进度、决策 | 每个阶段完成后 |
| `findings.md` | 研究、发现 | 任何发现后 |
| `progress.md` | 会话日志、测试结果 | 整个会话期间 |

## 快速开始

在任何复杂任务开始前：

1. **创建 `task_plan.md`** — 使用 [templates/task_plan.md](templates/task_plan.md)
2. **创建 `findings.md`** — 使用 [templates/findings.md](templates/findings.md)
3. **创建 `progress.md`** — 使用 [templates/progress.md](templates/progress.md)
4. **决策前重读计划** — 刷新注意力窗口中的目标
5. **每阶段后更新** — 标记完成，记录错误

## 关键规则

### 1. 先创建计划
永远不要在没有 `task_plan.md` 的情况下开始复杂任务。这是不可协商的。

### 2. 2-动作规则
> "每2次查看/浏览/搜索操作后，立即将关键发现保存到文件。"

这防止视觉/多模态信息丢失。

### 3. 决策前阅读
在重大决策前，阅读计划文件。这让目标保持在注意力窗口中。

### 4. 行动后更新
完成任何阶段后：
- 标记阶段状态：`in_progress` → `complete`
- 记录遇到的任何错误
- 记录创建/修改的文件

### 5. 记录所有错误
每个错误都进入计划文件。这建立知识并防止重复。

```markdown
## 遇到的错误
| 错误 | 尝试次数 | 解决方案 |
|------|----------|----------|
| FileNotFoundError | 1 | 创建默认配置 |
| API超时 | 2 | 添加重试逻辑 |
```

### 6. 永不重复失败
```
if action_failed:
    next_action != same_action
```
跟踪你尝试过的。改变方法。

## 3-Strike 错误协议

```
尝试1：诊断并修复
  → 仔细阅读错误
  → 识别根本原因
  → 应用针对性修复

尝试2：替代方法
  → 同样的错误？尝试不同方法
  → 不同的工具？不同的库？
  → 永不重复完全相同的失败操作

尝试3：更广泛的重新思考
  → 质疑假设
  → 搜索解决方案
  → 考虑更新计划

3次失败后：升级给用户
  → 解释你尝试了什么
  → 分享具体错误
  → 请求指导
```

## 5问题重启测试

如果你能回答这些，你的上下文管理是可靠的：

| 问题 | 答案来源 |
|------|----------|
| 我在哪里？ | task_plan.md 中的当前阶段 |
| 我要去哪里？ | 剩余阶段 |
| 目标是什么？ | 计划中的目标声明 |
| 我学到了什么？ | findings.md |
| 我做了什么？ | progress.md |

## 何时使用此模式

**使用于：**
- 多步骤任务（3+步骤）
- 研究任务
- 构建/创建项目
- 跨越多次工具调用的任务
- 任何需要组织的事情

**跳过于：**
- 简单问题
- 单文件编辑
- 快速查找

## 反模式

| 不要 | 改为 |
|------|------|
| 使用 TodoWrite 进行持久化 | 创建 task_plan.md 文件 |
| 只说一次目标然后忘记 | 决策前重读计划 |
| 隐藏错误并静默重试 | 将错误记录到计划文件 |
| 把所有东西塞进上下文 | 将大内容存储在文件中 |
| 立即开始执行 | 先创建计划文件 |
| 重复失败的操作 | 跟踪尝试，改变方法 |

## 模板

- [templates/task_plan.md](templates/task_plan.md) — 阶段跟踪
- [templates/findings.md](templates/findings.md) — 研究存储
- [templates/progress.md](templates/progress.md) — 会话日志

## 与Leo System集成

此技能可与Leo System的其他组件配合使用：

- **research_agent**: 调研时使用 findings.md 记录发现
- **content_pipeline**: 内容创作时使用 task_plan.md 跟踪进度
- **realestate_pipeline**: 房产营销项目使用完整三文件模式

## 致谢

基于 [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) 项目
