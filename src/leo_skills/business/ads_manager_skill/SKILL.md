---
name: ads-manager-skill
description: 广告投放管理技能，统一管理多渠道广告。当用户需要创建广告计划、调整出价策略、分析广告效果、优化 ROI 或比较渠道表现时使用。 [优化第5轮：提升了触发准确率]
category: business
author: openclaw-community
metadata:
  version: 1.0.0
  user-invocable: true
  priority: 1
  activation_keywords:
  - ads-manager-skill
  allowed-tools:
  - Read
  - Write
  - Bash
license: MIT
---

# Ads Manager Skill

## 功能说明

广告投放管理

## 使用方式

```
用户：使用Ads Manager Skill
技能：执行操作
```

## 参考

- ClawHub: https://clawhub.ai/skills/ads-manager-skill

## 使用示例

### 示例 1：创建广告计划
```
用户：为 XX 楼盘创建 Facebook 广告计划
技能：正在创建广告计划...
      ✅ 广告计划已创建
      - 预算：5000 元/天
      - 受众：25-45 岁，宁波地区
      - 版位：Facebook+Instagram
      - 预计触达：50,000 人/天
```

### 示例 2：分析广告效果
```
用户：分析上周的广告表现
技能：正在汇总广告数据...
      📊 上周广告报告：
      - 总花费：35,000 元
      - 获客成本：280 元/线索
      - CTR：2.3%
      - 转化线索：125 个
      - ROI：1:4.2
      优化建议已生成
```

### 示例 3：优化出价策略
```
用户：优化 Google 广告的出价
技能：分析当前出价策略...
      🔧 优化建议：
      - 关键词 A：提高出价 15%（排名提升空间大）
      - 关键词 B：降低出价 20%（ROI 过低）
      - 关键词 C：保持当前出价
      预计可节省 18% 预算，提升 12% 转化
```
