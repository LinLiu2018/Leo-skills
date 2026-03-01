---
name: brainstorming_skill
version: "1.1.0"
description: |
  【协作技能】头脑风暴。在任何创造性工作之前必须使用 - 创建功能、构建组件、添加功能或修改行为。
  在实现之前探索用户意图、需求和设计。通过自然协作对话帮助将想法转化为完全形成的设计和规范。
  基于 obra/superpowers 的 brainstorming 技能。
category: collaboration
author: Leo AI System (基于 obra/superpowers)
user-invocable: true
priority: 1
activation_keywords:
  - 头脑风暴
  - 设计讨论
  - 需求探索
  - brainstorming
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

# 头脑风暴（Brainstorming）

## 概述

通过自然协作对话帮助将想法转化为完全形成的设计和规范。

首先了解当前项目上下文，然后一次问一个问题来完善想法。一旦理解了要构建的内容，以小节（200-300 字）呈现设计，每节后检查是否看起来正确。

## 🚫 硬门禁（HARD-GATE）

**在呈现设计并获得用户批准之前，禁止执行任何实现操作！**

- ❌ 禁止调用任何实现技能
- ❌ 禁止编写任何代码
- ❌ 禁止搭建任何项目
- ❌ 禁止采取任何实施行动

**每个项目都必须走这个流程**，无论多么简单。

## ⚠️ 反模式："这太简单不需要设计"

每个项目都要经过这个过程。todo 列表、单功能工具、配置变更——所有这些。"简单"项目是未经检验的假设导致最多工作浪费的地方。设计可以很短（真正简单的项目几句话），但**必须呈现并获得批准**。

## ✅ 检查清单

你必须为每个项目创建任务并按顺序完成：

1. **探索项目上下文** — 检查文件、文档、最近提交
2. **提出澄清问题** — 一次一个，理解目的/约束/成功标准
3. **提出 2-3 种方案** — 包含权衡和你的推荐
4. **呈现设计** — 按复杂度分节，每节后获得用户批准
5. **编写设计文档** — 保存到 `docs/plans/YYYY-MM-DD-<主题>-design.md` 并提交
6. **过渡到实施** — 调用 writing_plans_skill 创建实施计划

## 流程

### 理解想法

- 首先查看当前项目状态（文件、文档、最近提交）
- 一次问一个问题来完善想法
- 可能时首选多项选择题，开放式也可以
- 每条消息只问一个问题 - 如果一个主题需要更多探索，将其分成多个问题
- 专注于理解：目的、约束、成功标准

### 探索方法

- 提出 2-3 种不同的方法及权衡
- 会话式呈现选项，包括推荐和推理
- 以推荐的选项开头并解释原因

### 呈现设计

- 一旦相信理解了要构建的内容，呈现设计
- 将其分成 200-300 字的小节
- 每节后询问是否到目前为止看起来正确
- 涵盖：架构、组件、数据流、错误处理、测试
- 准备好在某些内容不合理时返回并澄清

## 设计之后

### 文档

- 将经过验证的设计写入 `docs/plans/YYYY-MM-DD-<主题>-design.md`
- 如果有，使用 elements-of-style:writing-clearly-and-concisely 技能
- 将设计文档提交到 git

### 实现（如果继续）

- 询问："准备好设置实现了吗？"
- 使用 using-git-worktrees 创建隔离工作区
- 使用 writing-plans 创建详细实施计划

## 关键原则

- **一次一个问题** - 不要用多个问题压倒
- **首选多项选择** - 可能时比开放式更容易回答
- ** ruthless YAGNI** - 从所有设计中移除不必要的功能
- **探索替代方案** - 在确定之前始终提出 2-3 种方法
- **增量验证** - 分节呈现设计，验证每个
- **保持灵活** - 当某些内容不合理时返回并澄清

## 工作流集成

```
头脑风暴 (brainstorming_skill)
    ↓
理解需求 → 探索方法 → 呈现设计
    ↓
文档化设计 → 提交到 git
    ↓
使用 Git Worktree (using_git_worktrees_skill)
    ↓
编写计划 (writing_plans_skill)
    ↓
执行计划 (executing_plans_skill) 或 子代理开发 (subagent_driven_development_skill)
    ↓
完成开发分支 (finishing_development_branch_skill)
```

## 相关技能

- **using_git_worktrees_skill** - 创建隔离工作区
- **writing_plans_skill** - 创建实施计划
- **executing_plans_skill** - 执行计划
- **subagent_driven_development_skill** - 子代理开发
- **finishing_development_branch_skill** - 完成开发分支

## 致谢

基于 [obra/superpowers](https://github.com/obra/superpowers) v4.3.1
