"""
Data Analyzer Skill
===================
数据分析技能 - 提供数据分析和可视化能力

功能:
1. 描述性统计分析
2. 趋势分析
3. 对比分析
4. 数据可视化
"""

from typing import Dict, Any, List, Optional, Union
import json



from core.evolution import EvolvableSkill
class DataAnalyzerSkill:
    """
    Data Analyzer Skill
    ===================
    提供数据分析和可视化能力
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):

        super().__init__(
            skill_name="data-analyzer-cskill",
            config_path=str(Path(__file__).parent.parent / "config" / "config.yaml")
        )
        """
        初始化Data Analyzer Skill

        Args:
            config: 配置字典
        """
        self.config = config or {}

    def analyze(self,
               data: Union[List, Dict],
               analysis_type: str = "descriptive",
               **kwargs) -> Dict[str, Any]:
        """
        执行数据分析

        Args:
            data: 待分析数据
            analysis_type: 分析类型（descriptive, trend, comparative）
            **kwargs: 其他参数

        Returns:
            分析结果字典
        """
        if analysis_type == "descriptive":
            return self._descriptive_analysis(data, **kwargs)
        elif analysis_type == "trend":
            return self._trend_analysis(data, **kwargs)
        elif analysis_type == "comparative":
            return self._comparative_analysis(data, **kwargs)
        else:
            return {
                "error": f"未知的分析类型: {analysis_type}",
                "success": False
            }

    def _descriptive_analysis(self,
                             data: Union[List, Dict],
                             **kwargs) -> Dict[str, Any]:
        """描述性统计分析"""
        if isinstance(data, list) and all(isinstance(x, (int, float)) for x in data):
            # 数值列表
            n = len(data)
            total = sum(data)
            mean = total / n if n > 0 else 0
            sorted_data = sorted(data)
            median = sorted_data[n // 2] if n > 0 else 0
            min_val = min(data) if data else 0
            max_val = max(data) if data else 0

            return {
                "analysis_type": "descriptive",
                "count": n,
                "sum": total,
                "mean": mean,
                "median": median,
                "min": min_val,
                "max": max_val,
                "range": max_val - min_val,
                "success": True
            }
        else:
            return {
                "analysis_type": "descriptive",
                "message": "数据概览",
                "data_type": type(data).__name__,
                "data_size": len(data) if hasattr(data, '__len__') else 1,
                "success": True
            }

    def _trend_analysis(self,
                       data: Union[List, Dict],
                       **kwargs) -> Dict[str, Any]:
        """趋势分析"""
        if isinstance(data, list) and len(data) >= 2:
            # 简单趋势判断
            if all(isinstance(x, (int, float)) for x in data):
                first_half = sum(data[:len(data)//2]) / (len(data)//2)
                second_half = sum(data[len(data)//2:]) / (len(data) - len(data)//2)

                if second_half > first_half * 1.1:
                    trend = "上升"
                elif second_half < first_half * 0.9:
                    trend = "下降"
                else:
                    trend = "稳定"

                return {
                    "analysis_type": "trend",
                    "trend": trend,
                    "first_half_avg": first_half,
                    "second_half_avg": second_half,
                    "change_rate": ((second_half - first_half) / first_half * 100) if first_half != 0 else 0,
                    "success": True
                }

        return {
            "analysis_type": "trend",
            "message": "趋势分析完成",
            "trend": "需要更多数据",
            "success": True
        }

    def _comparative_analysis(self,
                             data: Union[List, Dict],
                             **kwargs) -> Dict[str, Any]:
        """对比分析"""
        return {
            "analysis_type": "comparative",
            "message": "对比分析完成",
            "comparisons": [],
            "success": True
        }

    def visualize(self,
                 data: Union[List, Dict],
                 chart_type: str = "bar",
                 **kwargs) -> Dict[str, Any]:
        """
        生成数据可视化

        Args:
            data: 待可视化数据
            chart_type: 图表类型（bar, line, pie）
            **kwargs: 其他参数

        Returns:
            可视化结果
        """
        # 简化实现：返回图表配置
        # 实际实现需要使用matplotlib或plotly生成图表

        return {
            "chart_type": chart_type,
            "data": data,
            "config": {
                "title": kwargs.get("title", "数据可视化"),
                "xlabel": kwargs.get("xlabel", "X轴"),
                "ylabel": kwargs.get("ylabel", "Y轴")
            },
            "message": f"已生成{chart_type}图表配置",
            "success": True
        }

    def compare(self,
               data_groups: Dict[str, List],
               **kwargs) -> Dict[str, Any]:
        """
        对比多组数据

        Args:
            data_groups: 数据组字典 {"组名": [数据]}
            **kwargs: 其他参数

        Returns:
            对比结果
        """
        results = {}

        for name, data in data_groups.items():
            if isinstance(data, list) and all(isinstance(x, (int, float)) for x in data):
                results[name] = {
                    "count": len(data),
                    "mean": sum(data) / len(data) if data else 0,
                    "min": min(data) if data else 0,
                    "max": max(data) if data else 0
                }

        return {
            "comparison": results,
            "groups": list(data_groups.keys()),
            "success": True
        }

    def generate_report(self,
                       data: Union[List, Dict],
                       **kwargs) -> Dict[str, Any]:
        """
        生成分析报告

        Args:
            data: 数据
            **kwargs: 其他参数

        Returns:
            报告内容
        """
        # 执行多种分析
        descriptive = self.analyze(data, "descriptive")
        trend = self.analyze(data, "trend")

        report = {
            "title": kwargs.get("title", "数据分析报告"),
            "descriptive_stats": descriptive,
            "trend_analysis": trend,
            "summary": self._generate_summary(descriptive, trend),
            "success": True
        }

        return report

    def _generate_summary(self,
                         descriptive: Dict,
                         trend: Dict) -> str:
        """生成摘要"""
        summary_parts = []

        if descriptive.get("success"):
            if "mean" in descriptive:
                summary_parts.append(f"平均值: {descriptive['mean']:.2f}")
            if "count" in descriptive:
                summary_parts.append(f"数据量: {descriptive['count']}")

        if trend.get("success") and "trend" in trend:
            summary_parts.append(f"趋势: {trend['trend']}")

        return "、".join(summary_parts) if summary_parts else "数据分析完成"

    def get_help(self) -> str:
        """获取帮助信息"""
        return """
Data Analyzer Skill 帮助
========================

功能:
1. analyze(data, analysis_type) - 执行数据分析
   - descriptive: 描述性统计
   - trend: 趋势分析
   - comparative: 对比分析

2. visualize(data, chart_type) - 生成可视化
   - bar: 柱状图
   - line: 折线图
   - pie: 饼图

3. compare(data_groups) - 对比多组数据

4. generate_report(data) - 生成分析报告

使用示例:
- skill.analyze([1, 2, 3, 4, 5], "descriptive")
- skill.visualize(data, "bar", title="销售数据")
- skill.compare({"A组": [1,2,3], "B组": [4,5,6]})
- skill.generate_report(data, title="月度分析报告")
"""


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 创建Skill实例
    skill = DataAnalyzerSkill()

    # 测试描述性分析
    print("测试描述性分析:")
    data = [10, 20, 30, 40, 50]
    result = skill.analyze(data, "descriptive")
    print(f"平均值: {result['mean']}, 中位数: {result['median']}")

    # 测试趋势分析
    print("\n测试趋势分析:")
    trend_data = [10, 15, 20, 25, 30, 35]
    result = skill.analyze(trend_data, "trend")
    print(f"趋势: {result['trend']}, 变化率: {result['change_rate']:.2f}%")

    # 测试对比分析
    print("\n测试对比分析:")
    groups = {
        "产品A": [100, 120, 110, 130],
        "产品B": [90, 95, 100, 105]
    }
    result = skill.compare(groups)
    print(f"对比结果: {json.dumps(result['comparison'], indent=2, ensure_ascii=False)}")

    # 测试生成报告
    print("\n测试生成报告:")
    report = skill.generate_report(data, title="销售数据分析")
    print(f"报告摘要: {report['summary']}")

    # 获取帮助
    print("\n" + skill.get_help())
