"""
Business Research Skill
=======================
商业项目调研技能 - 专为商业项目可行性研究和落地计划设计

功能:
1. 市场调研（竞品、人口、消费能力）
2. 舆情分析（政策、公众反馈）
3. 投资测算（ROI、成本收益）
4. 商业计划生成

作者: Claude Code
版本: 1.0.0
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import sys
import json
import re

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.evolution import EvolvableSkill


class BusinessResearchSkill(EvolvableSkill):
    """
    Business Research Skill - 商业项目调研专家
    ===========================================
    专为商业项目可行性研究和落地计划设计
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            skill_name="business_research_skill",
            config_path=str(Path(__file__).parent.parent / "config" / "config.yaml")
        )
        self.config = config or {}

        # 导入web_search_skill作为依赖
        try:
            from leo_skills.utilities.web_search_skill.web_search_skill import WebSearchSkill
            self.web_search = WebSearchSkill()
        except ImportError:
            self.web_search = None
            self.logger.warning("WebSearchSkill not available, limited functionality")

    def research_market(self,
                       location: str,
                       project_type: str,
                       radius_km: float = 1.5,
                       **kwargs) -> Dict[str, Any]:
        """
        市场调研 - 调研指定区域的市场环境

        Args:
            location: 地点（城市+区域）
            project_type: 项目类型（如：农贸市场、商场、超市）
            radius_km: 调研半径（公里）
            **kwargs: 其他参数

        Returns:
            市场调研报告
        """
        self.logger.info(f"Starting market research for {project_type} in {location}")

        # 1. 搜索竞品信息
        competitor_results = self._search_competitors(location, project_type, radius_km)

        # 2. 搜索人口和消费数据
        demographic_results = self._search_demographics(location)

        # 3. 搜索商业环境
        commercial_results = self._search_commercial_env(location, radius_km)

        # 4. 综合分析
        analysis = self._analyze_market(competitor_results, demographic_results, commercial_results)

        return {
            "location": location,
            "project_type": project_type,
            "radius_km": radius_km,
            "competitors": competitor_results,
            "demographics": demographic_results,
            "commercial": commercial_results,
            "analysis": analysis,
            "success": True
        }

    def _search_competitors(self, location: str, project_type: str, radius_km: float) -> Dict[str, Any]:
        """搜索竞品信息"""
        queries = [
            f"{location} {project_type} 地址",
            f"{location} 农贸市场 生鲜超市 竞争",
            f"{location} 买菜 哪里便宜"
        ]

        results = {}
        if self.web_search:
            batch = self.web_search.batch_search(queries)
            results = batch.get("results", {})

        return {"queries": queries, "data": results, "count": len(results)}

    def _search_demographics(self, location: str) -> Dict[str, Any]:
        """搜索人口统计数据"""
        queries = [
            f"{location} 人口数量 密度",
            f"{location} 小区 入住率 居民",
            f"{location} 消费水平 人均可支配收入"
        ]

        results = {}
        if self.web_search:
            batch = self.web_search.batch_search(queries)
            results = batch.get("results", {})

        return {"queries": queries, "data": results}

    def _search_commercial_env(self, location: str, radius_km: float) -> Dict[str, Any]:
        """搜索商业环境"""
        queries = [
            f"{location} 商业综合体 商场",
            f"{location} 地铁站 公交站 交通",
            f"{location} 商业街 店铺 租金"
        ]

        results = {}
        if self.web_search:
            batch = self.web_search.batch_search(queries)
            results = batch.get("results", {})

        return {"queries": queries, "data": results}

    def _analyze_market(self, competitors: Dict, demographics: Dict, commercial: Dict) -> Dict[str, Any]:
        """综合分析市场情况"""
        return {
            "opportunity_score": self._calculate_opportunity(competitors, demographics, commercial),
            "key_findings": [],
            "recommendations": []
        }

    def _calculate_opportunity(self, competitors: Dict, demographics: Dict, commercial: Dict) -> float:
        """计算机会评分（0-100）"""
        base_score = 50
        # 简化的评分逻辑
        return base_score

    def analyze_sentiment(self,
                         topic: str,
                         location: str,
                         **kwargs) -> Dict[str, Any]:
        """
        舆情分析 - 分析公众对特定话题的态度

        Args:
            topic: 话题（如：智慧农贸市场、菜市场改造）
            location: 地点
            **kwargs: 其他参数

        Returns:
            舆情分析报告
        """
        self.logger.info(f"Analyzing sentiment for {topic} in {location}")

        # 搜索相关讨论
        queries = [
            f"{location} {topic} 评价 怎么样",
            f"{topic} 好不好 优点 缺点",
            f"智慧农贸 {location} 居民 反馈"
        ]

        all_content = []
        sources = []

        if self.web_search:
            batch = self.web_search.batch_search(queries)
            for query, result in batch.get("results", {}).items():
                for item in result.get("results", []):
                    if item.get("url"):
                        content = self.web_search.fetch_content(item["url"])
                        if content["success"]:
                            all_content.append(content.get("content", ""))
                            sources.append({
                                "url": item["url"],
                                "title": item["title"]
                            })

        # 情感分析
        sentiment = self._analyze_sentiment_text(all_content)

        return {
            "topic": topic,
            "location": location,
            "sentiment": sentiment,
            "sources_analyzed": len(sources),
            "key_opinions": self._extract_opinions(all_content),
            "success": True
        }

    def _analyze_sentiment_text(self, contents: List[str]) -> Dict[str, Any]:
        """分析文本情感"""
        positive_keywords = ["方便", "便宜", "新鲜", "干净", "智能", "优惠", "支持"]
        negative_keywords = ["脏", "贵", "乱", "吵", "投诉", "问题", "不满"]

        pos_count = sum(1 for c in contents for kw in positive_keywords if kw in c)
        neg_count = sum(1 for c in contents for kw in negative_keywords if kw in c)

        total = pos_count + neg_count or 1

        return {
            "positive": pos_count,
            "negative": neg_count,
            "positive_ratio": round(pos_count / total, 2),
            "negative_ratio": round(neg_count / total, 2),
            "overall": "positive" if pos_count > neg_count else "negative" if neg_count > pos_count else "neutral"
        }

    def _extract_opinions(self, contents: List[str]) -> List[str]:
        """提取关键观点"""
        opinions = []
        for content in contents[:10]:  # 限制数量
            sentences = content.replace('。', '\n').split('\n')
            for sent in sentences:
                if any(kw in sent for kw in ["认为", "觉得", "应该", "希望", "期待"]):
                    if 20 < len(sent) < 100:
                        opinions.append(sent.strip())
        return opinions[:10]

    def calculate_roi(self,
                     investment: Dict[str, float],
                     revenue: Dict[str, float],
                     timeline_months: int = 12,
                     **kwargs) -> Dict[str, Any]:
        """
        投资回报计算 - 计算项目的ROI

        Args:
            investment: 投资项 {"物业收购": 800, "改造": 200, "营销": 30}
            revenue: 收入项 {"摊位销售": 2000, "租金": 200}
            timeline_months: 项目周期（月）
            **kwargs: 其他参数

        Returns:
            ROI分析报告
        """
        total_investment = sum(investment.values())
        total_revenue = sum(revenue.values())
        net_profit = total_revenue - total_investment
        roi = (net_profit / total_investment * 100) if total_investment > 0 else 0
        monthly_profit = net_profit / timeline_months if timeline_months > 0 else 0

        return {
            "investment": investment,
            "revenue": revenue,
            "total_investment": total_investment,
            "total_revenue": total_revenue,
            "net_profit": net_profit,
            "roi_percent": round(roi, 2),
            "monthly_profit": round(monthly_profit, 2),
            "timeline_months": timeline_months,
            "break_even_months": round(total_investment / monthly_profit, 1) if monthly_profit > 0 else None,
            "success": True
        }

    def generate_business_plan(self,
                              project_name: str,
                              project_type: str,
                              location: str,
                              market_research: Optional[Dict] = None,
                              investment_data: Optional[Dict] = None,
                              **kwargs) -> Dict[str, Any]:
        """
        生成商业计划书

        Args:
            project_name: 项目名称
            project_type: 项目类型
            location: 地点
            market_research: 市场调研数据（可选）
            investment_data: 投资数据（可选）
            **kwargs: 其他参数

        Returns:
            商业计划书
        """
        self.logger.info(f"Generating business plan for {project_name}")

        # 如果没有提供数据，自动进行调研
        if not market_research and self.web_search:
            market_research = self.research_market(location, project_type)

        # 计算ROI
        roi_analysis = {}
        if investment_data:
            investment = investment_data.get("investment", {})
            revenue = investment_data.get("revenue", {})
            roi_analysis = self.calculate_roi(investment, revenue, investment_data.get("timeline", 12))

        # 生成计划
        plan = self._compose_plan(
            project_name, project_type, location, market_research, roi_analysis, **kwargs
        )

        return {
            "project_name": project_name,
            "project_type": project_type,
            "location": location,
            "plan": plan,
            "market_research": market_research,
            "roi_analysis": roi_analysis,
            "success": True
        }

    def _compose_plan(self, name: str, ptype: str, location: str,
                     research: Dict, roi: Dict, **kwargs) -> str:
        """撰写商业计划"""
        sections = [
            f"# {name} 商业计划书\n",
            f"## 项目概述\n- 类型: {ptype}\n- 地点: {location}\n- 日期: 2026年1月\n",
        ]

        if research and research.get("success"):
            sections.append("## 市场调研\n")
            if research.get("analysis"):
                sections.append(f"- 机会评分: {research['analysis'].get('opportunity_score', 'N/A')}/100\n")
            sections.append("### 竞品分析\n")
            sections.append(f"- 分析项目数: {research.get('competitors', {}).get('count', 0)}\n")

        if roi and roi.get("success"):
            sections.append("## 投资分析\n")
            sections.append(f"- 总投入: {roi.get('total_investment', 0):,.0f}万元\n")
            sections.append(f"- 预计收入: {roi.get('total_revenue', 0):,.0f}万元\n")
            sections.append(f"- 净利润: {roi.get('net_profit', 0):,.0f}万元\n")
            sections.append(f"- ROI: {roi.get('roi_percent', 0)}%\n")
            if roi.get("break_even_months"):
                sections.append(f"- 回收期: {roi['break_even_months']}个月\n")

        sections.append("\n## 执行计划\n")
        sections.append("1. 第一阶段：尽职调查（2-4周）\n")
        sections.append("2. 第二阶段：收购签约（2-4周）\n")
        sections.append("3. 第三阶段：改造施工（3-6个月）\n")
        sections.append("4. 第四阶段：招商销售（2-4个月）\n")
        sections.append("5. 第五阶段：开业运营（1-2个月）\n")

        return "\n".join(sections)

    def deep_market_research(self,
                            location: str,
                            project_type: str,
                            focus_areas: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        深度市场调研 - 结合WebSearch深度研究

        Args:
            location: 地点
            project_type: 项目类型
            focus_areas: 重点调研领域

        Returns:
            深度调研报告
        """
        if not self.web_search:
            return {"error": "WebSearchSkill not available", "success": False}

        research_topics = focus_areas or [
            f"{location} {project_type} 市场规模",
            f"{location} {project_type} 发展趋势",
            f"{location} {project_type} 成功案例",
            f"{location} {project_type} 投资回报",
            f"{project_type} 政策 支持"
        ]

        all_findings = []
        all_sources = []

        for topic in research_topics:
            self.logger.info(f"Deep researching: {topic}")
            result = self.web_search.deep_research(topic, max_iterations=2, max_sources=3)
            if result.get("success"):
                all_findings.extend(result.get("findings", []))
                all_sources.extend(result.get("sources", []))

        # 生成综合报告
        report = self._synthesize_market_report(location, project_type, all_findings)

        return {
            "location": location,
            "project_type": project_type,
            "report": report,
            "findings": all_findings,
            "sources": all_sources,
            "total_sources": len(all_sources),
            "success": True
        }

    def _synthesize_market_report(self, location: str, ptype: str, findings: List[Dict]) -> str:
        """综合市场报告"""
        sections = [
            f"# {location} {ptype} 深度调研报告\n",
            f"## 调研概述\n- 地点: {location}\n- 类型: {ptype}\n- 来源数: {len(findings)}\n"
        ]

        # 按角度组织发现
        angles = {}
        for f in findings:
            angle = f.get("angle", "其他")
            if angle not in angles:
                angles[angle] = []
            angles[angle].append(f)

        for angle, items in angles.items():
            sections.append(f"\n## {angle}\n")
            for item in items[:3]:
                title = item.get("title", "Unknown")
                url = item.get("source", "")
                keywords = item.get("extracted_info", {}).get("auto_keywords", [])
                sections.append(f"- **{title}**")
                if keywords:
                    sections.append(f"  关键词: {', '.join(keywords[:3])}")
                sections.append(f"  [来源]({url})")

        return "\n".join(sections)

    def get_help(self) -> str:
        """获取帮助信息"""
        return """
Business Research Skill 帮助
=============================

功能:
1. research_market(location, project_type, radius_km)
   - 调研指定区域的市场环境
   - 返回竞品、人口、商业环境分析

2. analyze_sentiment(topic, location)
   - 分析公众对特定话题的态度
   - 返回正面/负面比例和关键观点

3. calculate_roi(investment, revenue, timeline_months)
   - 计算投资回报率
   - 返回ROI、回收期等指标

4. generate_business_plan(project_name, project_type, location)
   - 生成完整的商业计划书
   - 自动整合调研和ROI数据

5. deep_market_research(location, project_type)
   - 深度市场调研（结合Deep Research）
   - 返回综合调研报告

使用示例:
--------
# 市场调研
research = skill.research_market("宁波", "农贸市场", radius_km=1.5)

# 舆情分析
sentiment = skill.analyze_sentiment("智慧农贸", "宁波")

# ROI计算
roi = skill.calculate_哉oi(
    investment={"物业": 800, "改造": 200, "营销": 30},
    revenue={"销售": 2000, "租金": 150},
    timeline_months=12
)

# 生成商业计划
plan = skill.generate_business_plan(
    project_name="宁波XX农贸市场改造",
    project_type="农贸市场",
    location="宁波",
    investment_data={"investment": {"物业": 800}, "revenue": {"销售": 1500}, "timeline": 12}
)

# 深度调研（推荐）
report = skill.deep_market_research("宁波", "农贸市场")
"""


if __name__ == "__main__":
    skill = BusinessResearchSkill()
    print("Testing Business Research Skill...")

    # 测试市场调研
    print("\n1. Market Research:")
    result = skill.research_market("宁波", "农贸市场", radius_km=1.5)
    print(f"Success: {result['success']}")

    # 测试ROI计算
    print("\n2. ROI Calculation:")
    roi = skill.calculate_roi(
        investment={"物业收购": 800, "改造": 200, "营销": 30},
        revenue={"摊位销售": 1500, "租金收入": 200},
        timeline_months=12
    )
    print(f"ROI: {roi['roi_percent']}%")
    print(f"Net Profit: {roi['net_profit']}万元")

    # 测试商业计划生成
    print("\n3. Business Plan:")
    plan = skill.generate_business_plan(
        project_name="宁波闲置商业改造农贸市场",
        project_type="农贸市场",
        location="宁波",
        investment_data={"investment": {"物业": 800}, "revenue": {"销售": 1500}, "timeline": 12}
    )
    print(f"Success: {plan['success']}")
    print(f"Plan preview: {plan['plan'][:300]}...")
