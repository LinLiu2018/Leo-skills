---
name: web-search-enhanced-skill
description: 增强版网络搜索。支持 Brave Search + Tavily API 双引擎，智能并发控制，速率限制优化。。当用户需要实用工具相关帮助时使用。 [优化第5轮：提升了触发准确率]
category: utilities
author: Leo Liu
metadata:
  version: 1.0.0
  user-invocable: true
  priority: 1
  activation_keywords:
  - 搜索
  - web 搜索
  - 联网搜索
  - search
  - tavily
  allowed-tools:
  - Web Search
  - Web Fetch
license: MIT
---

# Web Search Enhanced Skill

## 功能说明

在原有 `web_search_skill` 基础上增强：
- 支持 Tavily API（可选）
- 智能并发控制
- 速率限制优化
- 搜索结果去重

## 使用方式

```
用户：搜索最新 AI 新闻
技能：双引擎搜索 → 去重 → 排序 → 返回结果
```