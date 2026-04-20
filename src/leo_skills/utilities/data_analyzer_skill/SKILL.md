---
name: data-analyzer-skill
description: Data Analyzer Skill 技能。当用户需要相关帮助时使用。 [优化第5轮：提升了触发准确率]
license: MIT
---

# Data Analyzer Skill

数据分析技能。

## Analyze

```python
from leo_skills.utilities.data_analyzer_skill import DataAnalyzer

analyzer = DataAnalyzer()
results = analyzer.execute("analyze", data=data, analysis_type="trend")
```

## Visualize

```python
chart = analyzer.execute("visualize", data=data, chart_type="bar")
```

## Compare

```python
comparison = analyzer.execute("compare", data_groups=[data1, data2, data3])
```

---
**Version:** 1.0.0
