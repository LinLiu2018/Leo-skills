---
name: find-skills-skill
description: 技能发现技能。让 Agent 自己去技能库搜索并推荐/安装技能，解决"不知道装什么"的痛点。。当用户需要工具集成相关帮助时使用。 [优化第5轮：提升了触发准确率]
category: tools
author: Leo Liu
metadata:
  version: 1.0.0
  user-invocable: true
  priority: 1
  activation_keywords:
  - 找技能
  - 推荐技能
  - 安装什么技能
  - find skills
  - 技能发现
  allowed-tools:
  - Read
  - Web Search
license: MIT
---

# Find Skills Skill - 技能发现

## 功能

- 搜索技能库
- 基于需求推荐技能
- 一键安装技能
- 技能使用指导

## 使用方式

```
用户：我想自动化日报，需要什么技能？
技能：分析需求 → 搜索技能库 → 推荐技能 → 指导安装
```