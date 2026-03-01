# -*- coding: utf-8 -*-
"""
客户画像AI分析技能 - 核心模块
基于多维数据构建精准客户画像
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Portrait:
    """客户画像数据模型"""
    name: str
    # 基础属性
    age_range: str = ""
    occupation: str = ""
    family_structure: str = ""
    income_level: str = ""
    # 购房动机
    purchase_motive: str = ""
    budget_range: str = ""
    preferred_area: str = ""
    preferred_type: str = ""
    # 决策特征
    decision_maker: str = ""
    decision_cycle: str = ""
    key_concerns: List[str] = field(default_factory=list)
    # 行为特征
    active_hours: str = ""
    preferred_contact: str = ""
    response_speed: str = ""
    # 风险评估
    churn_risk: str = "medium"
    close_probability: float = 0.0
    budget_match: str = ""
    # 标签
    tags: List[str] = field(default_factory=list)
    # 元数据
    created_at: str = ""
    updated_at: str = ""


# 购房动机推断规则
MOTIVE_RULES = {
    "养老": {"keywords": ["养老", "退休", "安静", "医疗", "低楼层", "电梯"], "weight": 1.0},
    "投资": {"keywords": ["投资", "回报", "升值", "出租", "租金"], "weight": 1.0},
    "自住": {"keywords": ["自住", "结婚", "刚需", "首套", "通勤"], "weight": 1.0},
    "改善": {"keywords": ["改善", "换房", "大户型", "品质", "学区"], "weight": 1.0},
    "学区": {"keywords": ["学区", "学校", "教育", "孩子上学"], "weight": 1.0},
}

# 流失风险评估规则
CHURN_RULES = {
    "high": {"no_contact_days": 14, "no_viewing": True},
    "medium": {"no_contact_days": 7, "no_viewing": False},
    "low": {"no_contact_days": 3, "no_viewing": False},
}


class CustomerPortrait:
    """客户画像分析引擎"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        logger.info("CustomerPortrait 初始化完成")

    def analyze(
        self,
        name: str,
        interactions: Optional[List[Dict[str, Any]]] = None,
        tags: Optional[List[str]] = None,
        crm_data: Optional[Dict[str, Any]] = None,
    ) -> Portrait:
        """分析客户数据，生成画像"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        interactions = interactions or []
        tags = tags or []

        portrait = Portrait(
            name=name,
            tags=list(tags),
            created_at=now,
            updated_at=now,
        )

        # 从CRM数据填充基础属性
        if crm_data:
            portrait.age_range = crm_data.get("age_range", "")
            portrait.occupation = crm_data.get("occupation", "")
            portrait.family_structure = crm_data.get("family", "")
            portrait.income_level = crm_data.get("income", "")
            portrait.budget_range = crm_data.get("budget", "")
            portrait.preferred_area = crm_data.get("area", "")
            portrait.preferred_type = crm_data.get("type", "")

        # 从标签和交互推断购房动机
        portrait.purchase_motive = self._infer_motive(tags, interactions)

        # 从交互记录分析行为特征
        if interactions:
            portrait.active_hours = self._analyze_active_hours(interactions)
            portrait.preferred_contact = self._analyze_contact_preference(interactions)
            portrait.response_speed = self._analyze_response_speed(interactions)

        # 提取关注点
        portrait.key_concerns = self._extract_concerns(tags, interactions)

        # 评估风险和成交概率
        portrait.churn_risk = self._assess_churn_risk(interactions)
        portrait.close_probability = self._estimate_close_probability(portrait)

        return portrait

    def get_strategy(self, portrait: Portrait) -> Dict[str, Any]:
        """根据画像生成跟进策略"""
        strategy = {
            "customer": portrait.name,
            "motive": portrait.purchase_motive,
            "risk_level": portrait.churn_risk,
            "close_probability": f"{portrait.close_probability:.0%}",
            "recommendations": [],
            "communication_tips": [],
            "next_actions": [],
        }

        # 根据动机定制策略
        motive = portrait.purchase_motive
        if "养老" in motive:
            strategy["recommendations"].extend([
                "重点推荐低密度、环境好的社区",
                "强调医疗配套和物业服务",
                "安排周末实地体验活动",
            ])
            strategy["communication_tips"].append("沟通节奏放慢，多倾听，建立信任")
        elif "投资" in motive:
            strategy["recommendations"].extend([
                "准备区域规划和升值数据",
                "提供租金回报率分析",
                "对比周边竞品价格走势",
            ])
            strategy["communication_tips"].append("用数据说话，突出投资回报")
        elif "学区" in motive:
            strategy["recommendations"].extend([
                "整理对口学校信息和入学政策",
                "准备学区划分地图",
                "收集在读家长评价",
            ])

        # 根据风险等级调整
        if portrait.churn_risk == "high":
            strategy["next_actions"].insert(0, "⚠️ 立即联系，客户有流失风险")
        elif portrait.churn_risk == "medium":
            strategy["next_actions"].append("本周内安排一次深度沟通")

        # 根据沟通偏好
        if portrait.preferred_contact:
            strategy["communication_tips"].append(
                f"客户偏好 {portrait.preferred_contact} 沟通"
            )
        if portrait.active_hours:
            strategy["communication_tips"].append(
                f"建议在 {portrait.active_hours} 联系"
            )

        return strategy

    # --- 内部分析方法 ---

    def _infer_motive(
        self, tags: List[str], interactions: List[Dict[str, Any]]
    ) -> str:
        """从标签和交互推断购房动机"""
        scores: Dict[str, float] = {}
        all_text = " ".join(tags)
        for i in interactions:
            all_text += " " + i.get("content", "")

        for motive, rule in MOTIVE_RULES.items():
            score = sum(1 for kw in rule["keywords"] if kw in all_text)
            if score > 0:
                scores[motive] = score * rule["weight"]

        if not scores:
            return "待确认"
        return max(scores, key=scores.get)

    def _analyze_active_hours(self, interactions: List[Dict[str, Any]]) -> str:
        """分析客户活跃时段"""
        hours = []
        for i in interactions:
            time_str = i.get("time", "")
            if time_str:
                try:
                    h = int(time_str.split(":")[0].split(" ")[-1])
                    hours.append(h)
                except (ValueError, IndexError):
                    pass
        if not hours:
            return ""
        avg = sum(hours) / len(hours)
        if avg < 12:
            return "上午"
        elif avg < 18:
            return "下午"
        return "晚上"

    def _analyze_contact_preference(self, interactions: List[Dict[str, Any]]) -> str:
        """分析偏好沟通方式"""
        methods: Dict[str, int] = {}
        for i in interactions:
            m = i.get("method", "")
            if m:
                methods[m] = methods.get(m, 0) + 1
        if not methods:
            return ""
        return max(methods, key=methods.get)

    def _analyze_response_speed(self, interactions: List[Dict[str, Any]]) -> str:
        """分析响应速度"""
        # 简化实现：基于交互频率判断
        if len(interactions) >= 10:
            return "快"
        elif len(interactions) >= 5:
            return "中等"
        return "慢"

    def _extract_concerns(
        self, tags: List[str], interactions: List[Dict[str, Any]]
    ) -> List[str]:
        """提取客户关注点"""
        concern_keywords = {
            "价格": ["价格", "预算", "首付", "月供", "贵"],
            "位置": ["位置", "地段", "交通", "通勤", "偏"],
            "学区": ["学区", "学校", "教育"],
            "配套": ["配套", "商场", "医院", "超市"],
            "户型": ["户型", "面积", "朝向", "楼层"],
            "品质": ["品质", "装修", "物业", "开发商"],
        }
        all_text = " ".join(tags)
        for i in interactions:
            all_text += " " + i.get("content", "")

        concerns = []
        for concern, keywords in concern_keywords.items():
            if any(kw in all_text for kw in keywords):
                concerns.append(concern)
        return concerns

    def _assess_churn_risk(self, interactions: List[Dict[str, Any]]) -> str:
        """评估流失风险"""
        if not interactions:
            return "high"
        # 简化：基于最近交互时间
        last = interactions[-1]
        last_date = last.get("date", "")
        if not last_date:
            return "medium"
        try:
            days = (datetime.now() - datetime.strptime(last_date, "%Y-%m-%d")).days
        except ValueError:
            return "medium"

        if days >= 14:
            return "high"
        elif days >= 7:
            return "medium"
        return "low"

    def _estimate_close_probability(self, portrait: Portrait) -> float:
        """估算成交概率"""
        score = 0.3  # 基础分
        if portrait.purchase_motive and portrait.purchase_motive != "待确认":
            score += 0.15
        if portrait.budget_range:
            score += 0.1
        if portrait.preferred_area:
            score += 0.1
        if portrait.churn_risk == "low":
            score += 0.15
        elif portrait.churn_risk == "high":
            score -= 0.1
        if len(portrait.key_concerns) <= 2:
            score += 0.1
        return min(max(score, 0.05), 0.95)
