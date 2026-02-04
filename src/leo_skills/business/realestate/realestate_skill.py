# -*- coding: utf-8 -*-
"""
realestate_skill - 房地产运营技能

提供房产数据分析、价格评估、市场分析和投资建议功能。
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class PropertyType(Enum):
    """房产类型"""
    RESIDENTIAL = "residential"      # 住宅
    COMMERCIAL = "commercial"        # 商业
    OFFICE = "office"                # 办公
    INDUSTRIAL = "industrial"        # 工业
    LAND = "land"                    # 土地


class TransactionType(Enum):
    """交易类型"""
    SALE = "sale"        # 出售
    RENT = "rent"        # 出租
    LEASE = "lease"      # 租赁


@dataclass
class PropertyInfo:
    """房产信息"""
    name: str
    address: str
    property_type: str
    area: float          # 面积（平方米）
    price: float         # 价格
    transaction_type: str = "sale"
    bedrooms: int = 0
    floor: int = 0
    total_floors: int = 0
    year_built: int = 0
    location_score: float = 0.0


@dataclass
class MarketAnalysis:
    """市场分析"""
    avg_price: float
    avg_rent: float
    price_change: float
    rent_change: float
    inventory: int
    days_on_market: float


class RealEstateSkill:
    """
    房地产运营技能

    功能：
    - 房产信息管理
    - 价格评估分析
    - 市场趋势分析
    - 投资回报计算
    - 房源匹配推荐
    - 市场报告生成

    使用场景：
    - 房产价格评估
    - 市场行情分析
    - 投资决策支持
    - 房源搜索优化
    - 风险评估
    """

    def __init__(self):
        self.name = "realestate_skill"
        self.version = "1.0.0"
        self.description = "房地产运营技能 - 提供房产分析和管理功能"

        # 示例市场数据
        self.market_data = {
            "residential": {
                "avg_price": 35000,  # 元/平米
                "avg_rent": 80,      # 元/平米/月
                "price_change": 3.5,
                "rent_change": 2.1,
                "inventory": 12000,
                "days_on_market": 45
            },
            "commercial": {
                "avg_price": 50000,
                "avg_rent": 150,
                "price_change": 2.0,
                "rent_change": 1.5,
                "inventory": 3000,
                "days_on_market": 90
            }
        }

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行房地产操作

        Args:
            action: 操作类型
                - evaluate: 房产评估
                - analyze_market: 市场分析
                - calculate_investment: 投资计算
                - recommend: 房源推荐
                - analyze_trend: 趋势分析
                - generate_report: 生成报告
            property_info: 房产信息
            location: 位置
            property_type: 房产类型

        Returns:
            Dict 包含执行结果
        """
        action = kwargs.get("action", "evaluate")

        try:
            if action == "evaluate":
                return self._evaluate_property(kwargs)
            elif action == "analyze_market":
                return self._analyze_market(kwargs)
            elif action == "calculate_investment":
                return self._calculate_investment(kwargs)
            elif action == "recommend":
                return self._recommend_properties(kwargs)
            elif action == "analyze_trend":
                return self._analyze_trend(kwargs)
            elif action == "generate_report":
                return self._generate_report(kwargs)
            else:
                return {"status": "error", "message": f"Unknown action: {action}"}

        except Exception as e:
            return {"status": "error", "error": str(e), "skill": self.name}

    def _evaluate_property(self, kwargs: Dict) -> Dict[str, Any]:
        """房产评估"""
        property_info = kwargs.get("property_info", {})
        location = kwargs.get("location", "")

        name = property_info.get("name", "")
        area = property_info.get("area", 0)
        property_type = property_info.get("property_type", "residential")
        transaction_type = property_info.get("transaction_type", "sale")

        if not name or area <= 0:
            return {"status": "error", "message": "Property name and area are required"}

        # 获取市场基准价
        market = self.market_data.get(property_type, self.market_data["residential"])
        base_price = market["avg_price"] if transaction_type == "sale" else market["avg_rent"]

        # 位置系数
        location_score = property_info.get("location_score", 0.5)
        location_factor = 0.8 + location_score * 0.4  # 0.8 - 1.2

        # 房龄系数
        year_built = property_info.get("year_built", 2020)
        age = datetime.now().year - year_built
        age_factor = 1.0 - max(0, age - 5) * 0.005  # 每超过5年减0.5%，最低0.7

        # 楼层系数
        floor = property_info.get("floor", 0)
        total_floors = property_info.get("total_floors", 1)
        if total_floors > 1:
            floor_factor = 0.9 + (floor / total_floors) * 0.2
        else:
            floor_factor = 1.0

        # 计算评估价
        if transaction_type == "sale":
            estimated_price = base_price * area * location_factor * age_factor * floor_factor
            price_per_sqm = estimated_price / area
            evaluation = {
                "estimated_price": round(estimated_price, 2),
                "price_per_sqm": round(price_per_sqm, 2),
                "market_range": {
                    "low": round(price_per_sqm * 0.9, 2),
                    "high": round(price_per_sqm * 1.1, 2)
                },
                "factors": {
                    "location_factor": round(location_factor, 3),
                    "age_factor": round(age_factor, 3),
                    "floor_factor": round(floor_factor, 3)
                }
            }
        else:
            estimated_rent = base_price * area * location_factor * floor_factor
            rent_per_sqm = estimated_rent / area
            evaluation = {
                "estimated_rent": round(estimated_rent, 2),
                "rent_per_sqm": round(rent_per_sqm, 2),
                "market_range": {
                    "low": round(rent_per_sqm * 0.9, 2),
                    "high": round(rent_per_sqm * 1.1, 2)
                },
                "factors": {
                    "location_factor": round(location_factor, 3),
                    "floor_factor": round(floor_factor, 3)
                }
            }

        # 评估建议
        suggestions = self._get_evaluation_suggestions(property_info, evaluation)

        return {
            "status": "success",
            "skill": self.name,
            "property": name,
            "evaluation": evaluation,
            "suggestions": suggestions
        }

    def _get_evaluation_suggestions(self, property_info: Dict, evaluation: Dict) -> List[str]:
        """获取评估建议"""
        suggestions = []

        if property_info.get("year_built", 2020) < 2010:
            suggestions.append("房龄较老，建议关注维护成本和改造潜力")
        if property_info.get("floor", 0) == 0:
            suggestions.append("考虑楼层对采光和噪音的影响")
        if property_info.get("location_score", 0.5) < 0.5:
            suggestions.append("位置评分一般，可考虑交通改善规划")

        return suggestions

    def _analyze_market(self, kwargs: Dict) -> Dict[str, Any]:
        """市场分析"""
        location = kwargs.get("location", "全市")
        property_type = kwargs.get("property_type", "residential")

        market = self.market_data.get(property_type, self.market_data["residential"])

        # 市场状况评估
        if market["price_change"] > 3:
            market_status = "上涨趋势"
        elif market["price_change"] > 0:
            market_status = "温和上涨"
        elif market["price_change"] > -3:
            market_status = "轻微调整"
        else:
            market_status = "下行压力"

        analysis = {
            "location": location,
            "property_type": property_type,
            "market_status": market_status,
            "avg_price": market["avg_price"],
            "avg_rent": market["avg_rent"],
            "price_change_12m": f"{market['price_change']}%",
            "rent_change_12m": f"{market['rent_change']}%",
            "inventory": market["inventory"],
            "avg_days_on_market": market["days_on_market"],
            "investment_score": self._calculate_investment_score(market),
            "recommendation": self._get_market_recommendation(market)
        }

        return {
            "status": "success",
            "skill": self.name,
            "analysis": analysis
        }

    def _calculate_investment_score(self, market: Dict) -> int:
        """计算投资评分"""
        score = 50  # 基础分

        # 价格变化加分
        if market["price_change"] > 3:
            score += 20
        elif market["price_change"] > 0:
            score += 10

        # 租金收益加分
        if market["avg_rent"] > 100:
            score += 15
        elif market["avg_rent"] > 50:
            score += 10

        # 流动性加分
        if market["days_on_market"] < 30:
            score += 15
        elif market["days_on_market"] < 60:
            score += 10

        return min(100, score)

    def _get_market_recommendation(self, market: Dict) -> str:
        """获取市场建议"""
        if market["price_change"] > 5 and market["days_on_market"] < 30:
            return "市场活跃，适合买入"
        elif market["price_change"] < -5:
            return "市场调整期，建议观望"
        elif market["avg_rent"] > 120:
            return "租金收益可观，适合长期持有"
        else:
            return "市场平稳，根据需求决策"

    def _calculate_investment(self, kwargs: Dict) -> Dict[str, Any]:
        """投资计算"""
        property_price = kwargs.get("property_price", 0)
        down_payment = kwargs.get("down_payment", 0)
        loan_term = kwargs.get("loan_term", 30)  # 年
        interest_rate = kwargs.get("interest_rate", 4.5)  # %
        rent_per_month = kwargs.get("rent_per_month", 0)
        annual_expenses = kwargs.get("annual_expenses", property_price * 0.02)

        if property_price <= 0:
            return {"status": "error", "message": "Property price is required"}

        # 贷款计算
        loan_amount = property_price - down_payment
        monthly_rate = interest_rate / 100 / 12
        num_payments = loan_term * 12

        # 月供计算
        if interest_rate > 0:
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
        else:
            monthly_payment = loan_amount / num_payments

        # 租金收益
        monthly_rent = rent_per_month
        net_monthly_income = monthly_rent - monthly_payment - (annual_expenses / 12)

        # 年化收益
        total_investment = down_payment + (annual_expenses * loan_term)  # 简化的总投资
        annual_return = (net_monthly_income * 12 + property_price * 0.03) / total_investment * 100  # 假设房产增值3%

        return {
            "status": "success",
            "skill": self.name,
            "investment": {
                "property_price": property_price,
                "loan_amount": round(loan_amount, 2),
                "monthly_payment": round(monthly_payment, 2),
                "monthly_rent": monthly_rent,
                "net_monthly_income": round(net_monthly_income, 2),
                "annual_return_rate": f"{round(annual_return, 2)}%",
                "break_even_years": round(abs(down_payment) / (net_monthly_income * 12), 1) if net_monthly_income != 0 else float('inf'),
                "suggestion": self._get_investment_suggestion(annual_return)
            }
        }

    def _get_investment_suggestion(self, return_rate: float) -> str:
        """获取投资建议"""
        if return_rate > 8:
            return "投资回报优秀，值得考虑"
        elif return_rate > 5:
            return "回报合理，可以考虑"
        elif return_rate > 0:
            return "回报较低，需谨慎考虑"
        else:
            return "负现金流，建议调整策略"

    def _recommend_properties(self, kwargs: Dict) -> Dict[str, Any]:
        """房源推荐"""
        budget = kwargs.get("budget", 500000)
        property_type = kwargs.get("property_type", "residential")
        min_area = kwargs.get("min_area", 50)
        location = kwargs.get("location", "")

        # 模拟房源数据
        sample_properties = [
            {
                "name": "阳光雅苑",
                "address": f"{location}XX路123号",
                "area": 89,
                "price": 3200000,
                "price_per_sqm": 35955,
                "bedrooms": 2,
                "location_score": 0.8
            },
            {
                "name": "中央大厦",
                "address": f"{location}YY路456号",
                "area": 120,
                "price": 4800000,
                "price_per_sqm": 40000,
                "bedrooms": 3,
                "location_score": 0.9
            },
            {
                "name": "湖畔家园",
                "address": f"{location}ZZ路789号",
                "area": 75,
                "price": 2700000,
                "price_per_sqm": 36000,
                "bedrooms": 2,
                "location_score": 0.7
            }
        ]

        # 过滤
        recommendations = []
        for prop in sample_properties:
            if prop["price"] <= budget and prop["area"] >= min_area:
                if property_type == "residential" or prop["price"] <= budget * 1.5:
                    prop["match_score"] = self._calculate_match_score(prop, kwargs)
                    recommendations.append(prop)

        # 按匹配度排序
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)

        return {
            "status": "success",
            "skill": self.name,
            "recommendations": recommendations[:5],
            "total_found": len(recommendations)
        }

    def _calculate_match_score(self, prop: Dict, criteria: Dict) -> int:
        """计算匹配分数"""
        score = 0

        budget = criteria.get("budget", float('inf'))
        if prop["price"] <= budget * 0.8:
            score += 30
        elif prop["price"] <= budget:
            score += 20

        location_score = prop.get("location_score", 0.5)
        score += location_score * 30

        bedrooms = criteria.get("bedrooms", 0)
        if bedrooms > 0 and prop.get("bedrooms", 0) >= bedrooms:
            score += 20

        return min(100, score)

    def _analyze_trend(self, kwargs: Dict) -> Dict[str, Any]:
        """趋势分析"""
        property_type = kwargs.get("property_type", "residential")
        period = kwargs.get("period", "12m")

        market = self.market_data.get(property_type, self.market_data["residential"])

        # 生成趋势数据
        trend_data = []
        base_price = market["avg_price"]
        months = 12 if period == "12m" else 24

        for i in range(months):
            month_price = base_price * (1 + market["price_change"] / 100 / 12 * (i + 1))
            trend_data.append({
                "month": f"2024-{i + 1:02d}",
                "price": round(month_price, 2)
            })

        return {
            "status": "success",
            "skill": self.name,
            "trend": {
                "property_type": property_type,
                "period": period,
                "current_price": base_price,
                "change_12m": market["price_change"],
                "data_points": trend_data
            }
        }

    def _generate_report(self, kwargs: Dict) -> Dict[str, Any]:
        """生成报告"""
        report_type = kwargs.get("report_type", "market")
        location = kwargs.get("location", "全市")

        report_templates = {
            "market": {
                "title": f"{location}房地产市场报告",
                "sections": ["市场概况", "价格分析", "热点区域", "投资建议"]
            },
            "valuation": {
                "title": "房产估值报告",
                "sections": ["基本信息", "估值分析", "比较分析", "风险提示"]
            },
            "investment": {
                "title": "投资分析报告",
                "sections": ["投资概况", "收益测算", "风险评估", "建议结论"]
            }
        }

        template = report_templates.get(report_type, report_templates["market"])

        return {
            "status": "success",
            "skill": self.name,
            "report": {
                "type": report_type,
                "title": template["title"],
                "sections": template["sections"],
                "generated_at": datetime.now().isoformat()
            }
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "features": [
                "property_evaluation",
                "market_analysis",
                "investment_calculation",
                "property_recommendation",
                "trend_analysis",
                "report_generation"
            ],
            "property_types": [t.value for t in PropertyType],
            "transaction_types": [t.value for t in TransactionType]
        }


# 向后兼容
Real_Estate_Skill = RealEstateSkill


def main():
    """入口函数 - 演示用法"""
    print("=" * 60)
    print("Real Estate Skill - 演示")
    print("=" * 60)

    skill = RealEstateSkill()

    # 演示1: 房产评估
    print("\n1. 房产评估")
    print("-" * 40)
    result = skill.execute(
        action="evaluate",
        property_info={
            "name": "阳光小区A栋",
            "area": 120,
            "property_type": "residential",
            "transaction_type": "sale",
            "bedrooms": 3,
            "floor": 15,
            "total_floors": 30,
            "year_built": 2018,
            "location_score": 0.8
        }
    )
    print(f"评估价格: {result['evaluation']['estimated_price']:,.0f} 元")
    print(f"单价: {result['evaluation']['price_per_sqm']:,.0f} 元/平米")

    # 演示2: 市场分析
    print("\n2. 市场分析")
    print("-" * 40)
    result = skill.execute(
        action="analyze_market",
        location="杭州市",
        property_type="residential"
    )
    print(f"市场状态: {result['analysis']['market_status']}")
    print(f"均价: {result['analysis']['avg_price']:,.0f} 元/平米")
    print(f"投资评分: {result['analysis']['investment_score']}/100")

    # 演示3: 投资计算
    print("\n3. 投资计算")
    print("-" * 40)
    result = skill.execute(
        action="calculate_investment",
        property_price=3500000,
        down_payment=700000,
        loan_term=30,
        interest_rate=4.5,
        rent_per_month=8000,
        annual_expenses=70000
    )
    print(f"月供: {result['investment']['monthly_payment']:,.0f} 元")
    print(f"月净收入: {result['investment']['net_monthly_income']:,.0f} 元")
    print(f"年化收益: {result['investment']['annual_return_rate']}")

    # 演示4: 房源推荐
    print("\n4. 房源推荐")
    print("-" * 40)
    result = skill.execute(
        action="recommend",
        budget=5000000,
        min_area=80,
        location="杭州市",
        bedrooms=2
    )
    print(f"找到 {result['total_found']} 套房源")
    for prop in result['recommendations'][:3]:
        print(f"  - {prop['name']}: {prop['price']:,.0f}元 ({prop['area']}平米)")

    # 演示5: 趋势分析
    print("\n5. 趋势分析")
    print("-" * 40)
    result = skill.execute(
        action="analyze_trend",
        property_type="residential",
        period="12m"
    )
    print(f"当前均价: {result['trend']['current_price']:,.0f} 元/平米")
    print(f"12个月变化: {result['trend']['change_12m']}%")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return skill


if __name__ == "__main__":
    main()
