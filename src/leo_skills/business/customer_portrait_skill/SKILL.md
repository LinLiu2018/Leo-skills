---
name: customer-portrait
description: 客户画像AI分析技能，基于多维数据构建精准客户画像
compatibility: ">=1.0.0"
license: MIT
metadata:
  version: "1.0.0"
  category: business
  author: Leo AI System
  industry: real_estate
---

# Customer Portrait Skill - 客户画像技能

## 概述

基于客户行为数据、沟通记录、浏览偏好等多维信息，
AI自动构建客户画像，辅助销售精准跟进。

## 画像维度

1. **基础属性** - 年龄/职业/家庭结构/收入水平
2. **购房动机** - 自住/投资/养老/改善/学区
3. **决策特征** - 决策周期/决策人/关注点排序
4. **行为特征** - 活跃时段/偏好沟通方式/响应速度
5. **风险评估** - 流失风险/成交概率/预算匹配度

## 使用方式

```python
from customer_portrait_skill import CustomerPortrait

portrait = CustomerPortrait()

# 生成客户画像
profile = portrait.analyze(
    name="张女士",
    interactions=[...],
    tags=["养老需求", "余姚意向"],
)

# 获取跟进建议
advice = portrait.get_strategy(profile)
```
