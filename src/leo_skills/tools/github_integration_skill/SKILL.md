---
name: github_integration_skill
version: 1.0.0
description: GitHub 集成技能。搜索代码/仓库、管理 Issue/PR、创建/更新仓库，基于 gh CLI。
category: tools
author: Leo Liu
user-invocable: true
priority: 1
activation_keywords:
  - github
  - GitHub
  - 代码搜索
  - issue
  - PR
  - 仓库
allowed-tools:
  - Bash
  - Read
  - Write
---

# GitHub Integration Skill

## 功能说明

基于 GitHub CLI (gh) 的集成技能：
- 搜索代码和仓库
- 管理 Issue 和 Pull Request
- 创建和更新仓库
- 查看 CI/CD 状态

## 依赖

需要安装 GitHub CLI: `gh`

## 使用方式

```
用户：搜索 Python 机器学习项目
技能：调用 gh search repos → 返回结果
```
