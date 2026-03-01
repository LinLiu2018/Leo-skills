---
name: content_to_action_skill
version: 1.0.0
description: 内容转化技能。将 X 平台/社交媒体内容转化为学习笔记和实战行动计划。
category: tools
author: Leo Liu
user-invocable: true
priority: 1
activation_keywords:
  - 内容转化
  - 学习转化
  - 实战转化
  - 行动转化
  - content to action
allowed-tools:
  - Read
  - Write
  - Web Fetch
---

# Content to Action Skill

## 功能

- **学习笔记**: 将推文/文章转化为结构化笔记
- **行动计划**: 提取可执行项，生成 TODO 列表
- **知识网站**: 创建知识学习网站 (集成 knowledge_site_creator)
- **趋势分析**: 分析内容趋势和热点

## 使用方式

```
用户：将这条推文转化为学习笔记
技能：提取知识点 → 组织结构 → 生成笔记
```
