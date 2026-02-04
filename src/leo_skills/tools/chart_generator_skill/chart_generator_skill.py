# -*- coding: utf-8 -*-
"""
chart_generator_skill - 图表生成技能

使用 Matplotlib 生成商业图表：饼图、柱状图、折线图、热力图等。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


class ChartType(Enum):
    """图表类型"""
    PIE = "pie"
    BAR = "bar"
    LINE = "line"
    HORIZONTAL_BAR = "hbar"
    COMBO = "combo"
    HEATMAP = "heatmap"
    RADAR = "radar"


@dataclass
class ChartConfig:
    """图表配置"""
    title: str
    chart_type: ChartType
    width: int = 10
    height: int = 6
    dpi: int = 100
    output_path: str = ""


@dataclass
class ChartData:
    """图表数据"""
    labels: List[str] = field(default_factory=list)
    values: List[float] = field(default_factory=list)
    series: Dict[str, List[float]] = field(default_factory=dict)
    categories: List[str] = field(default_factory=list)


@dataclass
class ChartResult:
    """图表生成结果"""
    status: str
    output_path: str = ""
    chart_type: str = ""
    message: str = ""


class ChartGeneratorSkill:
    """
    图表生成技能

    使用 Python + Matplotlib 生成商业图表。
    支持饼图、柱状图、折线图、热力图、组合图等多种类型。
    """

    def __init__(self):
        self.name = "chart_generator_skill"
        self.version = "1.0.0"
        self.description = "使用 Matplotlib 生成商业图表"
        self.category = "tools"
        self.output_dir = "./charts"

    def execute(
        self,
        chart_type: str,
        title: str,
        data: Dict[str, Any],
        output_filename: str = "",
        output_dir: str = "./charts",
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行图表生成

        Args:
            chart_type: 图表类型 (pie/bar/line/hbar/combo/heatmap/radar)
            title: 图表标题
            data: 图表数据
            output_filename: 输出文件名
            output_dir: 输出目录

        Returns:
            图表生成结果
        """
        try:
            self.output_dir = output_dir
            ctype = ChartType(chart_type.lower())

            # 生成文件名
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"{ctype.value}_{timestamp}.png"

            output_path = Path(output_dir) / output_filename

            # 生成图表代码
            chart_code = self._generate_chart_code(ctype, title, data, str(output_path))

            result = ChartResult(
                status="generated",
                output_path=str(output_path),
                chart_type=ctype.value,
                message=f"图表代码已生成: {output_path}"
            )

            return {
                "status": "success",
                "result": result,
                "chart_code": chart_code,
                "instructions": [
                    "1. 确保已安装 matplotlib: pip install matplotlib",
                    "2. 运行生成的代码",
                    "3. 图表将保存到指定路径"
                ]
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "skill": self.name
            }

    def _generate_chart_code(
        self,
        chart_type: ChartType,
        title: str,
        data: Dict[str, Any],
        output_path: str
    ) -> str:
        """生成图表代码"""
        lines = [
            "import matplotlib.pyplot as plt",
            "import matplotlib",
            "matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']",
            "matplotlib.rcParams['axes.unicode_minus'] = False",
            "",
            f"# 创建图表: {title}",
            f"fig, ax = plt.subplots(figsize=(10, 6))",
            "",
        ]

        if chart_type == ChartType.PIE:
            lines.extend(self._generate_pie_code(data, title))
        elif chart_type == ChartType.BAR:
            lines.extend(self._generate_bar_code(data, title))
        elif chart_type == ChartType.LINE:
            lines.extend(self._generate_line_code(data, title))
        elif chart_type == ChartType.HORIZONTAL_BAR:
            lines.extend(self._generate_hbar_code(data, title))

        lines.extend([
            f"plt.title('{title}')",
            f"plt.tight_layout()",
            f"plt.savefig('{output_path}', dpi=150, bbox_inches='tight')",
            f"plt.close()",
            f"print('图表已保存: {output_path}')",
        ])

        return "\n".join(lines)

    def _generate_pie_code(self, data: Dict[str, Any], title: str) -> List[str]:
        """生成饼图代码"""
        labels = data.get("labels", [])
        values = data.get("values", [])
        return [
            f"labels = {labels}",
            f"sizes = {values}",
            f"ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)",
            f"ax.axis('equal')",
        ]

    def _generate_bar_code(self, data: Dict[str, Any], title: str) -> List[str]:
        """生成柱状图代码"""
        categories = data.get("categories", [])
        values = data.get("values", [])
        ylabel = data.get("ylabel", "")
        return [
            f"categories = {categories}",
            f"values = {values}",
            f"ax.bar(categories, values)",
            f"plt.xlabel('类别')",
            f"plt.ylabel('{ylabel}')" if ylabel else "plt.ylabel('数值')",
        ]

    def _generate_line_code(self, data: Dict[str, Any], title: str) -> List[str]:
        """生成折线图代码"""
        years = data.get("years", [])
        series = data.get("series", {})
        lines = [
            f"years = {years}",
        ]
        for name, values in series.items():
            lines.append(f"ax.plot(years, {values}, label='{name}', marker='o')")
        lines.append("plt.legend()")
        lines.append("plt.xlabel('年份')")
        lines.append("plt.ylabel('数值')")
        return lines

    def _generate_hbar_code(self, data: Dict[str, Any], title: str) -> List[str]:
        """生成水平柱状图代码"""
        categories = data.get("categories", [])
        values = data.get("values", [])
        return [
            f"categories = {categories}",
            f"values = {values}",
            f"ax.barh(categories, values)",
            f"plt.xlabel('数值')",
        ]

    def create_pie_chart(
        self,
        data: Dict[str, float],
        title: str,
        filename: str = ""
    ) -> Dict[str, Any]:
        """创建饼图（便捷方法）"""
        return self.execute(
            chart_type="pie",
            title=title,
            data={"labels": list(data.keys()), "values": list(data.values())},
            output_filename=filename or "pie_chart.png"
        )

    def create_bar_chart(
        self,
        categories: List[str],
        values: List[float],
        title: str,
        ylabel: str = "",
        filename: str = ""
    ) -> Dict[str, Any]:
        """创建柱状图（便捷方法）"""
        return self.execute(
            chart_type="bar",
            title=title,
            data={"categories": categories, "values": values, "ylabel": ylabel},
            output_filename=filename or "bar_chart.png"
        )

    def create_line_chart(
        self,
        years: List[int],
        series: Dict[str, List[float]],
        title: str,
        filename: str = ""
    ) -> Dict[str, Any]:
        """创建折线图（便捷方法）"""
        return self.execute(
            chart_type="line",
            title=title,
            data={"years": years, "series": series},
            output_filename=filename or "line_chart.png"
        )


def main():
    """入口函数"""
    return ChartGeneratorSkill()


if __name__ == "__main__":
    skill = main()
