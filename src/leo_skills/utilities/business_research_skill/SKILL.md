---
name: business-research-skill
description: Business Research Skill 技能。当用户需要相关帮助时使用。 [优化第5轮：提升了触发准确率]
license: MIT
---

# Business Research Skill

**商业项目调研技能** - 专为商业项目可行性研究和落地计划设计

## 快速激活

```
调研宁波农贸市场
计算投资回报率
生成商业计划书
```

## 功能

1. **市场调研** - 调研指定区域的市场环境（竞品、人口、消费能力）
2. **舆情分析** - 分析公众对特定话题的态度
3. **投资测算** - 计算ROI、回收期、投入产出比
4. **商业计划生成** - 自动生成完整的商业计划书
5. **深度调研** - 结合Deep Research进行深度分析

## Deep Market Research

```
深度调研 "宁波" "农贸市场"
```

自动调研以下维度：
- 市场规模和发展趋势
- 成功案例分析
- 投资回报数据
- 政策支持情况

## 使用场景

- 商业项目可行性分析 ⭐
- 菜市场/农贸市场改造
- 投资回报测算
- 商业计划书撰写

## 示例：宁波菜市场项目调研

```python
# 1. 市场调研
research = skill.research_market(
    location="宁波",
    project_type="农贸市场",
    radius_km=1.5
)

# 2. 舆情分析
sentiment = skill.analyze_sentiment(
    topic="智慧农贸",
    location="宁波"
)

# 3. ROI计算
roi = skill.calculate_roi(
    investment={"物业": 800, "改造": 200, "营销": 30},
    revenue={"销售": 2000, "租金": 150},
    timeline_months=12
)

# 4. 生成商业计划
plan = skill.generate_business_plan(
    project_name="宁波XX农贸市场",
    project_type="农贸市场",
    location="宁波",
    investment_data={"investment": {"物业": 800}, "revenue": {"销售": 1500}, "timeline": 12}
)

# 5. 深度调研（推荐）
report = skill.deep_market_research("宁波", "农贸市场")
```

## 配置

```yaml
# config.yaml
max_results: 10
timeout: 30
language: zh-CN
```

---

**版本**: 1.0.0
**作者**: Claude Code
