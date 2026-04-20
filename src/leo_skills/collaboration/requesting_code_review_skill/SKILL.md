---
name: requesting-code-review-skill
description: 【协作技能】请求代码审查。在完成任务、实现主要功能或合并之前使用，以验证工作是否符合要求。
核心理念：早审查，常审查。
基于 obra/superpowers 的 requesting-code-review 技能。
。当用户需要协作与沟通相关帮助时使用。 [优化第5轮：提升了触发准确率]

  核心理念：早审查，常审查。

  基于 obra/superpowers 的 requesting-code-review 技能。

  。当用户需要协作与沟通相关帮助时使用。'
category: collaboration
author: Leo AI System (基于 obra/superpowers)
metadata:
  version: 1.0.0
  user-invocable: true
  priority: 1
  activation_keywords:
  - 代码审查
  - 请求审查
  - code-review
  allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Task
license: MIT
---

# 请求代码审查（Requesting Code Review）

## 概述

分发代码审查子代理以在问题级联之前捕获问题。

**核心理念**：早审查，常审查。

## 何时请求审查

**必需**：
- 子代理驱动开发中每个任务后
- 主要功能完成后
- 合并到主分支之前

**可选但有价值**：
- 卡住时（新视角）
- 重构前（基线检查）
- 复杂 bug 修复后

## 如何请求

**1. 获取 git SHAs**：
```bash
BASE_SHA=$(git rev-parse HEAD~1)  # 或 origin/main
HEAD_SHA=$(git rev-parse HEAD)
```

**2. 分派代码审查子代理**：

使用 Task 工具和 code-reviewer 类型，填充 `code-reviewer.md` 中的模板。

**占位符**：
- `{WHAT_WAS_IMPLEMENTED}` - 你刚刚构建了什么
- `{PLAN_OR_REQUIREMENTS}` - 它应该做什么
- `{BASE_SHA}` - 起始提交
- `{HEAD_SHA}` - 结束提交
- `{DESCRIPTION}` - 简要总结

**3. 处理反馈**：
- 立即修复关键问题
- 继续之前修复重要问题
- 记录次要问题以供以后处理
- 如果审查者错误则反驳（带推理）

## 示例

```
[刚刚完成任务 2：添加验证函数]

你：在继续之前让我请求代码审查。

BASE_SHA=$(git log --oneline | grep "Task 1" | head -1 | awk '{print $1}')
HEAD_SHA=$(git rev-parse HEAD)

[分派代码审查子代理]
  WHAT_WAS_IMPLEMENTED: 对话索引的验证和修复函数
  PLAN_OR_REQUIREMENTS: 来自 docs/plans/deployment-plan.md 的任务 2
  BASE_SHA: a7981ec
  HEAD_SHA: 3df7661
  DESCRIPTION: 添加了 verifyIndex() 和 repairIndex()，支持 4 种问题类型

[子代理返回]：
  优点：架构干净，有真实测试
  问题：
    重要：缺少进度指示器
    次要：魔法数字（100）用于报告间隔
  评估：准备好继续

你：[修复进度指示器]
[继续任务 3]
```

## 与工作流集成

**子代理驱动开发**：
- 每个任务后审查
- 在问题累积之前捕获
- 修复后再进行下一个任务

**执行计划**：
- 每个批次（3 个任务）后审查
- 获取反馈，应用，继续

**临时开发**：
- 合并前审查
- 卡住时审查

## 红旗

**永远不要**：
- 因为"简单"而跳过审查
- 忽略关键问题
- 继续未修复的重要问题
- 与有效的技术反馈争论

**如果审查者错误**：
- 用技术推理反驳
- 显示证明其有效的代码/测试
- 请求澄清

## 相关技能

- **subagent_driven_development_skill** - 子代理开发（每个任务后审查）
- **receiving_code_review_skill** - 接收代码审查反馈
- **finishing_development_branch_skill** - 完成开发分支

## 致谢

基于 [obra/superpowers](https://github.com/obra/superpowers) 项目