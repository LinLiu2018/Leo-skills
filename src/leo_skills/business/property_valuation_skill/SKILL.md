---
name: property-valuation-skill
description: 房产估值技能，评估房产市场价值。当用户需要提供房产估值、分析市场成交价、生成估值报告或比较类似房源时使用。 [优化第5轮：提升了触发准确率]
category: business
author: openclaw-community
metadata:
  version: 1.0.0
  user-invocable: true
  priority: 1
  activation_keywords:
  - property-valuation-skill
  allowed-tools:
  - Read
  - Write
  - Bash
license: MIT
---

# Property Valuation Skill

## 功能说明

房产估值

## 使用方式

```
用户：使用Property Valuation Skill
技能：执行操作
```

## 参考

- ClawHub: https://clawhub.ai/skills/property-valuation-skill

## 使用示例

### 示例 1：单套房产估值
```
用户：评估宁波市鄞州区 XX 小区 120 平别墅的价值
技能：正在分析市场数据...
      📍 估值报告：
      - 市场参考价：850-920 万元
      - 单价：7.1-7.7 万元/平
      - 置信度：85%
      - 可比成交：3 套（近 3 个月）
      详细报告已生成
```

### 示例 2：批量估值
```
用户：评估我列表中的 10 套房产
技能：正在批量处理...
      ✅ 完成 10 套房产估值
      - 总价值：8,500 万元
      - 平均单价：6.8 万元/平
      - 最高：1,200 万元（XX 别墅）
      - 最低：450 万元（XX 公寓）
      Excel 报告已导出
```
