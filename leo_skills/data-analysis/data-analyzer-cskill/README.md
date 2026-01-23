# Data Analyzer Skill

**数据分析技能** - 提供数据分析和可视化能力

---

## 🎯 技能概述

这个技能为Leo AI Agent System提供数据分析能力，支持：
- 描述性统计分析
- 趋势分析
- 对比分析
- 数据可视化
- 分析报告生成

## 📋 功能列表

### 1. 描述性统计
- 均值、中位数、众数
- 最小值、最大值、范围
- 标准差、方差
- 数据分布

### 2. 趋势分析
- 趋势识别（上升/下降/稳定）
- 变化率计算
- 周期性分析

### 3. 对比分析
- 多组数据对比
- 差异分析
- 相关性分析

### 4. 数据可视化
- 柱状图
- 折线图
- 饼图
- 散点图

## 🔧 使用方式

### 描述性分析
```python
from data_analyzer_skill import DataAnalyzerSkill

skill = DataAnalyzerSkill()
result = skill.analyze([10, 20, 30, 40, 50], "descriptive")
print(f"平均值: {result['mean']}")
```

### 趋势分析
```python
result = skill.analyze([10, 15, 20, 25, 30], "trend")
print(f"趋势: {result['trend']}")
```

### 对比分析
```python
groups = {
    "产品A": [100, 120, 110, 130],
    "产品B": [90, 95, 100, 105]
}
result = skill.compare(groups)
```

### 生成报告
```python
report = skill.generate_report(data, title="月度销售分析")
```

## 📊 应用场景

### 1. 房地产市场分析
```python
# 分析房价趋势
prices = [25000, 26000, 27500, 28000, 29000]
result = skill.analyze(prices, "trend")
# 输出: 趋势: 上升, 变化率: 16%
```

### 2. 项目投资回报分析
```python
# 对比不同项目的回报
projects = {
    "智慧农贸": [15, 18, 22, 25],
    "商业地产": [10, 12, 14, 16]
}
result = skill.compare(projects)
```

### 3. 销售数据分析
```python
# 生成销售分析报告
sales_data = [100, 120, 110, 130, 150]
report = skill.generate_report(sales_data, title="季度销售分析")
```

## 📝 API说明

### analyze(data, analysis_type="descriptive", **kwargs)
执行数据分析

**参数**:
- `data` (List|Dict): 待分析数据
- `analysis_type` (str): 分析类型
  - `descriptive`: 描述性统计
  - `trend`: 趋势分析
  - `comparative`: 对比分析

**返回**:
```python
{
    "analysis_type": "descriptive",
    "count": 5,
    "mean": 30.0,
    "median": 30,
    "min": 10,
    "max": 50,
    "range": 40,
    "success": True
}
```

### visualize(data, chart_type="bar", **kwargs)
生成数据可视化

**参数**:
- `data` (List|Dict): 待可视化数据
- `chart_type` (str): 图表类型（bar, line, pie）
- `title` (str): 图表标题
- `xlabel` (str): X轴标签
- `ylabel` (str): Y轴标签

**返回**:
```python
{
    "chart_type": "bar",
    "data": [...],
    "config": {...},
    "success": True
}
```

### compare(data_groups, **kwargs)
对比多组数据

**参数**:
- `data_groups` (Dict): 数据组字典 {"组名": [数据]}

**返回**:
```python
{
    "comparison": {
        "组A": {"count": 4, "mean": 25.0, ...},
        "组B": {"count": 4, "mean": 20.0, ...}
    },
    "groups": ["组A", "组B"],
    "success": True
}
```

### generate_report(data, **kwargs)
生成分析报告

**参数**:
- `data` (List|Dict): 数据
- `title` (str): 报告标题

**返回**:
```python
{
    "title": "数据分析报告",
    "descriptive_stats": {...},
    "trend_analysis": {...},
    "summary": "平均值: 30.00、数据量: 5、趋势: 上升",
    "success": True
}
```

## 🎓 使用示例

### 示例1：房地产市场分析
```python
# 分析宁波房价数据
prices = [25000, 26500, 27000, 28500, 30000]

# 描述性统计
stats = skill.analyze(prices, "descriptive")
print(f"平均房价: {stats['mean']}")
print(f"价格范围: {stats['min']} - {stats['max']}")

# 趋势分析
trend = skill.analyze(prices, "trend")
print(f"价格趋势: {trend['trend']}")
print(f"涨幅: {trend['change_rate']:.2f}%")
```

### 示例2：项目对比分析
```python
# 对比不同项目的投资回报
projects = {
    "淮安建华官园": [15, 18, 22, 25, 28],
    "竞品项目A": [12, 14, 16, 18, 20],
    "竞品项目B": [10, 12, 15, 17, 19]
}

# 对比分析
comparison = skill.compare(projects)
for name, stats in comparison['comparison'].items():
    print(f"{name}: 平均回报 {stats['mean']:.2f}%")
```

### 示例3：生成分析报告
```python
# 生成月度销售分析报告
sales = [100, 120, 110, 130, 150, 140]

report = skill.generate_report(
    sales,
    title="2026年1月销售分析报告"
)

print(report['summary'])
# 输出: 平均值: 125.00、数据量: 6、趋势: 上升
```

## 🔒 注意事项

1. **数据格式**: 支持数值列表和字典格式
2. **数据质量**: 确保数据准确性和完整性
3. **分析方法**: 当前提供基础统计分析，可扩展高级分析
4. **可视化**: 当前返回配置，实际图表生成需要matplotlib

## 🚀 未来计划

- [ ] 集成pandas进行高级数据处理
- [ ] 使用matplotlib生成实际图表
- [ ] 添加更多统计分析方法
- [ ] 支持Excel/CSV文件读取
- [ ] 添加机器学习预测功能

---

**创建时间**: 2026-01-09
**维护者**: Leo Liu
**版本**: 1.0.0
