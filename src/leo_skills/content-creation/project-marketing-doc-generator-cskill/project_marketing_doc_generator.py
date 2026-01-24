#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目营销文档生成器 - 可进化版本
"""

import sys
import io
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加leo-skills到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.evolution import EvolvableSkill


class ProjectMarketingDocGenerator(EvolvableSkill):
    """项目营销文档生成器"""

    def __init__(self):
        super().__init__(
            skill_name="project-marketing-doc-generator-cskill",
            config_path=str(Path(__file__).parent / "config" / "config.yaml")
        )

    def _execute_core(self, action: str = "generate", **kwargs) -> Dict[str, Any]:
        """核心执行逻辑"""
        if action == "generate_handbook":
            return self.generate_marketing_handbook(**kwargs)
        elif action == "generate_quick_card":
            return self.generate_quick_reference_card(**kwargs)
        elif action == "generate_all":
            return self.generate_all_documents(**kwargs)
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}",
                "quality_score": 0.0
            }

    def generate_marketing_handbook(self, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """生成全案营销手册"""
        try:
            handbook = self._build_handbook(project_info)

            return {
                "success": True,
                "document": handbook,
                "type": "handbook",
                "quality_score": 0.9
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "quality_score": 0.0
            }

    def generate_quick_reference_card(self, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """生成销售速查卡"""
        try:
            card = self._build_quick_card(project_info)

            return {
                "success": True,
                "document": card,
                "type": "quick_card",
                "quality_score": 0.85
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "quality_score": 0.0
            }

    def generate_all_documents(self, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """生成所有文档"""
        try:
            handbook = self._build_handbook(project_info)
            card = self._build_quick_card(project_info)

            return {
                "success": True,
                "handbook": handbook,
                "quick_card": card,
                "quality_score": 0.9
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "quality_score": 0.0
            }

    def _build_handbook(self, info: Dict[str, Any]) -> str:
        """构建营销手册"""
        sections = []

        # 标题
        sections.append(f"# {info.get('project_name', '项目')}全案营销手册\n")
        sections.append(f"生成时间：{datetime.now().strftime('%Y年%m月%d日')}\n")

        # 1. 项目基础信息
        sections.append("\n## 一、项目基础信息\n")
        sections.append(f"**项目名称**：{info.get('project_name', 'N/A')}\n")
        sections.append(f"**项目位置**：{info.get('location', 'N/A')}\n")
        sections.append(f"**项目面积**：{info.get('area', 'N/A')}\n")
        sections.append(f"**楼层/摊位**：{info.get('floors_stalls', 'N/A')}\n")
        sections.append(f"**预计开业**：{info.get('opening_date', 'N/A')}\n")
        sections.append(f"**招商联系**：{info.get('contact', 'N/A')}\n")

        # 2. 租金价格与业态规划
        sections.append("\n## 二、租金价格与业态规划\n")
        if 'rent_info' in info:
            sections.append("\n### 租金价格表\n")
            for category, details in info['rent_info'].items():
                sections.append(f"- **{category}**：{details}\n")

        # 3. 投资回报测算
        sections.append("\n## 三、投资回报测算\n")
        sections.append("### 投资成本分析\n")
        sections.append("- 租金成本\n")
        sections.append("- 装修成本\n")
        sections.append("- 运营成本\n")
        sections.append("\n### 收益预测\n")
        sections.append("- 月均营业额预估\n")
        sections.append("- 年度收益预测\n")
        sections.append("- 投资回报周期\n")

        # 4. 目标客群分析
        sections.append("\n## 四、目标客群分析\n")
        sections.append(f"**辐射人口**：{info.get('target_population', '待调研')}\n")
        sections.append("**主要客群**：\n")
        sections.append("- 周边社区居民\n")
        sections.append("- 商务办公人群\n")
        sections.append("- 流动消费人群\n")

        # 5. 核心卖点
        sections.append("\n## 五、核心卖点\n")
        if 'selling_points' in info:
            for i, point in enumerate(info['selling_points'], 1):
                sections.append(f"{i}. {point}\n")
        else:
            sections.append("1. 地理位置优越\n")
            sections.append("2. 配套设施完善\n")
            sections.append("3. 人流量稳定\n")
            sections.append("4. 投资回报可观\n")
            sections.append("5. 政策支持有力\n")

        # 6. 销售话术
        sections.append("\n## 六、销售话术与异议处理\n")
        sections.append("### 开场话术\n")
        sections.append(f"您好！我是{info.get('project_name', '项目')}的招商顾问...\n")
        sections.append("\n### 常见异议处理\n")
        sections.append("**Q: 租金是否可以优惠？**\n")
        sections.append("A: 我们的租金定价是经过市场调研的...\n")

        return "".join(sections)

    def _build_quick_card(self, info: Dict[str, Any]) -> str:
        """构建速查卡"""
        sections = []

        sections.append(f"# {info.get('project_name', '项目')}销售速查卡\n")
        sections.append("=" * 50 + "\n")

        # 基本信息
        sections.append("\n## 📍 基本信息\n")
        sections.append(f"项目：{info.get('project_name', 'N/A')}\n")
        sections.append(f"位置：{info.get('location', 'N/A')}\n")
        sections.append(f"面积：{info.get('area', 'N/A')}\n")
        sections.append(f"开业：{info.get('opening_date', 'N/A')}\n")
        sections.append(f"联系：{info.get('contact', 'N/A')}\n")

        # 租金速查
        sections.append("\n## 💰 租金速查\n")
        if 'rent_info' in info:
            for category, details in info['rent_info'].items():
                sections.append(f"- {category}：{details}\n")

        # 核心卖点
        sections.append("\n## [STAR] 核心卖点（5条）\n")
        if 'selling_points' in info:
            for i, point in enumerate(info['selling_points'][:5], 1):
                sections.append(f"{i}. {point}\n")

        # 快速话术
        sections.append("\n## 💬 快速话术\n")
        sections.append(f"这个项目位于{info.get('location', '优越位置')}，")
        sections.append(f"总面积{info.get('area', 'N/A')}，")
        sections.append(f"预计{info.get('opening_date', '近期')}开业。\n")

        sections.append("\n" + "=" * 50 + "\n")

        return "".join(sections)


def main():
    """主函数"""
    # 示例使用
    generator = ProjectMarketingDocGenerator()

    # 示例项目信息
    project_info = {
        "project_name": "建华官园智慧农贸",
        "location": "淮安生态新城·建华观园南侧",
        "area": "约3500㎡",
        "floors_stalls": "3层，86个摊位",
        "opening_date": "2026年12月10日",
        "contact": "158****6696",
        "target_population": "约14万",
        "rent_info": {
            "A类": "10-15㎡，年租金12000元",
            "B类": "5-10㎡，年租金8000元",
            "C类": "~5㎡，年租金3500元"
        },
        "selling_points": [
            "地理位置优越，紧邻主干道",
            "周边社区密集，人流量大",
            "智慧化管理，现代化设施",
            "政府支持，配套完善",
            "投资回报稳定，风险可控"
        ]
    }

    result = generator.execute(action="generate_all", project_info=project_info)

    if result.success:
        print("[SUCCESS] 文档生成成功")
        print("\n" + "="*60)
        print(result.data.get("handbook", ""))
        print("\n" + "="*60)
        print(result.data.get("quick_card", ""))
    else:
        print(f"[ERROR] 生成失败: {result.error}")


if __name__ == "__main__":
    main()
