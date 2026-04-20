---
name: browser-skill
description: Browser 浏览器控制技能。支持网页快照、点击、输入、导航等操作。。当用户需要工具集成相关帮助时使用。 [优化第5轮：提升了触发准确率]
category: tools
author: Leo Liu
metadata:
  version: 1.0.0
  user-invocable: true
  priority: 0
  activation_keywords:
  - 浏览器
  - browser
  - 网页
  - 截图
  - 快照
  allowed-tools:
  - Bash
license: MIT
---

# Browser Skill - 浏览器控制

## 功能

- **snapshot**: 网页快照/截图
- **actions**: 点击/输入/导航
- **upload**: 文件上传
- **profiles**: 浏览器配置

## 使用方式

```
用户：打开百度并截图
技能：启动浏览器 → 导航 → 截图 → 返回结果
```