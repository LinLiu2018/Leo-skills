"""
Leo Intent Router - 意图路由器

自动识别用户意图，决定调用 OpenClaw 还是 Leo System 的能力。

架构:
    用户输入
        ↓
    ┌─────────────────────────────────────┐
    │         IntentClassifier              │
    │  - 关键词匹配                       │
    │  - 能力注册表                       │
    │  - 置信度计算                       │
    └─────────────────────────────────────┘
        ↓
    路由决策 → 调用对应系统
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

# ============================================================
# 系统枚举
# ============================================================

class TargetSystem(str, Enum):
    """目标系统"""
    OPENCLAW = "openclaw"      # OpenClaw 内置能力
    LEO = "leo"               # Leo System 能力
    BOTH = "both"             # 两者都可
    UNKNOWN = "unknown"        # 未知


# ============================================================
# 意图分类
# ============================================================

class IntentCategory(str, Enum):
    """意图类别"""
    # OpenClaw 专属
    FEISHU = "feishu"              # 飞书操作
    BROWSER = "browser"            # 浏览器控制
    GITHUB = "github"             # GitHub 操作
    FILE_SYSTEM = "file_system"    # 文件操作

    # Leo System 专属
    REALESTATE = "realestate"      # 房产咨询
    ECOMMERCE = "ecommerce"        # 电商运营
    CONTENT = "content"            # 内容创作
    LOAN = "loan"                # 贷款咨询

    # 通用
    GENERAL = "general"            # 通用问答
    RESEARCH = "research"          # 研究分析
    CODE = "code"                 # 代码开发


# ============================================================
# 能力定义
# ============================================================

@dataclass
class Capability:
    """能力定义"""
    name: str
    description: str
    keywords: List[str]           # 关键词
    target_system: TargetSystem
    category: IntentCategory
    examples: List[str] = field(default_factory=list)


# ============================================================
# 能力注册表
# ============================================================

class CapabilityRegistry:
    """能力注册表"""

    def __init__(self):
        self._capabilities: List[Capability] = []

    def register(self, capability: Capability) -> None:
        """注册能力"""
        self._capabilities.append(capability)

    def match(self, user_input: str) -> List[tuple[Capability, float]]:
        """匹配用户输入，返回 (能力, 置信度) 列表"""
        user_input_lower = user_input.lower()
        results = []

        for cap in self._capabilities:
            score = self._calculate_score(user_input_lower, cap)
            if score > 0:
                results.append((cap, score))

        # 按置信度排序
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def _calculate_score(self, user_input: str, capability: Capability) -> float:
        """计算匹配分数"""
        score = 0.0

        # 1. 精确关键词匹配 (权重: 0.8)
        for keyword in capability.keywords:
            if keyword in user_input:
                score += 0.8

        # 2. 示例匹配 (权重: 0.5)
        for example in capability.examples:
            if example.lower() in user_input:
                score += 0.5

        # 3. 描述关键词匹配 (权重: 0.3)
        desc_words = capability.description.lower().split()
        for word in desc_words:
            if len(word) > 2 and word in user_input:
                score += 0.3

        return min(score, 1.0)  # 最高1.0


# ============================================================
# 意图路由器
# ============================================================

class IntentRouter:
    """意图路由器"""

    def __init__(self):
        self.registry = CapabilityRegistry()
        self._register_default_capabilities()

    def _register_default_capabilities(self) -> None:
        """注册默认能力"""

        # ========== OpenClaw 能力 ==========
        self.registry.register(Capability(
            name="feishu_send",
            description="发送飞书消息",
            keywords=["发飞书", "发消息", "飞书", "发送消息", "拉群"],
            target_system=TargetSystem.OPENCLAW,
            category=IntentCategory.FEISHU,
            examples=["帮我发消息给张三", "拉个群"]
        ))

        self.registry.register(Capability(
            name="browser_control",
            description="浏览器自动化控制",
            keywords=["浏览器", "截图", "打开网页", "点击", "爬虫"],
            target_system=TargetSystem.OPENCLAW,
            category=IntentCategory.BROWSER,
            examples=["打开百度", "截个图"]
        ))

        self.registry.register(Capability(
            name="github_operate",
            description="GitHub 操作",
            keywords=["github", "git", "仓库", "commit", "pr", "issue"],
            target_system=TargetSystem.OPENCLAW,
            category=IntentCategory.GITHUB,
            examples=["查看仓库", "创建issue"]
        ))

        self.registry.register(Capability(
            name="file_operate",
            description="文件操作",
            keywords=["文件", "读取", "写入", "创建文件", "文件夹"],
            target_system=TargetSystem.OPENCLAW,
            category=IntentCategory.FILE_SYSTEM,
            examples=["创建文件", "读取内容"]
        ))

        # ========== Leo System 能力 ==========
        self.registry.register(Capability(
            name="realestate_consult",
            description="房产咨询（别墅、刚需、商业）",
            keywords=["房产", "房子", "别墅", "买房", "卖房", "租房", "商铺", "写字楼", "房价", "楼盘"],
            target_system=TargetSystem.LEO,
            category=IntentCategory.REALESTATE,
            examples=["宁波房价怎么样", "推荐别墅", "商铺投资"]
        ))

        self.registry.register(Capability(
            name="loan_consult",
            description="贷款咨询",
            keywords=["贷款", "利率", "房贷", "按揭", "信用贷", "抵押贷款"],
            target_system=TargetSystem.LEO,
            category=IntentCategory.LOAN,
            examples=["贷款利率多少", "怎么办贷款"]
        ))

        self.registry.register(Capability(
            name="ecommerce_operate",
            description="电商运营",
            keywords=["电商", "亚马逊", "跨境", "商品", "listing", "运营"],
            target_system=TargetSystem.LEO,
            category=IntentCategory.ECOMMERCE,
            examples=["分析电商数据", "优化listing"]
        ))

        self.registry.register(Capability(
            name="content_create",
            description="内容创作（文案、视频脚本）",
            keywords=["写文章", "文案", "脚本", "短视频", "内容", "创作", "公众号", "小红书", "抖音"],
            target_system=TargetSystem.LEO,
            category=IntentCategory.CONTENT,
            examples=["写一篇公众号", "短视频脚本", "帮我文案"]
        ))

        self.registry.register(Capability(
            name="research_analysis",
            description="市场调研分析",
            keywords=["调研", "分析", "报告", "研究", "市场", "竞品"],
            target_system=TargetSystem.LEO,
            category=IntentCategory.RESEARCH,
            examples=["调研报告", "竞品分析", "市场分析"]
        ))

    def route(self, user_input: str) -> Dict[str, Any]:
        """路由决策

        Returns:
            {
                "target_system": TargetSystem,
                "category": IntentCategory,
                "capability": str,
                "confidence": float,
                "reason": str
            }
        """
        matches = self.registry.match(user_input)

        if not matches:
            return {
                "target_system": TargetSystem.UNKNOWN,
                "category": IntentCategory.GENERAL,
                "capability": None,
                "confidence": 0.0,
                "reason": "无法识别意图，使用通用处理"
            }

        best_match = matches[0]
        capability = best_match[0]
        confidence = best_match[1]

        # 置信度阈值判断
        if confidence < 0.3:
            return {
                "target_system": TargetSystem.UNKNOWN,
                "category": IntentCategory.GENERAL,
                "capability": capability.name,
                "confidence": confidence,
                "reason": "置信度较低，使用通用处理"
            }

        return {
            "target_system": capability.target_system,
            "category": capability.category,
            "capability": capability.name,
            "confidence": confidence,
            "reason": f"匹配到 '{capability.name}'，置信度 {confidence:.2f}"
        }


# ============================================================
# 全局实例
# ============================================================

_intent_router: Optional[IntentRouter] = None


def get_intent_router() -> IntentRouter:
    """获取全局意图路由器"""
    global _intent_router
    if _intent_router is None:
        _intent_router = IntentRouter()
    return _intent_router


# ============================================================
# 使用示例
# ============================================================

if __name__ == "__main__":
    router = get_intent_router()

    # 测试用例
    test_inputs = [
        "帮我发消息给张三",
        "宁波房价现在多少",
        "写一篇房产公众号文章",
        "帮我打开百度",
        "贷款利率怎么算",
    ]

    for user_input in test_inputs:
        result = router.route(user_input)
        print(f"\n输入: {user_input}")
        print(f"目标系统: {result['target_system'].value}")
        print(f"置信度: {result['confidence']:.2f}")
        print(f"原因: {result['reason']}")
