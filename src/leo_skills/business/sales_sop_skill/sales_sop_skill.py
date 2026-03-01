# -*- coding: utf-8 -*-
"""
销售SOP数字化技能 - 核心模块
AI辅助房地产销售流程管理，提供执行指导和话术建议
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)

SKILL_DIR = Path(__file__).parent.resolve()
TEMPLATES_DIR = SKILL_DIR / "templates"
DATA_DIR = SKILL_DIR / "data"


# 销售阶段定义
class SalesStage:
    LEAD = "获客"
    FIRST_CONTACT = "首次接触"
    NEEDS_ANALYSIS = "需求分析"
    PROPERTY_MATCH = "房源匹配"
    VIEWING_ARRANGE = "带看安排"
    VIEWING_FEEDBACK = "带看反馈"
    NEGOTIATION = "价格谈判"
    OBJECTION = "异议处理"
    CLOSING = "成交签约"
    AFTER_SALES = "售后服务"
    REFERRAL = "转介绍"

    ALL_STAGES = [
        LEAD, FIRST_CONTACT, NEEDS_ANALYSIS, PROPERTY_MATCH,
        VIEWING_ARRANGE, VIEWING_FEEDBACK, NEGOTIATION,
        OBJECTION, CLOSING, AFTER_SALES, REFERRAL,
    ]


@dataclass
class FollowupAdvice:
    """跟进建议"""
    stage: str
    urgency: str  # high / medium / low
    action: str
    script: str
    next_stage: str
    deadline_days: int


# 跟进时效规则（天数）
FOLLOWUP_RULES: Dict[str, Dict[str, Any]] = {
    SalesStage.FIRST_CONTACT: {
        "max_gap_days": 1,
        "urgency_threshold": 2,
        "default_action": "发送项目资料+预约看房时间",
    },
    SalesStage.NEEDS_ANALYSIS: {
        "max_gap_days": 2,
        "urgency_threshold": 3,
        "default_action": "发送需求分析问卷，引导客户明确需求",
    },
    SalesStage.PROPERTY_MATCH: {
        "max_gap_days": 1,
        "urgency_threshold": 2,
        "default_action": "推送匹配房源TOP3，附带对比表",
    },
    SalesStage.VIEWING_ARRANGE: {
        "max_gap_days": 2,
        "urgency_threshold": 3,
        "default_action": "确认带看时间，发送带看准备清单",
    },
    SalesStage.VIEWING_FEEDBACK: {
        "max_gap_days": 1,
        "urgency_threshold": 1,
        "default_action": "收集带看反馈，趁热打铁推进",
    },
    SalesStage.NEGOTIATION: {
        "max_gap_days": 2,
        "urgency_threshold": 3,
        "default_action": "发送价格方案对比，推动决策",
    },
    SalesStage.OBJECTION: {
        "max_gap_days": 1,
        "urgency_threshold": 2,
        "default_action": "针对性解答异议，提供案例佐证",
    },
    SalesStage.CLOSING: {
        "max_gap_days": 1,
        "urgency_threshold": 1,
        "default_action": "确认签约细节，准备合同材料",
    },
    SalesStage.AFTER_SALES: {
        "max_gap_days": 7,
        "urgency_threshold": 14,
        "default_action": "满意度回访，引导好评和转介绍",
    },
}


# 常见异议话术库
OBJECTION_SCRIPTS: Dict[str, Dict[str, str]] = {
    "价格太贵": {
        "养老需求": (
            "张姐，我理解您的顾虑。不过您看，这套房子的单价虽然看起来高一点，"
            "但它的得房率有85%，实际使用面积比同价位的多出十几平。"
            "而且周边配套了社区医疗中心，以后养老不用跑远路，"
            "这些隐性价值算下来其实很划算的。"
        ),
        "投资需求": (
            "王总，从投资角度看，这个价格其实是价值洼地。"
            "周边在建的地铁线明年通车，参考其他城市的经验，"
            "地铁房通车后普遍有15-20%的涨幅空间。"
            "现在入手正好吃到这波红利。"
        ),
        "刚需自住": (
            "李哥，我完全理解预算的压力。不过这套房子首付只要XX万，"
            "月供大概XX元，和您现在的房租差不多。"
            "而且开发商现在有XX优惠政策，算下来能省好几万。"
            "我帮您算一笔详细的账？"
        ),
    },
    "位置太偏": {
        "养老需求": (
            "张姐，其实现在很多养老客户反而喜欢这种环境。"
            "空气好、安静，小区里就有健身步道和花园。"
            "而且社区班车每天定时往返市区，买菜看病都方便。"
            "很多业主住进来之后都说比市区舒服多了。"
        ),
        "default": (
            "这个位置现在看确实不算市中心，但您注意到没有，"
            "政府的规划已经把这里纳入了新城核心区。"
            "在建的商业综合体明年就开业了，到时候生活配套完全不用担心。"
            "买房买的是未来，现在的价格正好是红利期。"
        ),
    },
    "再考虑考虑": {
        "default": (
            "完全理解，买房是大事，确实需要慎重考虑。"
            "不过我想提醒您，这个户型目前只剩X套了，"
            "上周已经有两组客户在看。如果您比较中意的话，"
            "我建议可以先交个小定金锁定，考虑好了再签正式合同，"
            "这样不会错过心仪的房子。您觉得呢？"
        ),
    },
    "要和家人商量": {
        "default": (
            "当然，家人的意见很重要。要不这样，"
            "我把这套房子的详细资料整理一份给您，"
            "包括户型图、周边配套、价格明细，"
            "方便您和家人一起看。"
            "另外，周末我们有个业主开放日活动，"
            "可以带家人一起来实地感受一下，您看方便吗？"
        ),
    },
}


class SalesSOP:
    """房地产销售SOP数字化引擎"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.stages = SalesStage.ALL_STAGES
        self.followup_rules = FOLLOWUP_RULES
        self.objection_scripts = OBJECTION_SCRIPTS
        logger.info("SalesSOP 初始化完成")

    def get_followup_advice(
        self,
        customer_tags: List[str],
        last_contact_days: int,
        stage: str,
    ) -> FollowupAdvice:
        """根据客户状态生成跟进建议"""
        rule = self.followup_rules.get(stage, {})
        max_gap = rule.get("max_gap_days", 3)
        threshold = rule.get("urgency_threshold", 5)

        # 判断紧急程度
        if last_contact_days >= threshold:
            urgency = "high"
        elif last_contact_days >= max_gap:
            urgency = "medium"
        else:
            urgency = "low"

        action = rule.get("default_action", "常规跟进")
        script = self._generate_followup_script(customer_tags, stage, urgency)
        next_stage = self._get_next_stage(stage)

        return FollowupAdvice(
            stage=stage,
            urgency=urgency,
            action=action,
            script=script,
            next_stage=next_stage,
            deadline_days=max_gap,
        )

    def generate_viewing_checklist(
        self,
        customer_needs: Dict[str, str],
        properties: List[str],
    ) -> Dict[str, Any]:
        """生成带看准备清单"""
        checklist = {
            "客户需求摘要": customer_needs,
            "带看房源": properties,
            "准备事项": [
                "确认客户到访时间和交通方式",
                "提前踩点确认房源现场状态",
                "准备户型图和价格表纸质版",
                "准备周边配套地图（学校/医院/商超）",
                "准备竞品对比表",
                "检查样板间/现房开放状态",
            ],
            "话术要点": [],
            "注意事项": [],
        }

        # 根据客户需求定制话术要点
        purpose = customer_needs.get("purpose", "")
        if "养老" in purpose:
            checklist["话术要点"].extend([
                "重点介绍社区医疗和健身配套",
                "强调低密度、绿化率、空气质量",
                "提及邻里社交活动和物业服务",
            ])
            checklist["注意事项"].append("带看节奏放慢，多留时间感受环境")
        elif "投资" in purpose:
            checklist["话术要点"].extend([
                "重点介绍区域规划和升值潜力",
                "准备租金回报率数据",
                "提及周边在建配套和交通规划",
            ])
        elif "自住" in purpose or "刚需" in purpose:
            checklist["话术要点"].extend([
                "重点介绍户型实用性和得房率",
                "准备月供计算和优惠政策",
                "强调学区和通勤便利性",
            ])

        budget = customer_needs.get("budget", "")
        if budget:
            checklist["注意事项"].append(f"客户预算: {budget}，注意价格引导节奏")

        return checklist

    def handle_objection(
        self,
        objection: str,
        customer_type: str = "default",
        property_name: str = "",
    ) -> Dict[str, str]:
        """获取异议处理话术"""
        # 模糊匹配异议关键词
        matched_key = None
        for key in self.objection_scripts:
            if key in objection or objection in key:
                matched_key = key
                break

        if not matched_key:
            return {
                "objection": objection,
                "strategy": "倾听+共情+转化",
                "script": (
                    "我完全理解您的想法。很多客户一开始也有类似的顾虑，"
                    "但了解之后都觉得这个项目确实不错。"
                    "要不我针对您关心的点，详细给您分析一下？"
                ),
                "tip": "先认同客户感受，再用事实和案例引导",
            }

        scripts = self.objection_scripts[matched_key]
        script = scripts.get(customer_type, scripts.get("default", ""))

        return {
            "objection": objection,
            "matched_type": matched_key,
            "customer_type": customer_type,
            "script": script,
            "tip": "话术仅供参考，请根据现场情况灵活调整",
        }

    def get_stage_sop(self, stage: str) -> Dict[str, Any]:
        """获取指定阶段的SOP详情"""
        sop_details = {
            SalesStage.FIRST_CONTACT: {
                "目标": "建立信任，了解基本需求",
                "AI辅助": "生成破冰话术，分析客户背景",
                "执行步骤": [
                    "24小时内首次联系",
                    "自我介绍+公司介绍（30秒版）",
                    "了解客户基本需求（预算/面积/区域）",
                    "添加微信，发送电子名片",
                    "发送项目资料包",
                ],
                "完成标志": "客户回复确认收到资料",
            },
            SalesStage.NEEDS_ANALYSIS: {
                "目标": "深度挖掘需求，建立客户画像",
                "AI辅助": "生成需求分析问卷，输出客户画像报告",
                "执行步骤": [
                    "引导客户填写需求问卷",
                    "分析购房动机（自住/投资/养老）",
                    "确认核心需求和次要需求",
                    "了解决策链（谁说了算）",
                    "评估购买力和时间节点",
                ],
                "完成标志": "输出完整客户画像",
            },
            SalesStage.VIEWING_ARRANGE: {
                "目标": "高效带看，促进意向",
                "AI辅助": "生成带看路线和话术要点",
                "执行步骤": [
                    "根据需求匹配2-3套房源",
                    "规划带看路线（先差后好）",
                    "提前确认房源现场状态",
                    "准备对比表和计算器",
                    "现场重点展示匹配需求的亮点",
                ],
                "完成标志": "客户表达明确意向或反馈",
            },
        }
        return sop_details.get(stage, {"提示": f"阶段 '{stage}' 的SOP正在完善中"})

    def generate_sales_funnel(
        self, customers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """生成销售漏斗报告"""
        funnel = {stage: [] for stage in self.stages}
        for c in customers:
            stage = c.get("stage", SalesStage.LEAD)
            if stage in funnel:
                funnel[stage].append(c.get("name", "未知"))

        total = len(customers)
        report = {
            "total_customers": total,
            "funnel": {},
            "conversion_suggestions": [],
        }
        for stage in self.stages:
            count = len(funnel[stage])
            report["funnel"][stage] = {
                "count": count,
                "ratio": f"{count/total*100:.1f}%" if total > 0 else "0%",
                "names": funnel[stage],
            }

        return report

    # --- 内部方法 ---

    def _generate_followup_script(
        self, tags: List[str], stage: str, urgency: str
    ) -> str:
        """根据标签和阶段生成跟进话术"""
        tag_str = "、".join(tags[:3]) if tags else "普通客户"

        if urgency == "high":
            prefix = "⚠️ 紧急跟进 - "
            tone = "建议立即联系，避免客户流失"
        elif urgency == "medium":
            prefix = "📋 常规跟进 - "
            tone = "按计划推进，保持节奏"
        else:
            prefix = "✅ 正常节奏 - "
            tone = "客户状态良好，持续维护"

        return f"{prefix}客户标签: {tag_str} | 当前阶段: {stage} | {tone}"

    def _get_next_stage(self, current: str) -> str:
        """获取下一个销售阶段"""
        try:
            idx = self.stages.index(current)
            if idx < len(self.stages) - 1:
                return self.stages[idx + 1]
        except ValueError:
            pass
        return current
