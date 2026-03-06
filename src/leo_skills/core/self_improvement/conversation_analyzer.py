# -*- coding: utf-8 -*-
"""
对话分析器 (Conversation Analyzer)

分析飞书/OpenClaw 会话历史，提取：
- 高频意图
- 未匹配查询
- 成功/失败模式
- 用户偏好
"""

import json
import logging
import re
from collections import Counter
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

logger = logging.getLogger(__name__)


@dataclass
class IntentPattern:
    """意图模式"""
    category: str
    keywords: List[str]
    frequency: int
    examples: List[str]
    confidence: float


@dataclass
class UnmatchedQuery:
    """未匹配查询"""
    query: str
    timestamp: str
    context: str
    suggested_category: Optional[str]


@dataclass
class ConversationInsight:
    """对话洞察"""
    analyzed_at: str
    total_messages: int
    date_range: Tuple[str, str]

    # 意图分析
    top_intents: List[IntentPattern]
    intent_distribution: Dict[str, int]

    # 未匹配分析
    unmatched_queries: List[UnmatchedQuery]
    unmatched_rate: float

    # 技能使用统计
    skill_usage: Dict[str, int]
    top_skills: List[str]

    # 用户偏好
    preferred_categories: List[str]
    active_hours: List[int]

    # 优化建议
    improvement_suggestions: List[Dict[str, Any]]


class ConversationAnalyzer:
    """
    对话分析器

    分析 OpenClaw 会话历史，生成优化洞察。
    """

    # 意图分类关键词
    INTENT_KEYWORDS = {
        "development": [
            "代码", "编程", "开发", "script", "code", "api", "refactor",
            "部署", "deploy", "bug", "fix", "debug", "调试", "测试"
        ],
        "content": [
            "文章", "内容", "创作", "写作", "文案", "article", "content",
            "publish", "发布", "seo", "copy", "写作", "标题"
        ],
        "realestate": [
            "房产", "别墅", "房源", "楼盘", "客户", "带看", "成交",
            "villa", "property", "residential", "commercial", "leasing"
        ],
        "loan": [
            "贷款", "利率", "银行", "按揭", "抵押", "资质", "额度",
            "loan", "mortgage", "credit", "interest"
        ],
        "ecommerce": [
            "电商", "产品", "上架", "亚马逊", "店铺", "订单", "库存",
            "amazon", "shopify", "product", "listing", "inventory"
        ],
        "analysis": [
            "分析", "报告", "数据", "研究", "调研", "对比", "评估",
            "analyze", "research", "report", "data", "study"
        ],
        "automation": [
            "自动化", "定时", "批量", "脚本", "workflow", "pipeline",
            "cron", "schedule", "自动", "批量"
        ],
        "learning": [
            "学习", "教程", "怎么", "如何", "什么是", "解释", "说明",
            "learn", "how to", "what is", "explain", "tutorial"
        ],
    }

    def __init__(
        self,
        sessions_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None
    ):
        """
        初始化分析器

        Args:
            sessions_dir: OpenClaw 会话目录，默认 ~/.openclaw/agents/leo-assistant/sessions/
            output_dir: 分析结果输出目录
        """
        if sessions_dir is None:
            home = Path.home()
            self.sessions_dir = home / ".openclaw" / "agents" / "leo-assistant" / "sessions"
        else:
            self.sessions_dir = Path(sessions_dir)

        if output_dir is None:
            self.output_dir = Path(__file__).parent.parent.parent.parent.parent / "docs" / "research"
        else:
            self.output_dir = Path(output_dir)

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def analyze(
        self,
        days: int = 7,
        min_frequency: int = 2
    ) -> ConversationInsight:
        """
        执行完整分析

        Args:
            days: 分析最近几天的数据
            min_frequency: 最小频率阈值

        Returns:
            分析洞察
        """
        logger.info(f"开始分析最近 {days} 天的会话数据...")

        # 1. 加载会话数据
        sessions = self._load_sessions(days)
        logger.info(f"加载了 {len(sessions)} 个会话")

        # 2. 提取所有消息
        messages = self._extract_messages(sessions)
        logger.info(f"提取了 {len(messages)} 条消息")

        if not messages:
            return self._empty_insight()

        # 3. 分析意图分布
        intents, intent_dist = self._analyze_intents(messages, min_frequency)

        # 4. 识别未匹配查询
        unmatched = self._find_unmatched_queries(messages)

        # 5. 统计技能使用
        skill_usage, top_skills = self._analyze_skill_usage(messages)

        # 6. 分析用户行为
        preferred_cats, active_hours = self._analyze_user_behavior(messages)

        # 7. 生成优化建议
        suggestions = self._generate_suggestions(
            intents, unmatched, skill_usage, preferred_cats
        )

        # 8. 构建洞察
        insight = ConversationInsight(
            analyzed_at=datetime.now().isoformat(),
            total_messages=len(messages),
            date_range=self._get_date_range(messages),
            top_intents=intents[:10],
            intent_distribution=intent_dist,
            unmatched_queries=unmatched[:20],
            unmatched_rate=len(unmatched) / max(len(messages), 1),
            skill_usage=skill_usage,
            top_skills=top_skills[:10],
            preferred_categories=preferred_cats,
            active_hours=active_hours,
            improvement_suggestions=suggestions
        )

        # 9. 保存结果
        self._save_insight(insight)

        return insight

    def _load_sessions(self, days: int) -> List[Dict]:
        """加载会话文件"""
        sessions = []
        cutoff_date = datetime.now() - timedelta(days=days)

        if not self.sessions_dir.exists():
            logger.warning(f"Sessions directory not found: {self.sessions_dir}")
            return sessions

        for session_file in self.sessions_dir.glob("*.json"):
            try:
                # 检查文件修改时间
                mtime = datetime.fromtimestamp(session_file.stat().st_mtime)
                if mtime < cutoff_date:
                    continue

                with open(session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["_file"] = str(session_file)
                    data["_mtime"] = mtime.isoformat()
                    sessions.append(data)

            except Exception as e:
                logger.debug(f"Failed to load session {session_file}: {e}")

        return sessions

    def _extract_messages(self, sessions: List[Dict]) -> List[Dict]:
        """提取所有用户消息"""
        messages = []

        for session in sessions:
            # OpenClaw 会话格式
            history = session.get("history", [])

            for msg in history:
                # 只分析用户消息
                if msg.get("role") == "user":
                    messages.append({
                        "content": msg.get("content", ""),
                        "timestamp": msg.get("timestamp", ""),
                        "session_id": session.get("id", ""),
                        "message_id": msg.get("id", ""),
                    })

        return messages

    def _analyze_intents(
        self,
        messages: List[Dict],
        min_frequency: int
    ) -> Tuple[List[IntentPattern], Dict[str, int]]:
        """分析意图分布"""
        category_counts = Counter()
        category_examples = {cat: [] for cat in self.INTENT_KEYWORDS.keys()}
        category_keywords = {cat: Counter() for cat in self.INTENT_KEYWORDS.keys()}

        for msg in messages:
            content = msg.get("content", "").lower()

            for category, keywords in self.INTENT_KEYWORDS.items():
                matched_keywords = []

                for kw in keywords:
                    if kw.lower() in content:
                        matched_keywords.append(kw)
                        category_keywords[cat][kw] += 1

                if matched_keywords:
                    category_counts[category] += 1

                    # 保存示例 (限制每个类别最多保存5个)
                    if len(category_examples[category]) < 5:
                        category_examples[category].append(content[:100])

        # 构建意图模式
        intents = []
        for category, count in category_counts.most_common():
            if count >= min_frequency:
                top_keywords = [kw for kw, _ in category_keywords[category].most_common(5)]

                intents.append(IntentPattern(
                    category=category,
                    keywords=top_keywords,
                    frequency=count,
                    examples=category_examples[category],
                    confidence=min(0.95, 0.6 + count * 0.01)
                ))

        intent_dist = dict(category_counts)

        return intents, intent_dist

    def _find_unmatched_queries(self, messages: List[Dict]) -> List[UnmatchedQuery]:
        """识别未匹配查询（可能的新意图）"""
        unmatched = []

        for msg in messages:
            content = msg.get("content", "").lower()

            # 检查是否匹配任何已知意图
            matched = False
            for keywords in self.INTENT_KEYWORDS.values():
                if any(kw in content for kw in keywords):
                    matched = True
                    break

            # 如果不匹配且长度适中（可能是有效查询）
            if not matched and 10 < len(content) < 200:
                # 尝试推测可能的类别
                suggested = self._suggest_category(content)

                unmatched.append(UnmatchedQuery(
                    query=content[:150],
                    timestamp=msg.get("timestamp", ""),
                    context=msg.get("session_id", "")[:8],
                    suggested_category=suggested
                ))

        return unmatched

    def _suggest_category(self, content: str) -> Optional[str]:
        """基于内容推测可能的类别"""
        # 简单的关键词匹配
        suggestions = {
            "development": ["python", "javascript", "代码", "函数", "class", "import"],
            "content": ["文章", "标题", "公众号", "小红书", "抖音", "视频号"],
            "realestate": ["客户", "带看", "房源", "价格", "房东", "买家"],
            "loan": ["银行", "利率", "贷款", "月供", "首付", "征信"],
            "ecommerce": ["产品", "订单", "物流", "亚马逊", "shopify", "上架"],
        }

        scores = {cat: 0 for cat in suggestions}
        for category, keywords in suggestions.items():
            for kw in keywords:
                if kw in content:
                    scores[category] += 1

        if scores:
            best = max(scores, key=scores.get)
            if scores[best] > 0:
                return best

        return None

    def _analyze_skill_usage(
        self,
        messages: List[Dict]
    ) -> Tuple[Dict[str, int], List[str]]:
        """分析技能使用统计"""
        skill_pattern = re.compile(r'(?:使用|执行|调用|运行|use|run|execute)\s+(\w+_skill)', re.IGNORECASE)

        skill_counts = Counter()

        for msg in messages:
            content = msg.get("content", "")
            matches = skill_pattern.findall(content)
            for match in matches:
                skill_counts[match] += 1

        return dict(skill_counts), [s for s, _ in skill_counts.most_common()]

    def _analyze_user_behavior(
        self,
        messages: List[Dict]
    ) -> Tuple[List[str], List[int]]:
        """分析用户行为模式"""
        # 活跃时间
        hours = []
        for msg in messages:
            ts = msg.get("timestamp", "")
            try:
                if ts:
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    hours.append(dt.hour)
            except:
                pass

        hour_dist = Counter(hours)
        active_hours = [h for h, c in hour_dist.most_common(5)]

        # 从意图推断偏好类别
        preferred = []
        return preferred, active_hours

    def _generate_suggestions(
        self,
        intents: List[IntentPattern],
        unmatched: List[UnmatchedQuery],
        skill_usage: Dict[str, int],
        preferred_cats: List[str]
    ) -> List[Dict[str, Any]]:
        """生成优化建议"""
        suggestions = []

        # 建议 1: 高频意图自动化
        for intent in intents[:3]:
            if intent.frequency >= 5:
                suggestions.append({
                    "type": "auto_skill",
                    "priority": "high",
                    "category": intent.category,
                    "description": f"意图 '{intent.category}' 出现 {intent.frequency} 次，建议创建自动化技能",
                    "keywords": intent.keywords,
                    "action": f"create_skill_{intent.category}"
                })

        # 建议 2: 未匹配查询处理
        if len(unmatched) > 10:
            # 聚类未匹配查询
            clustered = self._cluster_unmatched(unmatched)
            for cluster_name, queries in clustered.items():
                if len(queries) >= 3:
                    suggestions.append({
                        "type": "new_intent",
                        "priority": "medium",
                        "description": f"发现潜在新意图 '{cluster_name}' ({len(queries)} 次查询)",
                        "examples": [q.query[:50] for q in queries[:3]],
                        "action": f"define_intent_{cluster_name}"
                    })

        # 建议 3: 技能推荐优化
        if skill_usage:
            top_skill = max(skill_usage, key=skill_usage.get)
            suggestions.append({
                "type": "skill_optimization",
                "priority": "low",
                "description": f"最常用技能 '{top_skill}' 可优化执行效率",
                "action": "optimize_top_skill"
            })

        return suggestions

    def _cluster_unmatched(
        self,
        unmatched: List[UnmatchedQuery]
    ) -> Dict[str, List[UnmatchedQuery]]:
        """对未匹配查询进行简单聚类"""
        clusters = {}

        for query in unmatched:
            cat = query.suggested_category or "unknown"
            if cat not in clusters:
                clusters[cat] = []
            clusters[cat].append(query)

        return clusters

    def _get_date_range(self, messages: List[Dict]) -> Tuple[str, str]:
        """获取日期范围"""
        timestamps = []
        for msg in messages:
            ts = msg.get("timestamp", "")
            if ts:
                timestamps.append(ts)

        if timestamps:
            return (min(timestamps)[:10], max(timestamps)[:10])
        return ("", "")

    def _empty_insight(self) -> ConversationInsight:
        """空洞察"""
        return ConversationInsight(
            analyzed_at=datetime.now().isoformat(),
            total_messages=0,
            date_range=("", ""),
            top_intents=[],
            intent_distribution={},
            unmatched_queries=[],
            unmatched_rate=0.0,
            skill_usage={},
            top_skills=[],
            preferred_categories=[],
            active_hours=[],
            improvement_suggestions=[]
        )

    def _save_insight(self, insight: ConversationInsight) -> None:
        """保存分析结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"conversation_insight_{timestamp}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(asdict(insight), f, ensure_ascii=False, indent=2)

        logger.info(f"Insight saved to {output_file}")

        # 同时生成 Markdown 报告
        md_file = self.output_dir / f"conversation_insight_{timestamp}.md"
        self._generate_markdown_report(insight, md_file)

    def _generate_markdown_report(
        self,
        insight: ConversationInsight,
        output_file: Path
    ) -> None:
        """生成 Markdown 报告"""
        lines = [
            "# 对话分析报告",
            "",
            f"- 分析时间: {insight.analyzed_at}",
            f"- 分析范围: {insight.date_range[0]} 至 {insight.date_range[1]}",
            f"- 消息总数: {insight.total_messages}",
            f"- 未匹配率: {insight.unmatched_rate:.1%}",
            "",
            "## 热门意图 Top 10",
            "",
        ]

        for i, intent in enumerate(insight.top_intents, 1):
            lines.extend([
                f"{i}. **{intent.category}** ({intent.frequency} 次)",
                f"   - 关键词: {', '.join(intent.keywords)}",
                f"   - 置信度: {intent.confidence:.2f}",
                ""
            ])

        lines.extend([
            "",
            "## 未匹配查询分析",
            "",
            f"共发现 {len(insight.unmatched_queries)} 条未匹配查询",
            "",
        ])

        for q in insight.unmatched_queries[:10]:
            cat = f"(推测: {q.suggested_category})" if q.suggested_category else ""
            lines.append(f"- `{q.query[:60]}...` {cat}")

        lines.extend([
            "",
            "## 技能使用统计",
            "",
        ])

        for skill, count in sorted(
            insight.skill_usage.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]:
            lines.append(f"- {skill}: {count} 次")

        lines.extend([
            "",
            "## 优化建议",
            "",
        ])

        for i, suggestion in enumerate(insight.improvement_suggestions, 1):
            lines.extend([
                f"{i}. [{suggestion['priority'].upper()}] {suggestion['type']}",
                f"   - {suggestion['description']}",
                f"   - 建议操作: `{suggestion['action']}`",
                ""
            ])

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logger.info(f"Markdown report saved to {output_file}")

    def get_recent_insights(self, count: int = 5) -> List[Path]:
        """获取最近的分析报告"""
        files = sorted(
            self.output_dir.glob("conversation_insight_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        return files[:count]

    def compare_insights(self, file1: Path, file2: Path) -> Dict[str, Any]:
        """对比两个时间点的洞察"""
        try:
            with open(file1, "r", encoding="utf-8") as f:
                insight1 = json.load(f)
            with open(file2, "r", encoding="utf-8") as f:
                insight2 = json.load(f)

            return {
                "period1": insight1.get("date_range"),
                "period2": insight2.get("date_range"),
                "message_delta": insight2.get("total_messages", 0) - insight1.get("total_messages", 0),
                "unmatched_rate_delta": insight2.get("unmatched_rate", 0) - insight1.get("unmatched_rate", 0),
                "new_intents": list(
                    set(i["category"] for i in insight2.get("top_intents", [])) -
                    set(i["category"] for i in insight1.get("top_intents", []))
                ),
                "improved_areas": [
                    s["category"] for s in insight2.get("improvement_suggestions", [])
                    if s["priority"] == "high"
                ]
            }
        except Exception as e:
            return {"error": str(e)}


# 便捷函数
def analyze_conversations(days: int = 7) -> ConversationInsight:
    """快速分析入口"""
    analyzer = ConversationAnalyzer()
    return analyzer.analyze(days=days)


if __name__ == "__main__":
    # 测试运行
    insight = analyze_conversations(days=7)
    print(f"分析完成: {insight.total_messages} 条消息")
    print(f"热门意图: {[i.category for i in insight.top_intents[:5]]}")
    print(f"优化建议: {len(insight.improvement_suggestions)} 条")
