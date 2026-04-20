---
name: github-integration-skill
description: GitHub 集成技能，管理代码仓库和协作。当用户需要管理 GitHub 仓库、处理 Pull Request、查看 Issues 或自动化工作流时使用。 [优化第5轮：提升了触发准确率]
category: tools
author: Leo Liu
metadata:
  version: 1.0.0
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
license: MIT
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

## 使用示例

### 示例 1：查看 Issues
```
用户：查看我仓库的未关闭 Issues
技能：正在获取 Issues...
      📋 未关闭 Issues：12 个
      - 高优先级：3 个
      - 需要回复：5 个
      - Bug 报告：4 个
      详情已整理到表格
```

### 示例 2：处理 Pull Request
```
用户：帮我审查这个 PR
技能：正在分析代码变更...
      🔍 审查报告：
      - 变更文件：8 个
      - 新增代码：350 行
      - 潜在问题：2 个
      - 建议改进：3 处
      详细审查意见已生成
```
