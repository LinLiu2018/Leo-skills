#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Dispatcher Skill - 智能技能分发器

自动识别用户需求，匹配最佳技能/代理/工作流，供用户确认后执行。
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


# ==================== 关键词词库 ====================

KEYWORD_DICT = {
    # ==================== 房产业务 ====================
    "villa": ["别墅", "Villa", "独栋", "别墅区"],
    "residential": ["住宅", "购房", "买房", "新房", "刚需"],
    "commercial": ["商业", "写字楼", "商铺", "办公", "商办"],
    "auction": ["法拍", "拍卖", "拍房", "法拍房"],
    "leasing": ["租赁", "租房", "出租", "招商", "招租"],
    "property": ["房产", "楼盘", "房源", "地产"],
    "valuation": ["估值", "评估", "价格", "报价"],
    "tenant": ["租客", "租户", "房客"],

    # ==================== 金融业务 ====================
    "loan": ["贷款", "借贷", "融资", "信用贷"],
    "mortgage": ["房贷", "按揭", "房贷计算", "月供"],
    "investment": ["投资", "理财", "资产配置"],
    "credit": ["信用", "征信", "信用分"],
    "bank": ["银行", "产品", "银行贷款"],
    "interest": ["利率", "利息", "费率"],
    "repayment": ["还款", "提前还款"],

    # ==================== 电商业务 ====================
    "ecommerce": ["电商", "跨境电商", "跨境"],
    "amazon": ["亚马逊", "Amazon", "亚马逊运营"],
    "shopify": ["Shopify", "独立站", "Shopify运营"],
    "aliexpress": ["速卖通", "AliExpress"],
    "ebay": ["eBay", "Ebay", "eBay运营"],
    "product_selection": ["选品", "产品选择"],
    "inventory": ["库存", "仓储"],
    "shipping": ["物流", "发货", "跨境物流"],
    "customs": ["报关", "海关", "清关"],

    # ==================== 内容创作 ====================
    "article": ["文章", "写作", "写文章", "软文"],
    "copywriting": ["文案", "推广文案", "营销文案"],
    "content": ["内容", "创作", "内容创作"],
    "video": ["视频", "剪辑", "短视频", "口播"],
    "seo": ["SEO", "优化", "搜索优化", "排名"],
    "social": ["社交媒体", "抖音", "小红书", "视频号", "快手"],
    "thumbnail": ["封面", "缩略图", "封面图"],
    "publish": ["发布", "分发", "分发到"],
    "blog": ["博客", "自媒体"],

    # ==================== 开发工具 ====================
    "code": ["代码", "开发", "编程", "写代码"],
    "api": ["API", "接口", "后端", "REST"],
    "frontend": ["前端", "Vue", "React", "UI"],
    "miniprogram": ["小程序", "微信小程序", "uniapp"],
    "database": ["数据库", "DB", "SQL"],
    "docker": ["Docker", "容器", "镜像"],
    "test": ["测试", "单元测试", "E2E", "测试用例"],
    "architecture": ["架构", "系统设计", "技术选型"],
    "deployment": ["部署", "上线", "发布"],

    # ==================== 营销销售 ====================
    "marketing": ["营销", "推广", "获客"],
    "sales": ["销售", "成交", "转化"],
    "customer": ["客户", "客源", "客户资源"],
    "ads": ["广告", "投放", "推广费"],
    "facebook_ads": ["Facebook广告", "FB广告"],
    "google_ads": ["Google广告", "谷歌广告"],

    # ==================== 分析研究 ====================
    "research": ["研究", "调研", "调查", "研究一下"],
    "analysis": ["分析", "数据分析", "市场分析", "分析报告"],
    "monitor": ["监控", "监测", "追踪", "关注一下"],
    "report": ["报告", "周报", "日报", "报表"],
    "competitor": ["竞品", "竞争对手", "同行"],

    # ==================== 工具类 ====================
    "translate": ["翻译", "多语言", "英文翻译"],
    "weather": ["天气", "天气预报"],
    "schedule": ["日程", "日历", "预约", "会议"],
    "email": ["邮件", "邮箱", "发邮件"],
    "pdf": ["PDF", "文档", "分析PDF"],
    "excel": ["Excel", "表格", "Excel表格"],
    "ppt": ["PPT", "演示", "幻灯片", "做PPT"],
    "document": ["文档", "手册", "说明书"],
    "contract": ["合同", "协议", "模板"],

    # ==================== 智能硬件 ====================
    "smart_glasses": ["智能眼镜", "AI眼镜", "AR眼镜", "智能穿戴"],
    "wearable": ["智能穿戴", "穿戴设备"],
}


# ==================== 技能/代理映射 ====================

ENTITY_MAPPING = {
    # 房产业务
    "villa_agent": {"keywords": ["villa", "别墅"], "type": "agent", "desc": "别墅项目专家"},
    "residential_agent": {"keywords": ["residential", "住宅"], "type": "agent", "desc": "住宅项目专家"},
    "commercial_agent": {"keywords": ["commercial", "商业"], "type": "agent", "desc": "商业地产专家"},
    "auction_agent": {"keywords": ["auction", "法拍"], "type": "agent", "desc": "法拍房专家"},
    "leasing_agent": {"keywords": ["leasing", "租赁"], "type": "agent", "desc": "租赁管理专家"},
    "realestate_agent": {"keywords": ["property", "房产"], "type": "agent", "desc": "房地产市场分析"},

    # 金融业务
    "loan_agent": {"keywords": ["loan", "贷款"], "type": "agent", "desc": "贷款产品专家"},
    "bank_product_agent": {"keywords": ["bank", "银行"], "type": "agent", "desc": "银行产品专家"},
    "investment_agent": {"keywords": ["investment", "投资"], "type": "agent", "desc": "投资分析专家"},
    "mortgage_calculator_skill": {"keywords": ["mortgage", "房贷"], "type": "skill", "desc": "房贷计算"},
    "loan_calculator_skill": {"keywords": ["loan", "贷款"], "type": "skill", "desc": "贷款计算"},

    # 电商业务
    "ecommerce_agent": {"keywords": ["ecommerce", "电商"], "type": "agent", "desc": "AI电商运营专家"},
    "amazon_skill": {"keywords": ["amazon", "亚马逊"], "type": "skill", "desc": "亚马逊运营"},
    "shopify_skill": {"keywords": ["shopify"], "type": "skill", "desc": "Shopify独立站"},
    "aliexpress_skill": {"keywords": ["aliexpress", "速卖通"], "type": "skill", "desc": "速卖通运营"},

    # 内容创作
    "copywriting_skill": {"keywords": ["copywriting", "文案"], "type": "skill", "desc": "文案生成"},
    "article_generator_skill": {"keywords": ["article", "文章"], "type": "skill", "desc": "文章生成"},
    "content_generator_skill": {"keywords": ["content", "内容"], "type": "skill", "desc": "内容生成"},
    "content_layout_leo_skill": {"keywords": ["content", "排版"], "type": "skill", "desc": "多平台内容排版"},
    "social_auto_publish_skill": {"keywords": ["social", "抖音", "小红书"], "type": "skill", "desc": "多平台发布"},
    "video_skill": {"keywords": ["video", "视频"], "type": "skill", "desc": "视频处理"},
    "seo_skill": {"keywords": ["seo"], "type": "skill", "desc": "SEO优化"},

    # 开发工具
    "architect_agent": {"keywords": ["code", "架构"], "type": "agent", "desc": "技术架构专家"},
    "mobile_agent": {"keywords": ["miniprogram", "小程序"], "type": "agent", "desc": "移动开发专家"},
    "react_component_generator_skill": {"keywords": ["react", "前端"], "type": "skill", "desc": "React组件生成"},
    "vue_component_generator_skill": {"keywords": ["vue", "前端"], "type": "skill", "desc": "Vue组件生成"},
    "flask_api_generator_skill": {"keywords": ["api", "后端", "flask"], "type": "skill", "desc": "Flask API生成"},
    "fastapi_endpoint_generator_skill": {"keywords": ["api", "后端", "fastapi"], "type": "skill", "desc": "FastAPI生成"},
    "dockerfile_generator_skill": {"keywords": ["docker", "容器"], "type": "skill", "desc": "Docker配置生成"},
    "unit_test_generator_skill": {"keywords": ["test", "测试"], "type": "skill", "desc": "单元测试生成"},

    # 分析研究
    "research_agent": {"keywords": ["research", "研究"], "type": "agent", "desc": "研究调研专家"},
    "analysis_agent": {"keywords": ["analysis", "分析"], "type": "agent", "desc": "数据分析专家"},
    "market_analysis_skill": {"keywords": ["analysis", "市场", "分析"], "type": "skill", "desc": "市场分析"},
    "data_analyzer_skill": {"keywords": ["analysis", "数据"], "type": "skill", "desc": "数据分析"},
    "research_assistant_skill": {"keywords": ["research", "调研"], "type": "skill", "desc": "研究助手"},

    # 监控
    "video_monitor_skill": {"keywords": ["video", "抖音", "视频号"], "type": "skill", "desc": "视频号监控"},
    "twitter_monitor_skill": {"keywords": ["twitter", "X平台"], "type": "skill", "desc": "Twitter监控"},
    "social_media_monitor_skill": {"keywords": ["social", "监控", "小红书"], "type": "skill", "desc": "多平台监控"},

    # 工具类
    "translate_skill": {"keywords": ["translate", "翻译"], "type": "skill", "desc": "多语言翻译"},
    "weather_skill_skill": {"keywords": ["weather", "天气"], "type": "skill", "desc": "天气查询"},
    "pdf_analyzer_skill": {"keywords": ["pdf"], "type": "skill", "desc": "PDF分析"},
    "pdf_generator_skill": {"keywords": ["pdf"], "type": "skill", "desc": "PDF生成"},
    "excel_skill": {"keywords": ["excel", "表格"], "type": "skill", "desc": "Excel处理"},
    "powerpoint_skill": {"keywords": ["ppt", "演示"], "type": "skill", "desc": "PPT生成"},
    "obsidian_sync_skill": {"keywords": ["obsidian", "笔记"], "type": "skill", "desc": "Obsidian同步"},
    "web_search_skill": {"keywords": ["搜索", "查找"], "type": "skill", "desc": "网络搜索"},
    "summarize_skill": {"keywords": ["总结", "摘要"], "type": "skill", "desc": "内容总结"},
    "contract_generator_skill": {"keywords": ["contract", "合同"], "type": "skill", "desc": "合同生成"},
    "doc_generator_skill": {"keywords": ["document", "文档"], "type": "skill", "desc": "文档生成"},

    # 营销销售
    "marketing_agent": {"keywords": ["marketing", "营销"], "type": "agent", "desc": "营销策划专家"},
    "sales_agent": {"keywords": ["sales", "销售"], "type": "agent", "desc": "销售管理专家"},
    "ads_manager_skill": {"keywords": ["ads", "投放"], "type": "skill", "desc": "广告投放管理"},
    "facebook_ads_skill": {"keywords": ["facebook_ads", "Facebook"], "type": "skill", "desc": "Facebook广告"},
    "google_ads_skill": {"keywords": ["google_ads", "Google"], "type": "skill", "desc": "Google广告"},
    "competitor_monitor_skill": {"keywords": ["competitor", "竞品"], "type": "skill", "desc": "竞品监控"},
    "price_monitor_skill": {"keywords": ["price", "价格"], "type": "skill", "desc": "价格监控"},

    # 客户服务
    "support_agent": {"keywords": ["support", "客服"], "type": "agent", "desc": "客户支持专家"},
    "service_agent": {"keywords": ["service", "服务"], "type": "agent", "desc": "服务管理专家"},
    "pocket-crm": {"keywords": ["crm", "口袋助理"], "type": "skill", "desc": "口袋助理CRM"},
    "customer-portrait": {"keywords": ["customer", "客户画像"], "type": "skill", "desc": "客户画像分析"},

    # 智能硬件
    "ecommerce_agent": {"keywords": ["smart_glasses", "智能眼镜"], "type": "agent", "desc": "AI智能硬件电商"},
}


@dataclass
class MatchResult:
    """匹配结果"""
    name: str
    entity_type: str  # agent, skill
    score: int
    description: str
    keywords: List[str] = field(default_factory=list)


class AutoDispatcher:
    """智能技能分发器"""

    def __init__(self):
        self.keyword_dict = KEYWORD_DICT
        self.entity_mapping = ENTITY_MAPPING

    def extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 清理文本
        text = text.lower().strip()

        # 提取所有匹配的关键词类别
        matched_keywords = []

        for category, keywords in self.keyword_dict.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    matched_keywords.append(category)

        # 去重
        return list(set(matched_keywords))

    def match_entities(self, keywords: List[str], text: str) -> List[MatchResult]:
        """匹配实体（技能/代理）"""
        results = []

        for name, info in self.entity_mapping.items():
            score = 0
            matched_keywords = []

            # 检查关键词匹配
            for kw in keywords:
                if kw in info["keywords"]:
                    score += 100
                    matched_keywords.append(kw)

            # 检查文本直接匹配
            text_lower = text.lower()
            for keyword in info["keywords"]:
                if keyword.lower() in text_lower:
                    score += 50
                    if keyword not in matched_keywords:
                        matched_keywords.append(keyword)

            # 计算描述匹配
            if info["desc"] in text_lower:
                score += 30

            if score > 0:
                results.append(MatchResult(
                    name=name,
                    entity_type=info["type"],
                    score=score,
                    description=info["desc"],
                    keywords=matched_keywords
                ))

        # 按分数排序
        results.sort(key=lambda x: x.score, reverse=True)

        # 只返回前5个
        return results[:5]

    def format_candidates(self, text: str, results: List[MatchResult]) -> str:
        """格式化候选列表"""
        if not results:
            return f"❓ 未找到匹配的能力\n\n输入: {text}\n\n请尝试其他关键词，或直接说出你想要做什么。"

        # 提取的关键词
        keywords = self.extract_keywords(text)

        output = []
        output.append("## 🎯 识别结果")
        output.append("")
        output.append(f"**提取关键词**: {', '.join(keywords) if keywords else '无'}")
        output.append("")
        output.append("### 匹配的能力")

        # 按类型分组
        agents = [r for r in results if r.entity_type == "agent"]
        skills = [r for r in results if r.entity_type == "skill"]

        output.append("")
        output.append("| # | 名称 | 类型 | 匹配度 | 说明 |")
        output.append("|---|------|------|--------|------|")

        for i, r in enumerate(results, 1):
            stars = "⭐" * min(r.score // 30, 3)
            type_icon = "🤖" if r.entity_type == "agent" else "⚡"
            output.append(f"| {i} | **{r.name}** | {type_icon} {r.entity_type} | {stars} | {r.description} |")

        output.append("")
        output.append("---")
        output.append("")
        output.append("### 📝 请确认")
        output.append("")
        output.append("请回复：")
        output.append("- 数字 (如 `1`) - 执行单个")
        output.append("- `全部` - 执行全部")
        output.append("- `取消` - 取消操作")
        output.append("")

        return "\n".join(output)

    def dispatch(self, user_input: str) -> str:
        """执行分发"""
        # 1. 提取关键词
        keywords = self.extract_keywords(user_input)

        # 2. 匹配实体
        results = self.match_entities(keywords, user_input)

        # 3. 格式化输出
        return self.format_candidates(user_input, results)


def execute(user_input: str) -> str:
    """
    技能执行入口 - 识别匹配

    Args:
        user_input: 用户输入的文本

    Returns:
        格式化后的候选列表
    """
    dispatcher = AutoDispatcher()
    return dispatcher.dispatch(user_input)


def execute_skill(skill_name: str, params: dict = None) -> str:
    """
    执行指定的技能或代理

    Args:
        skill_name: 技能/代理名称
        params: 执行参数

    Returns:
        执行结果
    """
    params = params or {}

    # 技能执行映射表
    SKILL_EXECUTORS = {
        # 房贷计算
        "mortgage_calculator_skill": lambda: f"🏠 房贷计算器已启动\n\n请提供以下信息：\n- 房屋总价\n- 贷款金额\n- 贷款年限\n- 利率（可选，默认4.1%）",
        "loan_calculator_skill": lambda: f"💰 贷款计算器已启动\n\n请提供以下信息：\n- 贷款金额\n- 贷款期限\n- 年利率\n- 还款方式（等额本息/等额本金）",

        # 文章生成
        "article_generator_skill": lambda: f"📝 文章生成器已启动\n\n请提供：\n- 主题\n- 字数要求\n- 风格（专业/通俗/营销）",
        "copywriting_skill": lambda: f"✍️ 文案生成器已启动\n\n请提供：\n- 产品/服务名称\n- 目标用户\n- 文案风格",

        # 市场分析
        "market_analysis_skill": lambda: f"📊 市场分析已启动\n\n请提供：\n- 分析目标（区域/产品/竞品）\n- 时间范围\n- 数据来源偏好",

        # 合同生成
        "contract_generator_skill": lambda: f"📄 合同生成器已启动\n\n请提供：\n- 合同类型（租赁/购房/服务）\n- 当事人信息\n- 主要条款",

        # 视频监控
        "video_monitor_skill": lambda: f"📹 视频号监控已启动\n\n请提供：\n- 监控的账号\n- 监控频率（每日/每周）\n- 数据维度（粉丝/播放/互动）",

        # 电商
        "amazon_skill": lambda: f"🛒 亚马逊运营助手已启动\n\n请选择功能：\n1. 选品分析\n2. Listing优化\n3. 广告投放\n4. 竞品监控",
        "shopify_skill": lambda: f"🛍️ Shopify运营助手已启动\n\n请选择功能：\n1. 店铺装修\n2. 产品上架\n3. 物流设置",

        # API生成
        "flask_api_generator_skill": lambda: f"⚡ Flask API生成器已启动\n\n请提供：\n- API端点名称\n- 请求方法（GET/POST）\n- 参数定义",
        "fastapi_endpoint_generator_skill": lambda: f"⚡ FastAPI生成器已启动\n\n请提供：\n- 端点路径\n- 请求/响应模型\n- 认证方式",

        # PDF/PPT
        "pdf_generator_skill": lambda: f"📄 PDF生成器已启动\n\n请提供：\n- 文档标题\n- 内容大纲\n- 样式偏好",
        "powerpoint_skill": lambda: f"📊 PPT生成器已启动\n\n请提供：\n- 演示主题\n- 页面数量\n- 风格",

        # 搜索
        "web_search_skill": lambda: f"🔍 网络搜索已启动\n\n请提供搜索关键词：",
        "research_assistant_skill": lambda: f"📚 研究助手已启动\n\n请提供：\n- 研究主题\n- 深度要求\n- 参考文献数量",

        # 翻译
        "translate_skill": lambda: f"🌐 翻译助手已启动\n\n请提供：\n- 原文内容\n- 目标语言\n- 翻译风格（直译/意译）",
    }

    # 代理执行映射表
    AGENT_EXECUTORS = {
        "villa_agent": lambda: f"🏡 别墅项目专家已启动\n\n请问您想了解：\n1. 宁波别墅市场分析\n2. 别墅推荐\n3. 投资建议",
        "residential_agent": lambda: f"🏠 住宅专家已启动\n\n请问您想了解：\n1. 新房推荐\n2. 购房政策\n3. 贷款方案",
        "commercial_agent": lambda: f"🏢 商业地产专家已启动\n\n请问您想了解：\n1. 写字楼出租\n2. 商铺投资\n3. 商办市场",
        "auction_agent": lambda: f"🔨 法拍房专家已启动\n\n请问您想了解：\n1. 法拍房源\n2. 拍卖流程\n3. 风险评估",
        "leasing_agent": lambda: f"🔑 租赁管理专家已启动\n\n请问您想了解：\n1. 出租房源\n2. 租客筛选\n3. 合同管理",
        "loan_agent": lambda: f"💳 贷款产品专家已启动\n\n请问您想了解：\n1. 房贷产品\n2. 信用贷款\n3. 利率比较",
        "ecommerce_agent": lambda: f"🛒 电商运营专家已启动\n\n请问您想了解：\n1. 亚马逊运营\n2. Shopify建站\n3. 智能硬件选品",
        "marketing_agent": lambda: f"📢 营销策划专家已启动\n\n请问您想了解：\n1. 营销方案\n2. 广告投放\n3. 内容营销",
        "sales_agent": lambda: f"💼 销售管理专家已启动\n\n请问您想了解：\n1. 销售策略\n2. 客户管理\n3. 转化优化",
        "research_agent": lambda: f"🔬 研究调研专家已启动\n\n请提供研究主题：",
        "analysis_agent": lambda: f"📊 数据分析专家已启动\n\n请提供：\n- 数据来源\n- 分析目标\n- 可视化需求",
        "architect_agent": lambda: f"🏗️ 技术架构专家已启动\n\n请提供：\n- 项目类型\n- 技术栈偏好\n- 性能要求",
    }

    # 检查是否是技能
    if skill_name in SKILL_EXECUTORS:
        executor = SKILL_EXECUTORS[skill_name]
        return executor()

    # 检查是否是代理
    if skill_name in AGENT_EXECUTORS:
        executor = AGENT_EXECUTORS[skill_name]
        return executor()

    # 未找到执行器
    return f"⚠️ {skill_name} 已选中，但执行器尚未配置。\n\n当前仅支持：\n- 房贷计算\n- 文章/文案生成\n- 市场分析\n- 合同生成\n- 视频监控\n- 电商运营\n- API生成\n- PPT/PDF生成\n- 翻译\n- 各类代理问答"


def confirm_and_execute(user_response: str, last_results: List[MatchResult]) -> str:
    """
    解析用户确认并执行

    Args:
        user_response: 用户回复（数字/全部/取消）
        last_results: 上次的匹配结果

    Returns:
        执行结果
    """
    user_response = user_response.strip().lower()

    # 取消
    if user_response in ["取消", "cancel", "no", "q"]:
        return "✅ 已取消操作。有什么其他需要帮助的吗？"

    # 执行全部
    if user_response in ["全部", "all", "execute all"]:
        results = last_results
        if not results:
            return "⚠️ 没有可执行的项目。"
        output = ["## 🚀 执行全部\n"]
        for r in results:
            output.append(f"\n### {r.name}")
            output.append(execute_skill(r.name))
        return "\n".join(output)

    # 数字选择
    try:
        index = int(user_response) - 1
        if 0 <= index < len(last_results):
            selected = last_results[index]
            return f"## 🚀 执行: {selected.name}\n\n{execute_skill(selected.name)}"
        else:
            return f"⚠️ 无效的选择，请输入 1-{len(last_results)} 之间的数字。"
    except ValueError:
        return "⚠️ 无法识别您的回复，请输入数字（如 1）、'全部' 或 '取消'。"


# ==================== 测试 ====================

if __name__ == "__main__":
    # 测试用例
    test_cases = [
        "帮我分析一下宁波别墅市场",
        "写一篇关于房贷计算的文章",
        "监控一下抖音账号数据",
        "创建一个Python API",
        "我想做亚马逊电商",
        "帮我计算房贷",
    ]

    dispatcher = AutoDispatcher()

    print("=" * 60)
    print("Auto Dispatcher Skill 测试")
    print("=" * 60)

    for text in test_cases:
        print(f"\n>>> {text}")
        print("-" * 40)
        result = dispatcher.dispatch(text)
        print(result)
        print("=" * 60)
