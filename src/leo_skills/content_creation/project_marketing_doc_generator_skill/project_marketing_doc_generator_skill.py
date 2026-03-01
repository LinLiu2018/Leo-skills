# -*- coding: utf-8 -*-
"""
Project Marketing Doc Generator Skill
=====================================
项目营销文档生成技能

功能:
- 生成项目介绍文档
- 生成销售说辞
- 生成宣传文案
- 生成竞品对比表
- 生成投资分析报告
"""
from leo_skills.core.base_executor import BaseExecutor

import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path


class ProjectMarketingDocGeneratorSkill(BaseExecutor):
    """
    项目营销文档生成器
    ==================
    为房地产等项目生成专业营销文档
    """

    def __init__(self, output_dir: str = "output/marketing_docs"):
        self.name = "project_marketing_doc_generator_skill"
        self.version = "1.0.0"
        self.description = "项目营销文档生成"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, action: str = "generate", **kwargs) -> Dict[str, Any]:
        """
        执行技能

        Args:
            action: 操作类型
                - generate: 生成文档
                - outline: 生成大纲
                - sales_talk: 生成销售说辞
                - competitor_compare: 竞品对比
                - investment_analysis: 投资分析
            **kwargs: 参数
                - project_name: 项目名称
                - project_type: 项目类型 (realestate/product/service)
                - target_audience: 目标客群
                - highlights: 项目亮点
                - competitors: 竞品列表
                - price: 价格
                - location: 位置

        Returns:
            执行结果
        """
        if action == "generate":
            return self._generate_document(**kwargs)
        elif action == "outline":
            return self._generate_outline(**kwargs)
        elif action == "sales_talk":
            return self._generate_sales_talk(**kwargs)
        elif action == "competitor_compare":
            return self._generate_competitor_compare(**kwargs)
        elif action == "investment_analysis":
            return self._generate_investment_analysis(**kwargs)
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def _generate_document(self, **kwargs) -> Dict[str, Any]:
        """生成完整营销文档"""
        project_name = kwargs.get("project_name", "未命名项目")
        project_type = kwargs.get("project_type", "realestate")
        target_audience = kwargs.get("target_audience", "潜在客户")
        highlights = kwargs.get("highlights", [])

        # 生成各部分内容
        outline = self._generate_outline(
            project_name=project_name,
            project_type=project_type,
            target_audience=target_audience,
            highlights=highlights
        )

        sales_talk = self._generate_sales_talk(
            project_name=project_name,
            highlights=highlights,
            target_audience=target_audience
        )

        # 竞品对比（如果有）
        competitors = kwargs.get("competitors", [])
        competitor_doc = {}
        if competitors:
            competitor_doc = self._generate_competitor_compare(
                project_name=project_name,
                competitors=competitors
            )

        # 投资分析（如果有价格）
        price = kwargs.get("price")
        investment_doc = {}
        if price:
            investment_doc = self._generate_investment_analysis(
                project_name=project_name,
                price=price,
                location=kwargs.get("location", "")
            )

        # 组装完整文档
        doc_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{project_name}_{timestamp}.md"

        full_content = self._assemble_document(
            project_name=project_name,
            project_type=project_type,
            outline=outline,
            sales_talk=sales_talk,
            competitor_doc=competitor_doc,
            investment_doc=investment_doc
        )

        # 保存文件
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_content)

        return {
            "status": "success",
            "document_id": doc_id,
            "project_name": project_name,
            "output_path": str(output_path),
            "sections": {
                "outline": outline.get("sections", []),
                "sales_talk": True,
                "competitor_compare": bool(competitor_doc),
                "investment_analysis": bool(investment_doc)
            }
        }

    def _generate_outline(self, **kwargs) -> Dict[str, Any]:
        """生成文档大纲"""
        project_name = kwargs.get("project_name", "项目")
        project_type = kwargs.get("project_type", "realestate")

        sections = []

        if project_type == "realestate":
            sections = [
                {"title": "项目概述", "content": f"{project_name}位于核心地段..."},
                {"title": "区位优势", "content": "交通便利，周边配套成熟..."},
                {"title": "产品特色", "content": "精品户型，南北通透..."},
                {"title": "周边配套", "content": "学校、医院、商业一站式..."},
                {"title": "投资价值", "content": "核心地段，增值潜力大..."},
                {"title": "购买流程", "content": "VIP登记 → 实地看房 → 签约付款..."},
            ]
        else:
            sections = [
                {"title": "产品介绍", "content": f"{project_name}是..."},
                {"title": "核心优势", "content": "技术领先，性价比高..."},
                {"title": "应用场景", "content": "适用于..."},
                {"title": "客户案例", "content": "已服务..."},
            ]

        return {
            "status": "success",
            "project_name": project_name,
            "sections": [s["title"] for s in sections],
            "details": sections
        }

    def _generate_sales_talk(self, **kwargs) -> Dict[str, Any]:
        """生成销售说辞"""
        project_name = kwargs.get("project_name", "项目")
        highlights = kwargs.get("highlights", [])
        target_audience = kwargs.get("target_audience", "客户")

        if not highlights:
            highlights = ["核心地段", "优质户型", "完善配套"]

        talk_points = []
        for i, hl in enumerate(highlights, 1):
            talk_points.append(f"{i}. {hl}：{self._get_highlight_description(hl)}")

        sales_script = f"""# {project_name} 销售说辞

## 开场白
您好！欢迎了解{project_name}，我是您的专属顾问...

## 项目亮点
{chr(10).join(talk_points)}

## 针对{target_audience}的核心卖点
- 满足您对品质生活的追求
- 投资自住两相宜
- 专业的物业服务保障

## 促成话术
请问您最关注哪方面？我们可以安排实地看房...

## 异议处理
- 价格偏高？→ 我们提供分期付款方案
- 位置偏远？→ 周边规划正在快速发展
- 考虑周期？→ 现在是最佳入手时机
"""

        return {
            "status": "success",
            "project_name": project_name,
            "target_audience": target_audience,
            "talk_points": highlights,
            "script": sales_script
        }

    def _get_highlight_description(self, highlight: str) -> str:
        """获取亮点的描述"""
        descriptions = {
            "核心地段": "位于城市核心区域，交通便利，生活配套完善",
            "优质户型": "南北通透，采光充足，空间利用率高",
            "完善配套": "学校、医院、商业中心一站式配齐",
            "投资价值": "核心资产，增值潜力大，租金回报率高",
            "品牌开发商": "知名开发商，品质保障，后期物业可靠",
            "景观资源": "紧邻公园/河景/山景，居住环境优美",
            "智能家居": "配备智能门锁、新风系统等科技配置",
            "低密度": "容积率低，居住舒适度高",
        }
        return descriptions.get(highlight, "优质特性，值得拥有")

    def _generate_competitor_compare(self, **kwargs) -> Dict[str, Any]:
        """生成竞品对比表"""
        project_name = kwargs.get("project_name", "本项目")
        competitors = kwargs.get("competitors", [])

        if not competitors:
            competitors = ["竞品A", "竞品B", "竞品C"]

        comparison_items = ["位置", "价格", "户型", "配套", "品牌", "物业"]

        rows = []
        for comp in competitors:
            row = {"项目": comp}
            for item in comparison_items:
                row[item] = self._get_competitor_score(comp, item)
            rows.append(row)

        # 本项目（优势）
        our_project = {"项目": f"★{project_name}"}
        for item in comparison_items:
            our_project[item] = "★★★★★"
        rows.insert(0, our_project)

        # 生成Markdown表格
        table_md = f"| 项目 | {' | '.join(comparison_items)} |\n"
        table_md += f"|---|{'---|'.join([''] * len(comparison_items))}\n"
        for row in rows:
            table_md += f"| {row['项目']} | "
            table_md += " | ".join([row.get(item, "-") for item in comparison_items])
            table_md += " |\n"

        return {
            "status": "success",
            "project_name": project_name,
            "competitors": competitors,
            "comparison_items": comparison_items,
            "table": table_md
        }

    def _get_competitor_score(self, competitor: str, item: str) -> str:
        """获取竞品评分（模拟）"""
        scores = {
            ("竞品A", "位置"): "★★★☆☆",
            ("竞品A", "价格"): "★★★★☆",
            ("竞品B", "位置"): "★★★★☆",
            ("竞品B", "价格"): "★★★☆☆",
            ("竞品C", "配套"): "★★★★☆",
        }
        return scores.get((competitor, item), "★★★☆☆")

    def _generate_investment_analysis(self, **kwargs) -> Dict[str, Any]:
        """生成投资分析报告"""
        project_name = kwargs.get("project_name", "项目")
        price = kwargs.get("price", 1000000)
        location = kwargs.get("location", "核心区")

        # 模拟投资回报计算
        try:
            price = float(price)
        except:
            price = 1000000

        # 假设数据
        initial_investment = price
        monthly_rent = price * 0.003  # 假设月租金为房价的0.3%
        annual_rent = monthly_rent * 12
        rent_return_rate = (annual_rent / initial_investment) * 100

        # 预计增值（模拟）
        appreciation_3y = initial_investment * 0.15  # 3年预计增值15%
        appreciation_5y = initial_investment * 0.30  # 5年预计增值30%

        analysis = f"""# {project_name} 投资分析报告

## 基本信息
- 项目名称: {project_name}
- 购买价格: ¥{price:,.0f}
- 所在区域: {location}

## 租金回报分析
- 预估月租金: ¥{monthly_rent:,.0f}
- 预估年租金: ¥{annual_rent:,.0f}
- 租金回报率: {rent_return_rate:.2f}%

## 增值潜力
- 3年预计增值: ¥{appreciation_3y:,.0f} (15%)
- 5年预计增值: ¥{appreciation_5y:,.0f} (30%)

## 综合收益（5年）
- 租金总收入: ¥{annual_rent * 5:,.0f}
- 增值收益: ¥{appreciation_5y:,.0f}
- 总收益: ¥{annual_rent * 5 + appreciation_5y:,.0f}
- 综合收益率: {((annual_rent * 5 + appreciation_5y) / initial_investment * 100):.1f}%

## 风险提示
1. 市场波动风险
2. 政策调控风险
3. 租金空置风险

## 建议
- 适合长期投资
- 建议出租获取稳定现金流
- 关注区域发展规划
"""

        return {
            "status": "success",
            "project_name": project_name,
            "price": price,
            "rent_return_rate": rent_return_rate,
            "analysis": analysis
        }

    def _assemble_document(self, project_name: str, project_type: str,
                           outline: Dict, sales_talk: Dict,
                           competitor_doc: Dict, investment_doc: Dict) -> str:
        """组装完整文档"""
        doc = f"""# {project_name} 营销手册

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**项目类型**: {project_type}

---

## 一、项目概述

{outline.get('details', [{}])[0].get('content', '') if outline.get('details') else ''}

---

## 二、文档大纲

"""
        for section in outline.get("details", []):
            doc += f"### {section['title']}\n{section['content']}\n\n"

        doc += f"---\n\n## 三、销售说辞\n\n{sales_talk.get('script', '')}\n\n"

        if competitor_doc.get("table"):
            doc += f"---\n\n## 四、竞品对比\n\n{competitor_doc['table']}\n\n"

        if investment_doc.get("analysis"):
            doc += f"---\n\n## 五、投资分析\n\n{investment_doc['analysis']}\n\n"

        doc += f"""---

*本文档由 ProjectMarketingDocGeneratorSkill 自动生成*
"""
        return doc


def main():
    """入口函数"""
    return ProjectMarketingDocGeneratorSkill()


if __name__ == "__main__":
    skill = main()

    # 测试生成营销文档
    result = skill.execute(
        action="generate",
        project_name="淮安建华官园",
        project_type="realestate",
        target_audience="改善型购房者",
        highlights=["核心地段", "优质户型", "完善配套", "品牌开发商"],
        price=1500000,
        location="淮安市清江浦区"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
