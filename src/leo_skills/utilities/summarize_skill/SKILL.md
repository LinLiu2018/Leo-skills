---
name: summarize-skill
description: 内容总结技能。总结 URL、PDF、YouTube 视频、音频内容，快速消化信息。。当用户需要实用工具相关帮助时使用。 [优化第5轮：提升了触发准确率]
category: utilities
author: Leo Liu
metadata:
  version: 1.0.0
  user-invocable: true
  priority: 1
  activation_keywords:
  - 总结
  - summarize
  - 摘要
  - 概括
  - 提炼
  allowed-tools:
  - Web Fetch
  - Read
license: MIT
---

# Summarize Skill - 内容总结

## 功能

- URL 内容总结
- PDF 文档总结
- YouTube 视频总结
- 音频转录总结

## 使用方式

```
用户：总结这个链接的内容
技能：抓取内容 → 提取要点 → 生成摘要
```