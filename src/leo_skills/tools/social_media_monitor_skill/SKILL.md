---
name: social_media_monitor_skill
version: 1.0.0
description: 多平台社交媒体监控技能。监控 X/公众号/视频号/抖音/小红书账号内容，支持竞品对标分析。
category: tools
author: Leo Liu
user-invocable: true
priority: 0
activation_keywords:
  - 社交媒体监控
  - 账号监控
  - 竞品分析
  - 内容监控
  - 账号内容检测
allowed-tools:
  - Web Search
  - Web Fetch
  - Read
  - Write
---

# Social Media Monitor Skill

## 功能说明

监控多平台社交媒体账号内容，包括：
- X (Twitter) 账号
- 微信公众号
- 视频号
- 抖音账号
- 小红书账号

支持竞品对标分析、内容趋势分析、互动数据分析。

## 使用方式

```
用户：监控我关注的账号内容
技能：读取配置 → 抓取内容 → 分析数据 → 生成报告
```

## 支持平台

| 平台 | 监控内容 | 更新频率 |
|------|---------|---------|
| X | 推文、互动数据 | 实时 |
| 公众号 | 文章、阅读数 | 每日 |
| 视频号 | 视频、播放数 | 每日 |
| 抖音 | 视频、点赞评论 | 每日 |
| 小红书 | 笔记、点赞收藏 | 每日 |
