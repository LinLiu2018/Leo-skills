---
name: competitor-scraper-skill
description: Competitor Scraper Skill 技能。当用户需要相关帮助时使用。 [优化第5轮：提升了触发准确率]
license: MIT
---

# Competitor Scraper Skill (竞品数据抓取技能)

## 技能描述

自动抓取电商平台（京东、淘宝、亚马逊等）的竞品数据，包括销量、评价、价格等信息，并进行智能分析。

## 核心能力

- **数据抓取**: 从主流电商平台抓取竞品商品信息
- **销量分析**: 估算竞品销量，分析销售趋势
- **评价解析**: 提取用户评论中的痛点和需求
- **价格监控**: 跟踪竞品价格变动
- **进化学习**: 根据抓取失败经验自动优化策略

## 使用方法

```python
from competitor_scraper_skill import CompetitorScraperSkill

skill = CompetitorScraperSkill(
    skill_name="competitor_scraper",
    config_path="competitor_scraper_skill/config/config.yaml"
)

# 抓取竞品数据
result = skill.execute(
    platform="jd",  # jd, taobao, amazon
    keywords=["AI眼镜", "智能眼镜"],
    max_pages=5
)
```

## 进化机制

本技能支持自我进化能力：
- 抓取失败时自动记录经验（需要加延时、更换User-Agent等）
- 根据反爬策略自动调整抓取参数
- 持续优化分析准确度

## 配置文件

参考 `config/config.yaml` 和 `config/evolution_config.yaml`
