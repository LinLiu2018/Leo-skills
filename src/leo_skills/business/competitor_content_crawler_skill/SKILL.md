---
name: competitor-content-crawler
description: 竞品内容采集分析技能，采集抖音/小红书等平台同行爆款内容
compatibility: ">=1.0.0"
license: MIT
metadata:
  version: "1.0.0"
  category: business
  author: Leo AI System
  platforms: [douyin, xiaohongshu, kuaishou, bilibili]
  upstream: https://github.com/NanmiCoder/MediaCrawler
---

# Competitor Content Crawler Skill - 竞品内容采集技能

## 概述

基于 [MediaCrawler](https://github.com/NanmiCoder/MediaCrawler) 的竞品内容采集分析技能。
自动采集同行在抖音、小红书等平台的爆款内容，分析内容策略，反哺自身内容创作。

## 核心功能

1. **竞品账号监控**: 监控指定竞品账号的内容更新
2. **关键词搜索采集**: 按关键词搜索采集相关内容
3. **爆款内容分析**: 分析点赞/评论/分享数据，识别爆款规律
4. **内容策略报告**: 生成竞品内容策略分析报告
5. **选题灵感库**: 基于爆款内容生成选题建议

## 采集维度

| 维度 | 说明 |
|------|------|
| 标题 | 爆款标题结构分析 |
| 封面 | 封面图风格分析 |
| 标签 | 高频标签统计 |
| 互动数据 | 点赞/评论/收藏/分享 |
| 发布时间 | 最佳发布时间分析 |
| 内容类型 | 图文/视频/直播切片 |

## 房地产专用关键词

```yaml
搜索关键词:
  - 宁波买房
  - 宁波别墅
  - 度假养老房
  - 法拍房
  - 宁波新房
  - 近郊别墅
  - 养老地产
```

## 使用方式

```python
from competitor_content_crawler_skill import CompetitorCrawler

crawler = CompetitorCrawler()

# 按关键词采集小红书爆款
results = crawler.search_hot_content(
    platform="xiaohongshu",
    keywords=["宁波别墅", "度假养老"],
    min_likes=100,
    limit=50
)

# 监控竞品账号
crawler.monitor_accounts(
    platform="douyin",
    accounts=["竞品账号1", "竞品账号2"],
    days=7
)

# 生成分析报告
report = crawler.generate_analysis_report(results)
```

## 依赖

- MediaCrawler (参考: https://github.com/NanmiCoder/MediaCrawler)
- playwright >= 1.40.0
