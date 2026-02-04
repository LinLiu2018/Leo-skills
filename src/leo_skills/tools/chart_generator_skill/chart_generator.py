#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart Generator - 图表生成器
为商业计划书生成专业图表
"""

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

class ChartGenerator:
    """图表生成器"""

    def __init__(self, output_dir="./charts"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def create_pie_chart(self, data, title, filename, colors=None):
        """生成饼图"""
        if colors is None:
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']

        labels = list(data.keys())
        sizes = list(data.values())

        fig, ax = plt.subplots(figsize=(10, 8))
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, autopct='%1.1f%%',
            colors=colors[:len(data)],
            explode=[0.02] * len(data),
            shadow=True,
            startangle=90
        )

        # 设置文字样式
        for text in texts:
            text.set_fontsize(12)
        for autotext in autotexts:
            autotext.set_fontsize(11)
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)

        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✅ 饼图已生成: {filepath}")
        return filepath

    def create_bar_chart(self, categories, values, title, filename, ylabel="数值"):
        """生成柱状图"""
        fig, ax = plt.subplots(figsize=(12, 7))

        x = np.arange(len(categories))
        bars = ax.bar(x, values, color='#3498DB', width=0.6, edgecolor='#2980B9', linewidth=1.5)

        # 添加数值标签
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.annotate(f'{val}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 5),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=11, fontweight='bold')

        ax.set_xlabel('类别', fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(categories, fontsize=11)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=0.3)

        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✅ 柱状图已生成: {filepath}")
        return filepath

    def create_line_chart(self, years, series, title, filename):
        """生成折线图"""
        fig, ax = plt.subplots(figsize=(12, 7))

        colors = ['#E74C3C', '#3498DB', '#2ECC71', '#9B59B6', '#F39C12']
        markers = ['o', 's', '^', 'D', 'v']

        for idx, (name, values) in enumerate(series.items()):
            ax.plot(years, values,
                    color=colors[idx % len(colors)],
                    marker=markers[idx % len(markers)],
                    markersize=8,
                    linewidth=2.5,
                    label=name)

        ax.set_xlabel('年份', fontsize=12)
        ax.set_ylabel('租金（元/㎡/天）', fontsize=12)
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.legend(loc='best', fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_xticks(years)

        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✅ 折线图已生成: {filepath}")
        return filepath

    def create_horizontal_bar(self, categories, values, title, filename):
        """生成水平柱状图"""
        fig, ax = plt.subplots(figsize=(12, 7))

        y = np.arange(len(categories))
        colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(categories)))[::-1]

        bars = ax.barh(y, values, color=colors, height=0.6, edgecolor='#2C3E50', linewidth=1)

        # 添加数值标签
        for bar, val in zip(bars, values):
            width = bar.get_width()
            ax.annotate(f'{val}%',
                        xy=(width, bar.get_y() + bar.get_height() / 2),
                        xytext=(5, 0),
                        textcoords="offset points",
                        ha='left', va='center',
                        fontsize=11, fontweight='bold')

        ax.set_xlabel('市场份额 (%)', fontsize=12)
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_yticks(y)
        ax.set_yticklabels(categories, fontsize=11)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='x', alpha=0.3)
        ax.invert_yaxis()

        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✅ 水平柱状图已生成: {filepath}")
        return filepath

    def create_combo_chart(self, categories, revenue, cost, profit, title, filename):
        """生成组合图（柱状+折线）"""
        fig, ax1 = plt.subplots(figsize=(14, 8))

        x = np.arange(len(categories))
        width = 0.35

        # 柱状图
        bars1 = ax1.bar(x - width/2, revenue, width, label='营收', color='#3498DB', alpha=0.8)
        bars2 = ax1.bar(x + width/2, cost, width, label='成本', color='#E74C3C', alpha=0.8)

        ax1.set_xlabel('季度', fontsize=12)
        ax1.set_ylabel('金额（万元）', fontsize=12, color='#2C3E50')
        ax1.tick_params(axis='y', labelcolor='#2C3E50')

        # 折线图（次坐标轴）
        ax2 = ax1.twinx()
        ax2.plot(x, profit, color='#2ECC71', marker='o', markersize=10, linewidth=3, label='利润')
        ax2.set_ylabel('利润（万元）', fontsize=12, color='#2ECC71')
        ax2.tick_params(axis='y', labelcolor='#2ECC71')
        ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)

        # 标签
        ax1.set_xticks(x)
        ax1.set_xticklabels(categories, fontsize=11)
        ax1.legend(loc='upper left', fontsize=10)
        ax2.legend(loc='upper right', fontsize=10)

        ax1.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax1.grid(axis='y', alpha=0.3)

        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✅ 组合图已生成: {filepath}")
        return filepath

    def create_heatmap(self, data, title, filename, xlabels=None, ylabels=None):
        """生成热力图"""
        fig, ax = plt.subplots(figsize=(10, 8))

        im = ax.imshow(data, cmap='YlOrRd', aspect='auto')

        # 设置标签
        if xlabels:
            ax.set_xticks(np.arange(len(xlabels)))
            ax.set_xticklabels(xlabels, fontsize=11)
        if ylabels:
            ax.set_yticks(np.arange(len(ylabels)))
            ax.set_yticklabels(ylabels, fontsize=11)

        # 添加数值
        for i in range(len(ylabels) if ylabels else data.shape[0]):
            for j in range(len(xlabels) if xlabels else data.shape[1]):
                text = ax.text(j, i, f'{data[i, j]:.1f}',
                              ha="center", va="center", color="black", fontsize=12)

        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        plt.colorbar(im, ax=ax, label='数值')

        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✅ 热力图已生成: {filepath}")
        return filepath


def generate_business_plan_charts():
    """生成商业计划书所有图表"""
    generator = ChartGenerator(output_dir="./charts")

    charts = {}

    # 1. 市场规模饼图
    charts['market_size'] = generator.create_pie_chart(
        data={"写字楼": 45, "商铺": 35, "产业园区": 20},
        title="宁波商业地产市场规模分布",
        filename="chart1_market_size_pie.png"
    )

    # 2. 各商圈租金柱状图
    charts['rental_comparison'] = generator.create_bar_chart(
        categories=["天一广场", "东部新城", "南部商务区", "鄞州万达", "江北来福士"],
        values=[5.5, 3.5, 2.0, 4.5, 3.2],
        title="宁波主要商圈租金水平（元/㎡/天）",
        filename="chart2_rental_bar.png",
        ylabel="租金（元/㎡/天）"
    )

    # 3. 租金趋势折线图
    charts['rental_trend'] = generator.create_line_chart(
        years=[2020, 2021, 2022, 2023, 2024, 2025],
        series={
            "写字楼": [2.0, 2.1, 2.0, 2.3, 2.4, 2.5],
            "商铺": [4.0, 4.5, 4.2, 3.8, 3.6, 3.7],
            "产业园区": [1.0, 1.1, 1.2, 1.3, 1.5, 1.6]
        },
        title="宁波商业地产租金走势（2020-2025）",
        filename="chart3_rental_trend.png"
    )

    # 4. 竞争格局水平柱状图
    charts['competition'] = generator.create_horizontal_bar(
        categories=["链家/贝壳", "本地头部中介", "开发商自营", "线上平台", "散兵中介"],
        values=[30, 25, 15, 20, 10],
        title="宁波商业地产经纪市场竞争格局",
        filename="chart4_competition_hbar.png"
    )

    # 5. 三年营收利润组合图
    charts['revenue_profit'] = generator.create_combo_chart(
        categories=["Year 1", "Year 2", "Year 3"],
        revenue=[150, 440, 730],
        cost=[280, 480, 620],
        profit=[-130, -40, 110],
        title="三年营收、成本与利润预测（万元）",
        filename="chart5_revenue_combo.png"
    )

    # 6. 客户类型饼图
    charts['client_types'] = generator.create_pie_chart(
        data={"中小企业": 50, "创业公司": 25, "连锁品牌": 15, "政府/国企": 10},
        title="目标客户类型分布",
        filename="chart6_client_types.png"
    )

    # 7. 服务对比雷达图（用柱状图替代）
    charts['service_comparison'] = generator.create_bar_chart(
        categories=["房源信息", "需求匹配", "带看服务", "合同服务", "增值服务", "后续跟进"],
        values=[90, 85, 95, 80, 70, 60],
        title="服务能力对比（传统中介 vs 我们）",
        filename="chart7_service_comparison.png",
        ylabel="得分"
    )

    # 8. 风险矩阵热力图
    charts['risk_matrix'] = generator.create_heatmap(
        data=np.array([[3, 8, 2], [5, 6, 4], [7, 4, 3], [2, 3, 1]]),
        title="风险评估矩阵",
        filename="chart8_risk_heatmap.png",
        xlabels=["市场风险", "运营风险", "财务风险"],
        ylabels=["市场低迷", "人才流失", "平台竞争", "政策风险"]
    )

    return charts


if __name__ == '__main__':
    print("=" * 50)
    print("生成商业计划书图表")
    print("=" * 50)

    charts = generate_business_plan_charts()

    print("\n" + "=" * 50)
    print("所有图表已生成！")
    print("=" * 50)
    for name, path in charts.items():
        print(f"  • {name}: {path}")
