# Chart Generator Skill - 图表生成技能

**版本**: V1.0
**作者**: Claude Code

---

## 功能

使用 Python + Matplotlib 生成商业图表：
- 饼图 (Pie Chart)
- 柱状图 (Bar Chart)
- 折线图 (Line Chart)
- 热力图 (Heatmap)
- 组合图

---

## 快速使用

```python
from chart_generator import ChartGenerator

# 创建图表生成器
generator = ChartGenerator(output_dir="./charts")

# 生成饼图
generator.create_pie_chart(
    data={"写字楼": 40, "商铺": 35, "产业园区": 25},
    title="宁波商业地产市场规模分布",
    filename="market_size_pie.png"
)

# 生成柱状图
generator.create_bar_chart(
    categories=["天一", "东部新城", "南部商务区", "鄞州万达"],
    values=[5.5, 3.5, 2.0, 4.5],
    title="各商圈租金水平（元/㎡/天）",
    filename="rent_bar.png",
    ylabel="租金"
)

# 生成折线图
generator.create_line_chart(
    years=[2020, 2021, 2022, 2023, 2024, 2025],
    series={
        "写字楼": [2.0, 2.1, 2.0, 2.3, 2.4, 2.5],
        "商铺": [4.0, 4.5, 4.2, 3.8, 3.6, 3.7],
        "产业园区": [1.0, 1.1, 1.2, 1.3, 1.5, 1.6]
    },
    title="宁波商业地产租金走势",
    filename="rent_trend_line.png"
)

# 生成水平柱状图
generator.create_horizontal_bar(
    categories=["链家/贝壳", "本地头部", "开发商", "线上平台", "散兵中介"],
    values=[30, 25, 15, 20, 10],
    title="市场竞争格局（市场份额%）",
    filename="competition_hbar.png"
)

# 生成组合图
generator.create_combo_chart(
    categories=["Q1", "Q2", "Q3", "Q4"],
    revenue=[30, 45, 60, 80],
    cost=[40, 50, 55, 60],
    profit=[-10, -5, 5, 20],
    title="季度营收与利润",
    filename="revenue_combo.png"
)
```

---

## 图表类型

| 图表类型 | 函数名 | 用途 |
|---------|--------|------|
| 饼图 | `create_pie_chart()` | 市场份额、构成比例 |
| 柱状图 | `create_bar_chart()` | 对比分析、排名 |
| 折线图 | `create_line_chart()` | 趋势变化、时间序列 |
| 水平柱状图 | `create_horizontal_bar()` | 排名、份额对比 |
| 组合图 | `create_combo_chart()` | 多指标对比 |
| 热力图 | `create_heatmap()` | 相关性分析 |
| 雷达图 | `create_radar_chart()` | 多维度对比 |

---

## 输出

图表保存为 PNG 文件，可直接嵌入 Markdown 或文档。
