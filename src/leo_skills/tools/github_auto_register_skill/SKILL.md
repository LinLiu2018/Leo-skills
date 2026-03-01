---
name: github_auto_register_skill
version: 1.0.0
description: GitHub 技能自动注册。自动扫描、评估、下载、注册 GitHub 热门 Claude 技能到 Leo AI 系统。
category: tools
author: Leo Liu
user-invocable: true
priority: 1
activation_keywords:
  - github 自动注册
  - 技能自动集成
  - github 技能加载
  - 自动获取技能
allowed-tools:
  - Read
  - Write
  - Bash
  - web_search
---

# GitHub Auto Register Skill

## 功能说明

自动扫描 GitHub 热门 Claude 技能，评估质量后自动下载并注册到 Leo AI 系统。

## 使用方式

```
用户：自动注册 GitHub 热门技能
技能：开始扫描 GitHub → 评估质量 → 下载 → 注册 → 更新索引
```

## 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| min_stars | 50 | 最少 Star 数 |
| max_age_days | 90 | 最大更新时间（天） |
| auto_mode | false | 是否自动注册（true=自动，false=手动确认） |

## 工作流程

1. 扫描 GitHub 热门 Claude 技能仓库
2. 评估质量（Star 数、更新时间、描述完整度）
3. 检查功能重复（对比现有技能）
4. 下载技能文件
5. 注册到 `src/leo_skills/` 目录
6. 更新 `capability_index.md`

## 输出

- 成功注册的技能列表
- 跳过的技能及原因
- 错误日志
