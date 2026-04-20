---
name: skill-deduplication-skill
description: 技能去重检查。扫描所有技能，检测功能重复和命名冲突，提供合并建议。。当用户需要工具集成相关帮助时使用。 [优化第5轮：提升了触发准确率]
category: tools
author: Leo Liu
metadata:
  version: 1.0.0
  user-invocable: true
  priority: 1
  activation_keywords:
  - 技能去重
  - 检查重复技能
  - 技能合并
  - 命名冲突检查
  allowed-tools:
  - Read
  - Write
  - Bash
license: MIT
---

# Skill Deduplication Skill

## 功能说明

扫描 Leo AI 系统所有技能，检测功能重复和命名冲突，提供合并建议。

## 使用方式

```
用户：检查有没有重复的技能
技能：扫描所有技能 → 分析功能 → 检测重复 → 提供建议
```

## 检查项

1. **命名冲突**: 目录名/文件名重复
2. **功能重复**: 描述相似、触发词重叠
3. **能力重叠**: 多个技能实现相同功能

## 输出

- 重复技能列表
- 合并建议
- 命名冲突报告