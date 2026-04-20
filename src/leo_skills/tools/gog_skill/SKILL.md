---
name: gog-skill
description: Google Workspace 集成技能。Gmail、日历、Drive、Docs 全家桶，日常办公/邮件/日程神器。。当用户需要工具集成相关帮助时使用。 [优化第5轮：提升了触发准确率]
category: tools
author: Leo Liu
metadata:
  version: 1.0.0
  user-invocable: true
  priority: 2
  activation_keywords:
  - google
  - Gmail
  - 日历
  - Drive
  - Docs
  - 谷歌
  allowed-tools:
  - Bash
license: MIT
---

# GOG Skill - Google Workspace 集成

## 功能

- Gmail 邮件管理
- Google 日历
- Google Drive
- Google Docs

## 依赖

需要配置 Google API 认证

## 使用方式

```
用户：查看我的 Gmail 未读邮件
技能：调用 Gmail API → 返回邮件列表
```