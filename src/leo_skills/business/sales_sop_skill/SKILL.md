---
name: sales-sop
description: 销售 SOP 执行技能，标准化销售流程。当用户需要执行销售流程、跟进销售线索、管理销售管道或生成销售报告时使用。 [优化第5轮：提升了触发准确率]
compatibility: '>=1.0.0'
license: MIT
metadata:
  version: 1.0.0
  category: business
  author: Leo AI System
  industry: real_estate
  crm_integration: pocket_assistant
---

# Sales SOP Skill - 销售SOP数字化技能

## 概述

将房地产销售SOP文档数字化，通过AI辅助判断每个环节的执行边界，
为业务人员提供实时指导，解决"SOP有但执行不一"的问题。

## 核心理念

> 见面 = 人做 | 线上环节 = AI 辅助指导

## 销售全流程 SOP

```
获客 → 首次接触 → 需求分析 → 房源匹配 → 带看安排 → 现场接待
  ↓                                                    ↓
线上跟进 ← 异议处理 ← 方案对比 ← 价格谈判 ← 意向确认 ← 带看反馈
  ↓
成交签约 → 售后服务 → 转介绍
```

## AI 介入环节

| 环节 | AI 职责 | 人的职责 |
|------|---------|---------|
| 获客 | 内容生成+多平台发布+线索收集 | IP打造+拍摄素材 |
| 首次接触 | 生成破冰话术+客户背景分析 | 电话/微信沟通 |
| 需求分析 | 标准化问卷+AI分析报告 | 引导客户填写 |
| 房源匹配 | 基于标签自动推荐TOP3房源 | 确认推荐结果 |
| 带看安排 | 生成带看路线+话术要点 | 现场接待 |
| 跟进提醒 | 自动提醒+跟进话术建议 | 执行跟进 |
| 异议处理 | 常见异议应对话术库 | 灵活应对 |
| 成交签约 | 合同模板+风险检查 | 签约确认 |
| 售后服务 | 满意度回访+转介绍引导 | 关系维护 |

## 与口袋助理CRM集成

- 读取客户标签 → 生成个性化跟进策略
- 读取录音分析 → 优化话术库
- 导出数据 → 生成销售漏斗报告

## 使用方式

```python
from sales_sop_skill import SalesSOP

sop = SalesSOP()

# 获取客户跟进建议
advice = sop.get_followup_advice(
    customer_tags=["价格敏感", "养老需求", "余姚意向"],
    last_contact_days=3,
    stage="需求分析"
)

# 生成带看准备清单
checklist = sop.generate_viewing_checklist(
    customer_needs={"type": "别墅", "budget": "200-300万", "purpose": "养老"},
    properties=["牟山玫瑰园", "九龙湖玖珑湾"]
)

# 获取异议处理话术
response = sop.handle_objection(
    objection="价格太贵了",
    customer_type="养老需求",
    property="牟山玫瑰园"
)
```