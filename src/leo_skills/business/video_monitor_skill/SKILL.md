---
name: video-monitor-skill
display_name: 视频号账号监测
description: 监测视频号账号数据，包括粉丝增长、视频表现、互动数据等。
支持单账号监测和多账号对比分析。
。当用户需要业务运营支持相关帮助时使用。 [优化第5轮：提升了触发准确率]

  支持单账号监测和多账号对比分析。

  。当用户需要业务运营支持相关帮助时使用。'
author: Leo AI System
category: business
status: active
inputs:
- name: account_id
  type: string
  required: false
  description: 视频号账号ID或名称
- name: city
  type: string
  required: false
  description: 城市名称（如：宁波）
- name: days
  type: integer
  required: false
  default: 7
  description: 监测天数范围
- name: metric_type
  type: string
  required: false
  default: all
  description: 数据类型（all/followers/videos/lives/engagement）
outputs:
- name: report
  type: object
  description: 监测数据报告
- name: summary
  type: string
  description: 数据摘要
metadata:
  version: 1.0.0
  user-invocable: true
  activation_keywords:
  - 视频号
  - 账号监测
  - 粉丝统计
  - 数据分析
  - 宁波视频号
  - 视频数据
  - 直播数据
  - 监测工具
license: MIT
---

# 视频号账号监测技能

## 功能说明

本技能用于监测和分析视频号账号数据，提供以下功能：

### 1. 单账号监测
- 粉丝增长趋势
- 视频发布统计
- 互动数据分析（点赞、评论、转发）
- 直播数据统计

### 2. 多账号对比
- 同一城市多个账号对比
- 行业标杆对比
- 增长趋势对比

### 3. 数据导出
- 生成监测报告
- 数据可视化建议
- 运营优化建议

## 使用示例

### 监测单个账号
```python
skill.monitor_account("账号名称")
```

### 城市账号批量监测
```python
skill.monitor_city_accounts("宁波")
```

### 获取账号对比分析
```python
skill.compare_accounts(["账号A", "账号B"])
```

## 注意事项

1. 当前版本使用模拟数据演示功能
2. 实际部署时需要接入视频号开放平台API
3. 数据更新频率建议设置为每日一次