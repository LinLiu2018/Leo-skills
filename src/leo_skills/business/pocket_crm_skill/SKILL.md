---
name: pocket-crm
description: 口袋助理CRM集成技能，对接口袋助理数据实现AI增强的客户管理
compatibility: ">=1.0.0"
license: MIT
metadata:
  version: "1.0.0"
  category: business
  author: Leo AI System
  industry: real_estate
  crm_platform: pocket_assistant
---

# Pocket CRM Skill - 口袋助理CRM集成技能

## 概述

对接口袋助理CRM系统，读取客户数据、通话录音、跟进记录，
通过AI分析生成客户洞察和跟进策略。

## 核心功能

1. **客户数据同步** - 从口袋助理读取客户列表和标签
2. **通话分析** - 分析录音内容，提取关键信息
3. **跟进策略** - 基于客户行为数据生成个性化跟进方案
4. **销售漏斗** - 自动统计各阶段客户数量和转化率
5. **日报周报** - 自动生成销售工作报告

## 数据流

```
口袋助理 → API/导出 → 数据清洗 → AI分析 → 策略输出
                                      ↓
                              跟进提醒 + 话术建议
```

## 使用方式

```python
from pocket_crm_skill import PocketCRM

crm = PocketCRM(api_key="your_key")

# 获取客户列表
customers = crm.get_customers(stage="需求分析")

# 分析客户跟进状态
report = crm.analyze_followup_status()

# 生成日报
daily = crm.generate_daily_report()
```
