# -*- coding: utf-8 -*-
"""
自优化引擎 (Self-Optimization Engine)

OpenClaw "越用越好" 的核心实现：
1. 自动分析会话历史
2. 发现优化机会
3. 推荐或自动生成技能
4. 追踪效果并持续改进
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

from .conversation_analyzer import ConversationAnalyzer, analyze_conversations
from .skill_recommender import SkillRecommender, SkillGenerationRequest
from .performance_tracker import PerformanceTracker

logger = logging.getLogger(__name__)


class SelfOptimizationEngine:
    """
    自优化引擎

    实现完整的自优化闭环：
    感知(分析) → 认知(推荐) → 执行(生成) → 反馈(追踪)
    """

    def __init__(self):
        self.analyzer = ConversationAnalyzer()
        self.recommender = SkillRecommender()
        self.tracker = PerformanceTracker()

        self.project_root = Path(__file__).parent.parent.parent.parent.parent
        self.optimization_log = self.project_root / "docs" / "research" / "optimization_log.json"

    async def run_optimization_cycle(self) -> Dict[str, Any]:
        """
        运行完整优化周期

        Returns:
            优化结果报告
        """
        logger.info("=" * 60)
        logger.info("启动自优化周期")
        logger.info("=" * 60)

        results = {
            "started_at": datetime.now().isoformat(),
            "steps": []
        }

        # Step 1: 分析对话
        logger.info("[1/4] 分析对话历史...")
        insight = await self._step_analyze()
        results["steps"].append({
            "step": "analyze",
            "status": "success" if insight.total_messages > 0 else "skipped",
            "messages_analyzed": insight.total_messages,
            "top_intents": [i.category for i in insight.top_intents[:5]]
        })

        # Step 2: 推荐技能
        logger.info("[2/4] 生成技能推荐...")
        recommendations = await self._step_recommend(insight)
        results["steps"].append({
            "step": "recommend",
            "status": "success",
            "recommendations_count": len(recommendations),
            "high_confidence": len([r for r in recommendations if r.confidence > 0.8])
        })

        # Step 3: 生成新技能 (可选)
        logger.info("[3/4] 评估新技能生成...")
        generated = await self._step_generate(insight, recommendations)
        results["steps"].append({
            "step": "generate",
            "status": "success",
            "generated_count": len(generated),
            "generated_skills": [g["skill_name"] for g in generated]
        })

        # Step 4: 生成报告
        logger.info("[4/4] 生成优化报告...")
        report = await self._step_report(insight, recommendations, generated)
        results["steps"].append({
            "step": "report",
            "status": "success",
            "report_path": str(report.get("report_path", ""))
        })

        results["completed_at"] = datetime.now().isoformat()
        results["summary"] = {
            "messages_analyzed": insight.total_messages,
            "recommendations": len(recommendations),
            "skills_generated": len(generated),
            "improvement_suggestions": len(insight.improvement_suggestions)
        }

        # 保存优化日志
        self._save_optimization_log(results)

        logger.info("=" * 60)
        logger.info("自优化周期完成")
        logger.info(f"  - 分析消息: {insight.total_messages}")
        logger.info(f"  - 技能推荐: {len(recommendations)}")
        logger.info(f"  - 自动生成: {len(generated)}")
        logger.info("=" * 60)

        return results

    async def _step_analyze(self):
        """分析步骤"""
        return self.analyzer.analyze(days=7, min_frequency=2)

    async def _step_recommend(self, insight):
        """推荐步骤"""
        recommendations = []

        # 为每个高频意图推荐技能
        for intent in insight.top_intents[:5]:
            recs = self.recommender.recommend_for_intent(
                intent.category,
                intent.keywords,
                top_n=3
            )
            recommendations.extend(recs)

        return recommendations

    async def _step_generate(self, insight, recommendations):
        """生成步骤"""
        generated = []

        # 找出高优先级的新意图建议
        new_intent_suggestions = [
            s for s in insight.improvement_suggestions
            if s.get("type") == "new_intent" and s.get("priority") == "high"
        ]

        for suggestion in new_intent_suggestions[:3]:  # 最多生成3个
            category = suggestion.get("category", "general")

            request = SkillGenerationRequest(
                intent_category=category,
                trigger_keywords=suggestion.get("keywords", [category]),
                description=suggestion.get("description", f"Auto-generated skill for {category}"),
                example_inputs=suggestion.get("examples", []),
                priority="high",
                context={"source": "self_optimization", "suggestion": suggestion}
            )

            try:
                skill_code = self.recommender.generate_skill_code(request)

                # 保存生成的技能 (草稿状态)
                saved = self._save_generated_skill(skill_code)
                if saved:
                    generated.append(skill_code)
                    logger.info(f"Generated skill draft: {skill_code['skill_name']}")

            except Exception as e:
                logger.error(f"Failed to generate skill: {e}")

        return generated

    async def _step_report(self, insight, recommendations, generated):
        """报告步骤"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        report = {
            "generated_at": datetime.now().isoformat(),
            "period": insight.date_range,
            "summary": {
                "total_messages": insight.total_messages,
                "unmatched_rate": insight.unmatched_rate,
                "top_intents": [
                    {
                        "category": i.category,
                        "frequency": i.frequency,
                        "confidence": i.confidence
                    }
                    for i in insight.top_intents[:10]
                ]
            },
            "recommendations": [
                {
                    "skill": r.skill_name,
                    "confidence": r.confidence,
                    "reason": r.reason,
                    "effort": r.estimated_effort
                }
                for r in recommendations[:10]
            ],
            "generated_skills": [
                {
                    "name": g["skill_name"],
                    "category": g["category"],
                    "triggers": g["triggers"]
                }
                for g in generated
            ],
            "improvement_suggestions": insight.improvement_suggestions
        }

        # 保存报告
        report_dir = self.project_root / "docs" / "research"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"self_optimization_report_{timestamp}.json"

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        # 同时生成 Markdown
        md_path = report_dir / f"self_optimization_report_{timestamp}.md"
        self._generate_markdown_report(report, md_path)

        return {
            "report_path": report_path,
            "markdown_path": md_path,
            "data": report
        }

    def _save_generated_skill(self, skill_code: Dict[str, Any]) -> bool:
        """保存生成的技能草稿"""
        try:
            draft_dir = self.project_root / "src" / "leo_skills" / "_generated"
            draft_dir.mkdir(exist_ok=True)

            skill_dir = draft_dir / skill_code["skill_name"]
            skill_dir.mkdir(exist_ok=True)

            # 保存文件
            for file_path, content in skill_code["files"].items():
                full_path = skill_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding="utf-8")

            logger.info(f"Saved skill draft to {skill_dir}")
            return True

        except Exception as e:
            logger.error(f"Failed to save generated skill: {e}")
            return False

    def _generate_markdown_report(self, report: Dict[str, Any], output_path: Path):
        """生成 Markdown 报告"""
        lines = [
            "# 自优化报告",
            "",
            f"**生成时间**: {report['generated_at']}",
            f"**分析周期**: {report['period'][0]} 至 {report['period'][1]}",
            "",
            "## 数据概览",
            "",
            f"- 分析消息数: {report['summary']['total_messages']}",
            f"- 未匹配率: {report['summary']['unmatched_rate']:.1%}",
            "",
            "## 热门意图 Top 10",
            "",
        ]

        for intent in report['summary']['top_intents']:
            lines.append(f"- **{intent['category']}**: {intent['frequency']} 次 (置信度: {intent['confidence']:.2f})")

        lines.extend(["", "## 技能推荐", ""])

        for rec in report['recommendations']:
            lines.extend([
                f"### {rec['skill']}",
                f"- 置信度: {rec['confidence']:.2f}",
                f"- 工作量: {rec['effort']}",
                f"- 原因: {rec['reason']}",
                ""
            ])

        if report['generated_skills']:
            lines.extend(["## 自动生成的技能", ""])
            for skill in report['generated_skills']:
                lines.append(f"- **{skill['name']}** ({skill['category']})")
                lines.append(f"  - 触发词: {', '.join(skill['triggers'])}")

        lines.extend(["", "## 优化建议", ""])

        for suggestion in report['improvement_suggestions']:
            lines.append(f"- [{suggestion['priority'].upper()}] {suggestion['description']}")

        output_path.write_text("\n".join(lines), encoding="utf-8")

    def _save_optimization_log(self, results: Dict[str, Any]):
        """保存优化日志"""
        try:
            logs = []
            if self.optimization_log.exists():
                with open(self.optimization_log, "r", encoding="utf-8") as f:
                    logs = json.load(f)

            logs.append(results)

            # 只保留最近 100 条
            logs = logs[-100:]

            with open(self.optimization_log, "w", encoding="utf-8") as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"Failed to save optimization log: {e}")

    def get_optimization_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取优化历史"""
        if not self.optimization_log.exists():
            return []

        try:
            with open(self.optimization_log, "r", encoding="utf-8") as f:
                logs = json.load(f)
            return logs[-limit:]
        except Exception as e:
            logger.error(f"Failed to load optimization history: {e}")
            return []

    async def schedule_daily(self, hour: int = 6):
        """
        调度每日运行

        Args:
            hour: 运行小时 (24小时制)
        """
        logger.info(f"Scheduling daily optimization at {hour}:00")

        while True:
            now = datetime.now()
            target = now.replace(hour=hour, minute=0, second=0)

            if target <= now:
                target += timedelta(days=1)

            wait_seconds = (target - now).total_seconds()
            logger.info(f"Next optimization in {wait_seconds/3600:.1f} hours")

            await asyncio.sleep(wait_seconds)
            await self.run_optimization_cycle()


# 便捷函数
async def run_self_optimization() -> Dict[str, Any]:
    """快速运行入口"""
    engine = SelfOptimizationEngine()
    return await engine.run_optimization_cycle()


def quick_analyze():
    """快速分析入口"""
    insight = analyze_conversations(days=7)
    print(f"\n📊 分析完成")
    print(f"   消息数: {insight.total_messages}")
    print(f"   热门意图: {', '.join(i.category for i in insight.top_intents[:5])}")
    print(f"   未匹配率: {insight.unmatched_rate:.1%}")
    print(f"   优化建议: {len(insight.improvement_suggestions)} 条")


if __name__ == "__main__":
    # 测试运行
    import asyncio
    asyncio.run(run_self_optimization())
