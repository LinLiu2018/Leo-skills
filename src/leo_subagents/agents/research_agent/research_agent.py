"""
Research Agent
==============
Research-focused subagent that combines local project evidence and web retrieval.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

parent_path = Path(__file__).parent.parent.parent
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))

from leo_subagents.agents.base_agent import AgentConfig, AgentFactory, BaseAgent


class ResearchAgent(BaseAgent):
    ACTIVATION_KEYWORDS = ["研究", "调研", "分析", "报告", "收集", "整理", "查找", "搜索"]

    # Local project knowledge to avoid generic web-only responses.
    LOCAL_PROJECT_KB: Dict[str, Dict[str, Any]] = {
        "乐橙汇": {
            "aliases": ["乐橙汇", "乐橙荟", "橙汇", "橙荟", "宁波橙汇", "宁波乐橙汇", "宁波乐橙荟"],
            "facts": [
                "位置在宁波鄞州区环城南路与世纪大道交汇处，距离地铁5号线曹隘站约450米。",
                "在售核心产品为1F临街金铺，主力面积10-65㎡，定位24小时餐饮游乐基地和社区邻里中心。",
                "2公里内约15万+常住人口，项目材料强调3公里内缺少同类大型商业Mall。",
                "采用统一招商运营10年模型：前4年固定回报6%-7%，第5年起租金2:8分成。",
                "开发商强调2/3自持，运营方与业主收益深度绑定。",
                "项目资料记录了2026-02-02宜家撤场事件，并将其解读为全国战略调整而非区域衰退。",
            ],
            "risks": [
                "宜家撤场后短期市场情绪可能影响看铺转化，需要持续验证客流承接。",
                "固定回报与后续分成兑现依赖招商质量和商管执行力，不是无风险收益。",
                "现有结论较多来自项目营销资料，需和最新销控表、租约和客流数据交叉核实。",
            ],
            "next_actions": [
                "补充最近30天招商签约率、空置率和租金实现率，验证回报兑现能力。",
                "核验曹隘站周边近6个月新增竞品和客群迁移，确认‘3公里内无竞品’是否仍成立。",
                "建立按月监控看板：客流、客单、坪效、品牌稳定度、退租率。",
            ],
            "web_keywords": ["乐橙汇", "乐橙荟", "鄞州", "曹隘", "宜家"],
            "source_paths": [
                "src/leo_skills/business/realestate/output/乐橙汇_项目全案营销手册_v3_Refactored.md",
                "src/leo_skills/business/realestate/output/乐橙汇_项目营销实战手册_v2_RealData.md",
                "projects/乐橙荟/乐橙荟商铺项目全案营销手册.md",
            ],
        }
    }

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.capabilities = {
            "research": "research_assistant_skill",
            "web_search": "web_search_skill",
        }

    def can_handle(self, task: str) -> float:
        task_lower = task.lower()
        keyword_matches = sum(1 for kw in self.ACTIVATION_KEYWORDS if kw in task_lower)

        capability_score = 0.0
        if any(kw in task_lower for kw in ["研究", "调研", "research"]):
            capability_score += 0.4
        if any(kw in task_lower for kw in ["分析", "报告", "analysis", "report"]):
            capability_score += 0.3
        if any(kw in task_lower for kw in ["收集", "整理", "搜索", "查找"]):
            capability_score += 0.2

        return min(1.0, 0.3 + keyword_matches * 0.1 + capability_score)

    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        project_context = self._detect_project_context(task)
        research_plan = self._plan_research(task, project_context=project_context, **kwargs)

        results = []
        for step in research_plan:
            results.append(self._execute_research_step(step, project_context=project_context))

        final_result = self._synthesize_results(
            task,
            results,
            project_context=project_context,
            **kwargs,
        )
        self.log_task(task, final_result)
        return final_result

    def _detect_project_context(self, task: str) -> Optional[Dict[str, Any]]:
        task_text = (task or "").strip()
        if not task_text:
            return None

        for canonical_name, profile in self.LOCAL_PROJECT_KB.items():
            for alias in profile.get("aliases", []):
                if alias and alias in task_text:
                    return {
                        "canonical_name": canonical_name,
                        "matched_alias": alias,
                        "profile": profile,
                    }
        return None

    def _plan_research(
        self,
        task: str,
        project_context: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        topic = kwargs.get("topic", task)
        depth = kwargs.get("depth", 2)

        if project_context:
            name = project_context["canonical_name"]
            subtopics = [f"{name} - 项目基本面", f"{name} - 进展风险与验证点"]
        else:
            subtopics = self._break_down_topic(topic, depth)

        steps = []
        for i, subtopic in enumerate(subtopics):
            steps.append(
                {
                    "step": i + 1,
                    "subtopic": subtopic,
                    "params": {"topic": subtopic, "depth": depth},
                }
            )
        return steps

    def _break_down_topic(self, topic: str, depth: int) -> List[str]:
        if depth == 1:
            return [topic]
        if depth == 2:
            return [f"{topic} - 概述", f"{topic} - 详细分析"]
        return [
            f"{topic} - 背景和概述",
            f"{topic} - 当前状态和趋势",
            f"{topic} - 风险与建议",
        ]

    def _build_web_query(
        self,
        step: Dict[str, Any],
        project_context: Optional[Dict[str, Any]],
    ) -> str:
        subtopic = step["subtopic"]
        params = step.get("params", {})
        base_topic = str(params.get("topic") or subtopic).split(" - ")[0].strip()
        step_num = step.get("step", 1)

        if project_context:
            project_name = project_context["canonical_name"]
            if step_num == 1:
                return f"{project_name} 宁波 鄞州 项目 位置 开发商 业态 招商"
            return f"{project_name} 宜家 撤场 进展 风险 回报 2026"

        if step_num == 1:
            return f"{base_topic} 项目 概况 开发商 位置"
        return f"{base_topic} 项目 进展 规划 动态"

    def _execute_research_step(
        self,
        step: Dict[str, Any],
        project_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        subtopic = step["subtopic"]
        params = step.get("params", {})
        web_query = self._build_web_query(step, project_context)

        try:
            web_exec = self.use_skill(
                "web_search_skill",
                "search",
                query=web_query,
                max_results=5,
                language="zh-CN",
            )
            web_payload = self._unwrap_execution_result(web_exec)
            web_hits = self._extract_web_hits(web_payload)[:5]

            assistant_exec = self.use_skill("research_assistant_skill", "research", **params)
            assistant_payload = self._unwrap_execution_result(assistant_exec)

            return {
                "step": step["step"],
                "subtopic": subtopic,
                "success": True,
                "result": {
                    "web_query": web_query,
                    "web_results": web_hits,
                    "assistant_result": assistant_payload,
                },
            }
        except Exception as e:
            return {
                "step": step["step"],
                "subtopic": subtopic,
                "success": False,
                "error": str(e),
            }

    def _unwrap_execution_result(self, payload: Any) -> Any:
        if hasattr(payload, "to_dict"):
            return payload.to_dict()
        if hasattr(payload, "result"):
            return getattr(payload, "result")
        return payload

    def _extract_web_hits(self, payload: Any) -> List[Dict[str, Any]]:
        if not isinstance(payload, dict):
            return []

        direct = payload.get("results")
        if isinstance(direct, list):
            return [x for x in direct if isinstance(x, dict)]

        nested = payload.get("result")
        if isinstance(nested, dict) and isinstance(nested.get("results"), list):
            return [x for x in nested.get("results", []) if isinstance(x, dict)]

        return []

    def _collect_web_hits(self, research_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        collected: List[Dict[str, Any]] = []
        for item in research_content:
            detail = item.get("content")
            if not isinstance(detail, dict):
                continue
            hits = detail.get("web_results", [])
            if not isinstance(hits, list):
                continue
            for hit in hits:
                if isinstance(hit, dict):
                    collected.append(hit)
        return collected

    def _rank_web_hits(
        self,
        hits: List[Dict[str, Any]],
        project_context: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        if not hits:
            return []

        keywords = []
        if project_context:
            keywords = project_context["profile"].get("web_keywords", [])

        ranked: List[Dict[str, Any]] = []
        seen_urls = set()
        for hit in hits:
            url = str(hit.get("url", "")).strip()
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)

            title = str(hit.get("title", ""))
            snippet = str(hit.get("snippet", ""))
            score = 0
            if keywords:
                text_blob = f"{title} {snippet} {url}"
                score = sum(1 for kw in keywords if kw and kw in text_blob)
            ranked.append({**hit, "_score": score})

        ranked.sort(key=lambda x: x.get("_score", 0), reverse=True)
        return ranked

    def _build_structured_summary(
        self,
        task: str,
        research_content: List[Dict[str, Any]],
        project_context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        profile = project_context["profile"] if project_context else {}
        web_hits = self._rank_web_hits(self._collect_web_hits(research_content), project_context)
        high_conf_web_hits = web_hits
        if project_context:
            high_conf_web_hits = [h for h in web_hits if int(h.get("_score", 0)) > 0]

        core_findings: List[str]
        risk_items: List[str]
        action_items: List[str]
        local_sources: List[str]

        if project_context:
            core_findings = profile.get("facts", [])
            risk_items = profile.get("risks", [])
            action_items = profile.get("next_actions", [])
            local_sources = profile.get("source_paths", [])
        else:
            core_findings = []
            for hit in high_conf_web_hits[:4]:
                title = str(hit.get("title", "")).strip()
                if title:
                    core_findings.append(f"公开信息命中：{title}")
            risk_items = ["当前任务未命中本地项目知识库，结论主要来自公开搜索结果。"]
            action_items = ["补充明确项目名称或上传项目资料，以提升结论准确性。"]
            local_sources = []

        evidence_items: List[str] = []
        for hit in high_conf_web_hits[:4]:
            title = str(hit.get("title", "")).strip()
            url = str(hit.get("url", "")).strip()
            if title:
                evidence_items.append(f"{title}" + (f" ({url})" if url else ""))

        if project_context and not high_conf_web_hits:
            risk_items = list(risk_items) + ["联网搜索结果相关性偏低，已降级为以本地项目资料为主。"]

        return {
            "project": project_context["canonical_name"] if project_context else None,
            "matched_alias": project_context.get("matched_alias") if project_context else None,
            "core_findings": core_findings,
            "evidence": evidence_items,
            "risks": risk_items,
            "next_actions": action_items,
            "local_sources": local_sources,
            "web_sources": [
                str(hit.get("url", "")).strip()
                for hit in high_conf_web_hits[:6]
                if str(hit.get("url", "")).strip()
            ],
            "task": task,
        }

    def _synthesize_results(
        self,
        task: str,
        results: List[Dict[str, Any]],
        project_context: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        successful_results = [r for r in results if r.get("success", False)]
        failed_results = [r for r in results if not r.get("success", False)]

        research_content = []
        for result in successful_results:
            content = result.get("result", "")
            if hasattr(content, "to_dict"):
                content = content.to_dict()
            research_content.append({"subtopic": result["subtopic"], "content": content})

        structured = self._build_structured_summary(task, research_content, project_context)
        summary = self._generate_summary(task, structured)

        return {
            "task": task,
            "total_steps": len(results),
            "successful_steps": len(successful_results),
            "failed_steps": len(failed_results),
            "summary": summary,
            "structured_summary": structured,
            "research_content": research_content,
            "errors": [r.get("error") for r in failed_results] if failed_results else [],
        }

    def _generate_summary(self, task: str, structured: Dict[str, Any]) -> str:
        lines: List[str] = [f"任务：{task}"]
        project = structured.get("project")
        alias = structured.get("matched_alias")
        if project:
            lines.append(f"识别项目：{project}" + (f"（别名命中：{alias}）" if alias else ""))
        lines.append("")

        lines.append("核心结论：")
        core_findings = structured.get("core_findings") or []
        if core_findings:
            for idx, finding in enumerate(core_findings[:6], 1):
                lines.append(f"{idx}. {finding}")
        else:
            lines.append("1. 暂无高置信结论。")

        lines.append("")
        lines.append("证据来源：")
        evidence = structured.get("evidence") or []
        if evidence:
            for item in evidence[:4]:
                lines.append(f"- {item}")
        else:
            lines.append("- 当前未抓到高相关公开网页证据。")

        lines.append("")
        lines.append("风险与待核实：")
        risks = structured.get("risks") or []
        for risk in risks[:4]:
            lines.append(f"- {risk}")

        lines.append("")
        lines.append("下一步建议：")
        next_actions = structured.get("next_actions") or []
        for action in next_actions[:4]:
            lines.append(f"- {action}")

        lines.append("")
        lines.append("本地资料：")
        local_sources = structured.get("local_sources") or []
        if local_sources:
            for path in local_sources:
                lines.append(f"- {path}")
        else:
            lines.append("- 无")

        return "\n".join(lines)

    def get_capabilities(self) -> Dict[str, str]:
        return self.capabilities

    def get_help_text(self) -> str:
        return (
            "Research Agent 帮助\n"
            "==================\n\n"
            "能力:\n"
            "1. 信息收集 - research_assistant_skill\n"
            "2. 实时搜索 - web_search_skill\n"
            "3. 本地项目资料优先融合\n"
            "4. 结构化输出（结论/证据/风险/建议）\n"
        )


AgentFactory.register_agent_class("researcher", ResearchAgent)


if __name__ == "__main__":
    config = AgentConfig(
        name="research-agent",
        type="researcher",
        priority=2,
        skills=["research_assistant_skill", "web_search_skill"],
        description="研究代理",
    )
    agent = ResearchAgent(config)
    print(agent.get_help_text())
