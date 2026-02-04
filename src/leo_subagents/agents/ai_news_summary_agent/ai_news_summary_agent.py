"""
DailyNewsSummaryAgent

每日情报战略官 - 全球商业情报深度版
支持 AI动态、国际政治、财经新闻三大板块
每板块精选10条，转化为决策情报
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

# 添加父目录到路径
parent_path = Path(__file__).parent.parent.parent
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))

if TYPE_CHECKING:
    from leo_subagents.agents.base_agent import BaseAgent, AgentConfig
else:
    from leo_subagents.agents.base_agent import BaseAgent, AgentConfig

from leo_subagents.agents.base_agent import logger
from leo_system.metrics import track_time


class DailyNewsSummaryAgent(BaseAgent):
    """
    DailyNewsSummaryAgent - 每日情报战略官

    全球商业情报深度版，转化新闻为决策情报
    """

    # 新闻类别配置 - 扩展搜索关键词
    NEWS_CATEGORIES = {
        "ai": {
            "keywords": ["AI", "大模型", "LLM", "ChatGPT", "Claude", "OpenAI", "机器学习", "深度学习", "AI芯片"],
            "name": "AI动态",
            "section": "🤖 1. AI 动态 Top 10",
            "source_keywords": ["TechCrunch", "The Verge", "Wired", "OpenAI Blog", "Anthropic", "MIT Technology Review"]
        },
        "finance": {
            "keywords": ["股市", "美股", "A股", "基金", "比特币", "加密货币", "crypto", "美联储", "通胀", "GDP"],
            "name": "财经新闻",
            "section": "💰 3. 财经新闻 Top 10",
            "source_keywords": ["Bloomberg", "Reuters", "CNBC", "Financial Times", "WSJ"]
        },
        "politics": {
            "keywords": ["中美关系", "国际政治", "政策", "关税", "贸易战", "地缘政治", "两会", "政府工作报告"],
            "name": "国际政治",
            "section": "🌏 2. 国际政治 Top 10",
            "source_keywords": ["Reuters", "AP News", "BBC", "FT", "The Economist"]
        }
    }

    def __init__(self, config: AgentConfig):
        """初始化 Agent"""
        super().__init__(config)
        self.agent_name = "daily_intelligence"

    def can_handle(self, task: str) -> float:
        """判断是否能处理此任务"""
        task_lower = task.lower()

        # 情报战略官关键词
        intelligence_keywords = [
            "情报", "商业情报", "深度情报", "决策情报",
            "全球情报", "战略情报", "每日情报"
        ]

        for keyword in intelligence_keywords:
            if keyword.lower() in task_lower:
                return 0.95

        # 新闻摘要关键词
        news_keywords = [
            "新闻摘要", "今日新闻", "每日快报", "要闻汇总", "新闻日报",
            "财经要闻", "政治新闻", "AI新闻"
        ]

        for keyword in news_keywords:
            if keyword.lower() in task_lower:
                return 0.85

        return 0.3

    def _detect_category(self, task: str) -> List[str]:
        """检测任务需要的新闻类别"""
        task_lower = task.lower()
        categories = []

        # AI 相关
        if any(kw in task_lower for kw in ["ai", "大模型", "llm", "人工智能"]):
            categories.append("ai")

        # 财经相关
        if any(kw in task_lower for kw in ["财经", "股市", "经济", "金融"]):
            categories.append("finance")

        # 政治相关
        if any(kw in task_lower for kw in ["政治", "政策", "国际", "外交"]):
            categories.append("politics")

        # 默认返回所有类别（情报模式）
        if not categories:
            categories = ["ai", "politics", "finance"]

        return categories

    def _search_news(self, category: str, max_results: int = 15) -> List[Dict[str, Any]]:
        """搜索指定类别的新闻"""
        category_config = self.NEWS_CATEGORIES.get(category, {})
        keywords = category_config.get("keywords", [])

        news_results = []
        for keyword in keywords[:5]:
            try:
                search_result = self.use_skill(
                    "web_search_skill",
                    "search",
                    query=f"{keyword} latest news 2026-02",
                    max_results=max_results
                )

                if search_result.get("success"):
                    news_results.extend([
                        {
                            "keyword": keyword,
                            "title": item.get("title", ""),
                            "url": item.get("url", ""),
                            "snippet": item.get("snippet", ""),
                            "source": item.get("source", ""),
                            "category": category
                        }
                        for item in search_result.get("results", [])[:max_results]
                    ])
            except Exception as e:
                logger.warning(f"搜索 {keyword} 失败: {e}")

        return news_results[:10]  # 每类别最多10条

    def _analyze_opportunity(self, news: Dict, category: str) -> str:
        """分析商机/影响/信号"""
        title = news.get('title', '')
        snippet = news.get('snippet', '')

        if category == "ai":
            # AI 动态分析
            if "OpenAI" in title or "GPT" in title:
                return "建议关注AI应用层创业机会，模型成本下降利好垂直场景。"
            elif "Anthropic" in title or "Claude" in title:
                return "关注企业级AI服务市场，差异化能力构建竞争壁垒。"
            elif "芯片" in title or "GPU" in title:
                return "算力需求持续增长，关注国产替代和液冷技术机会。"
            else:
                return "AI基础设施成熟，关注端侧AI和行业解决方案落地。"

        elif category == "politics":
            # 政治影响分析
            if "中美" in title or "美国" in title:
                return "关注国产替代板块，科技自主可控逻辑持续强化。"
            elif "关税" in title or "贸易" in title:
                return "供应链多元化趋势，关注东南亚和墨西哥产能转移。"
            elif "政策" in title or "两会" in title:
                return "关注新质生产力方向，数字经济和绿色低碳是主线。"
            else:
                return "地缘风险上升，关注军工和信息安全板块。"

        elif category == "finance":
            # 财经信号分析
            if "比特币" in title or "crypto" in title:
                return "加密市场波动加大，建议配置不超过总资产5%。"
            elif "美联储" in title or "利率" in title:
                return "利率见顶预期增强，利好成长股和长久期债券。"
            elif "AI" in title and ("股" in title or "财报" in title):
                return "AI相关财报超预期，科技股估值重塑进行中。"
            else:
                return "市场结构性机会为主，关注业绩预增和政策受益板块。"

        return "建议持续跟踪，等待更多数据验证。"

    def _generate_intelligence_report(self, news_data: Dict[str, List]) -> str:
        """生成深度情报报告"""
        today = datetime.now().strftime("%Y-%m-%d")
        report = f"# 📅 {today} 全球商业情报深度版\n\n"

        # 核心结语
        keywords = {
            "ai": "AI应用落地加速",
            "politics": "政策密集期",
            "finance": "业绩验证期"
        }
        core_keyword = keywords.get("ai", "结构性机会")

        for category in ["ai", "politics", "finance"]:
            category_config = self.NEWS_CATEGORIES.get(category, {})
            section = category_config.get("section", f"## {category}")
            news_list = news_data.get(category, [])

            report += f"{section}\n\n"

            for i, news in enumerate(news_list[:10], 1):
                title = news.get('title', '无标题')[:50]
                source = news.get('source', '来源') or "未知来源"
                snippet = news.get('snippet', '')[:80]

                opportunity = self._analyze_opportunity(news, category)

                if category == "ai":
                    report += f"### {i}. {title} @{source}\n"
                    report += f"*   **📝 摘要:** {snippet}...\n"
                    report += f"*   **💡 商机:** {opportunity}\n\n"
                elif category == "politics":
                    report += f"### {i}. {title} @{source}\n"
                    report += f"*   **📝 摘要:** {snippet}...\n"
                    report += f"*   **⚖️ 影响:** {opportunity}\n\n"
                else:
                    report += f"### {i}. {title} @{source}\n"
                    report += f"*   **📝 摘要:** {snippet}...\n"
                    report += f"*   **📈 信号:** {opportunity}\n\n"

        report += f"""---
**🧠 每日结语:** {core_keyword}，把握结构性机会。

---
*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
*由 Leo AI System - Daily Intelligence Strategist 自动生成*
"""

        return report

    @track_time
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """执行任务"""
        try:
            self.log_task(task, {"status": "started"})

            # 检测新闻类别
            categories = self._detect_category(task)
            self.logger.info(f"情报类别: {categories}")

            # 搜索各类别新闻
            news_data = {}
            for category in categories:
                news_data[category] = self._search_news(category)

            # 生成深度情报报告
            report = self._generate_intelligence_report(news_data)

            # 保存到 Obsidian
            from leo_skills.utilities.obsidian_sync_skill.scripts.main import ObsidianSync
            sync = ObsidianSync()
            obsidian_result = sync.save_leo_output(
                content=report,
                skill_name="daily_intelligence",
                title=f"全球商业情报_{datetime.now().strftime('%Y-%m-%d')}",
                folder="30-Resources/情报",
                tags=["情报", "深度", "AI", "财经", "政治"]
            )

            total_news = sum(len(news) for news in news_data.values())

            final_result = {
                "task": task,
                "status": "completed",
                "categories": categories,
                "total_news": total_news,
                "report": report,
                "obsidian_save": obsidian_result,
                "agent": self.agent_name
            }

            self.log_task(task, final_result)
            return final_result

        except Exception as e:
            error_result = {
                "task": task,
                "status": "failed",
                "error": str(e),
                "agent": self.agent_name
            }
            self.log_task(task, error_result)
            logger.error(f"Agent execution failed: {e}")
            return error_result
