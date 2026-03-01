# -*- coding: utf-8 -*-
"""
analyze_sessions_skill - DataClaw 驱动的会话分析与知识提取

通过 DataClaw 解析 Claude/Codex/OpenClaw 等多源会话数据，
提取工具使用模式、常见问题、自动化机会，并整合到 Leo 记忆系统。
"""

import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class SessionParser:
    """基于 DataClaw 的多源会话解析器"""

    def __init__(self, project_filter: Optional[str] = None):
        self.project_filter = project_filter
        self._ensure_utf8()

    @staticmethod
    def _ensure_utf8():
        os.environ["PYTHONUTF8"] = "1"

    def discover(self) -> List[Dict]:
        """发现所有可用项目"""
        from dataclaw.parser import discover_projects
        projects = discover_projects()
        if self.project_filter:
            projects = [
                p for p in projects
                if self.project_filter in p.get("dir_name", "")
                or self.project_filter in p.get("display_name", "")
            ]
        return projects

    def parse_sessions(
        self, dir_name: str, source: str = "claude",
        include_thinking: bool = False
    ) -> List[Dict]:
        """解析指定项目的所有会话"""
        from dataclaw.anonymizer import Anonymizer
        from dataclaw.parser import parse_project_sessions
        anon = Anonymizer()
        return parse_project_sessions(
            dir_name, anon,
            include_thinking=include_thinking,
            source=source,
        )


class KnowledgeExtractor:
    """从会话数据中提取可操作知识"""

    def extract_all(self, sessions: List[Dict]) -> Dict[str, Any]:
        """执行全量知识提取"""
        return {
            "tool_patterns": self._extract_tool_patterns(sessions),
            "common_questions": self._extract_questions(sessions),
            "error_patterns": self._extract_errors(sessions),
            "workflow_sequences": self._extract_workflows(sessions),
            "model_usage": self._extract_model_usage(sessions),
            "session_summary": self._summarize_sessions(sessions),
        }

    def _extract_tool_patterns(self, sessions: List[Dict]) -> Dict:
        """提取工具使用模式"""
        tool_counts = Counter()
        tool_sequences = []
        tool_success_rate = defaultdict(lambda: {"success": 0, "fail": 0})

        for session in sessions:
            seq = []
            for msg in session.get("messages", []):
                for tu in msg.get("tool_uses", []):
                    tool = tu.get("tool", "unknown")
                    tool_counts[tool] += 1
                    seq.append(tool)
                    status = tu.get("status", "success")
                    if status == "success":
                        tool_success_rate[tool]["success"] += 1
                    else:
                        tool_success_rate[tool]["fail"] += 1
            if seq:
                tool_sequences.append(seq)

        # 找出常见的工具序列对
        bigrams = Counter()
        for seq in tool_sequences:
            for i in range(len(seq) - 1):
                bigrams[(seq[i], seq[i + 1])] += 1

        top_bigrams = [
            {"from": a, "to": b, "count": c}
            for (a, b), c in bigrams.most_common(15)
        ]

        success_rates = {}
        for tool, counts in tool_success_rate.items():
            total = counts["success"] + counts["fail"]
            success_rates[tool] = {
                "total": total,
                "success_rate": round(counts["success"] / total, 3) if total else 0,
            }

        return {
            "total_tool_calls": sum(tool_counts.values()),
            "tool_frequency": dict(tool_counts.most_common(20)),
            "common_sequences": top_bigrams,
            "success_rates": success_rates,
        }

    def _extract_questions(self, sessions: List[Dict]) -> List[Dict]:
        """提取用户常见问题模式"""
        questions = []
        for session in sessions:
            for msg in session.get("messages", []):
                if msg.get("role") != "user":
                    continue
                content = msg.get("content", "")
                if not isinstance(content, str):
                    continue
                # 检测问句
                if any(content.rstrip().endswith(c) for c in ("?", "？")):
                    questions.append({
                        "question": content[:200],
                        "session_id": session.get("session_id", "")[:12],
                        "timestamp": msg.get("timestamp", ""),
                    })
        return questions[:50]  # 限制数量

    def _extract_errors(self, sessions: List[Dict]) -> List[Dict]:
        """提取错误模式"""
        error_patterns = Counter()
        error_examples = {}
        error_re = re.compile(
            r"(Error|Exception|Traceback|FAILED|error:|failed:)",
            re.IGNORECASE,
        )

        for session in sessions:
            for msg in session.get("messages", []):
                for tu in msg.get("tool_uses", []):
                    output = tu.get("output", {})
                    text = output.get("text", "") if isinstance(output, dict) else str(output)
                    if error_re.search(text):
                        # 提取错误类型
                        lines = text.split("\n")
                        for line in lines:
                            if error_re.search(line):
                                key = line.strip()[:100]
                                error_patterns[key] += 1
                                if key not in error_examples:
                                    error_examples[key] = {
                                        "tool": tu.get("tool", ""),
                                        "session": session.get("session_id", "")[:12],
                                    }
                                break

        return [
            {"pattern": pat, "count": cnt, **error_examples.get(pat, {})}
            for pat, cnt in error_patterns.most_common(20)
        ]

    def _extract_workflows(self, sessions: List[Dict]) -> List[Dict]:
        """提取常见工作流序列"""
        # 提取每个 session 的高层工作流（用户意图 -> 工具序列）
        workflows = []
        for session in sessions:
            msgs = session.get("messages", [])
            current_intent = None
            current_tools = []

            for msg in msgs:
                if msg.get("role") == "user":
                    if current_intent and current_tools:
                        workflows.append({
                            "intent": current_intent[:100],
                            "tools": current_tools[:20],
                            "tool_count": len(current_tools),
                        })
                    content = msg.get("content", "")
                    current_intent = content[:100] if isinstance(content, str) else ""
                    current_tools = []
                else:
                    for tu in msg.get("tool_uses", []):
                        current_tools.append(tu.get("tool", "unknown"))

            if current_intent and current_tools:
                workflows.append({
                    "intent": current_intent[:100],
                    "tools": current_tools[:20],
                    "tool_count": len(current_tools),
                })

        # 按工具数量排序，返回最复杂的工作流
        workflows.sort(key=lambda w: w["tool_count"], reverse=True)
        return workflows[:30]

    def _extract_model_usage(self, sessions: List[Dict]) -> Dict:
        """提取模型使用统计"""
        model_counts = Counter()
        model_tokens = defaultdict(int)
        for session in sessions:
            model = session.get("model", "unknown")
            model_counts[model] += 1
            stats = session.get("stats", {})
            model_tokens[model] += stats.get("input_tokens", 0)
        return {
            "model_frequency": dict(model_counts.most_common()),
            "model_tokens": dict(model_tokens),
        }

    def _summarize_sessions(self, sessions: List[Dict]) -> Dict:
        """生成会话总览"""
        if not sessions:
            return {"total": 0}

        timestamps = []
        total_msgs = 0
        total_tools = 0
        branches = Counter()

        for s in sessions:
            total_msgs += len(s.get("messages", []))
            stats = s.get("stats", {})
            total_tools += stats.get("tool_uses", 0)
            branch = s.get("git_branch", "unknown")
            if branch:
                branches[branch] += 1
            for ts_key in ("start_time", "end_time"):
                ts = s.get(ts_key, "")
                if ts:
                    timestamps.append(ts)

        timestamps.sort()
        return {
            "total_sessions": len(sessions),
            "total_messages": total_msgs,
            "total_tool_calls": total_tools,
            "date_range": {
                "earliest": timestamps[0] if timestamps else None,
                "latest": timestamps[-1] if timestamps else None,
            },
            "branches": dict(branches.most_common(10)),
        }


class MemoryIntegrator:
    """将提取的知识整合到 Leo 记忆系统"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(".")
        self.memory_dir = self.project_root / "leo_knowledge" / "context"
        self.report_dir = self.project_root / ".claude" / "logs"

    def save_report(self, knowledge: Dict[str, Any]) -> Path:
        """保存分析报告"""
        self.report_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.report_dir / "ANALYSIS_REPORT.md"

        summary = knowledge.get("session_summary", {})
        tools = knowledge.get("tool_patterns", {})
        errors = knowledge.get("error_patterns", [])
        models = knowledge.get("model_usage", {})

        lines = [
            "# Session Analysis Report",
            f"\nGenerated: {datetime.now().isoformat()}",
            f"Sessions analyzed: {summary.get('total_sessions', 0)}",
        ]

        dr = summary.get("date_range", {})
        if dr.get("earliest"):
            lines.append(f"Date range: {dr['earliest']} to {dr['latest']}")

        # Tool usage table
        lines.append("\n## Tool Usage")
        lines.append("| Tool | Count | Success Rate |")
        lines.append("|------|-------|-------------|")
        rates = tools.get("success_rates", {})
        for tool, count in tools.get("tool_frequency", {}).items():
            rate = rates.get(tool, {})
            sr = f"{rate.get('success_rate', 0) * 100:.1f}%"
            lines.append(f"| {tool} | {count} | {sr} |")

        # Common sequences
        seqs = tools.get("common_sequences", [])
        if seqs:
            lines.append("\n## Common Tool Sequences")
            for s in seqs[:10]:
                lines.append(f"- {s['from']} → {s['to']} ({s['count']}x)")

        # Error patterns
        if errors:
            lines.append("\n## Error Patterns")
            lines.append("| Pattern | Count | Tool |")
            lines.append("|---------|-------|------|")
            for e in errors[:15]:
                pat = e["pattern"].replace("|", "\\|")
                lines.append(f"| {pat} | {e['count']} | {e.get('tool', '')} |")

        # Model usage
        mf = models.get("model_frequency", {})
        if mf:
            lines.append("\n## Model Usage")
            for model, count in mf.items():
                lines.append(f"- {model}: {count} sessions")

        # Branches
        branches = summary.get("branches", {})
        if branches:
            lines.append("\n## Git Branches")
            for branch, count in branches.items():
                lines.append(f"- {branch}: {count} sessions")

        report_path.write_text("\n".join(lines), encoding="utf-8")
        return report_path

    def update_shared_memory(self, knowledge: Dict[str, Any]) -> Path:
        """更新 shared_memory 中的会话分析摘要"""
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        mem_path = self.memory_dir / "session_insights.md"

        summary = knowledge.get("session_summary", {})
        tools = knowledge.get("tool_patterns", {})

        lines = [
            "# Session Insights (Auto-generated)",
            f"\nLast updated: {datetime.now().isoformat()}",
            f"Based on {summary.get('total_sessions', 0)} sessions",
            "\n## Top Tools",
        ]
        for tool, count in list(tools.get("tool_frequency", {}).items())[:10]:
            lines.append(f"- {tool}: {count}")

        seqs = tools.get("common_sequences", [])
        if seqs:
            lines.append("\n## Common Patterns")
            for s in seqs[:5]:
                lines.append(f"- {s['from']} → {s['to']}")

        errors = knowledge.get("error_patterns", [])
        if errors:
            lines.append("\n## Frequent Errors")
            for e in errors[:5]:
                lines.append(f"- [{e['count']}x] {e['pattern'][:80]}")

        mem_path.write_text("\n".join(lines), encoding="utf-8")
        return mem_path


class AnalyzeSessionsSkill:
    """DataClaw 驱动的会话分析技能"""

    def __init__(self, project_root: Optional[str] = None):
        self.name = "analyze_sessions_skill"
        self.version = "2.0.0"
        self.description = "DataClaw 驱动的会话分析与知识提取"
        self.project_root = Path(project_root) if project_root else Path(".")

    def execute(
        self,
        project_filter: Optional[str] = None,
        source: str = "claude",
        save_report: bool = True,
        update_memory: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        """执行完整的会话分析流程"""
        parser = SessionParser(project_filter=project_filter)

        # 1. 发现项目
        projects = parser.discover()
        if not projects:
            return {"status": "no_projects", "message": "未发现任何会话数据"}

        # 2. 解析会话
        all_sessions = []
        for proj in projects:
            if proj.get("source") == source or source == "all":
                sessions = parser.parse_sessions(
                    proj["dir_name"], source=proj["source"]
                )
                all_sessions.extend(sessions)

        if not all_sessions:
            return {"status": "no_sessions", "message": "未找到匹配的会话"}

        # 3. 提取知识
        extractor = KnowledgeExtractor()
        knowledge = extractor.extract_all(all_sessions)

        # 4. 保存结果
        integrator = MemoryIntegrator(self.project_root)
        result = {
            "status": "completed",
            "sessions_analyzed": len(all_sessions),
            "knowledge": knowledge,
        }

        if save_report:
            report_path = integrator.save_report(knowledge)
            result["report_path"] = str(report_path)

        if update_memory:
            mem_path = integrator.update_shared_memory(knowledge)
            result["memory_path"] = str(mem_path)

        return result


def main():
    """入口函数"""
    return AnalyzeSessionsSkill()


if __name__ == "__main__":
    skill = AnalyzeSessionsSkill(project_root="d:/桌面/leo_ai_system")
    result = skill.execute(project_filter="leo-ai-system", source="claude")
    print(json.dumps(
        {k: v for k, v in result.items() if k != "knowledge"},
        indent=2, ensure_ascii=False,
    ))
    if result.get("knowledge"):
        k = result["knowledge"]
        print(f"\nTool calls: {k['tool_patterns']['total_tool_calls']}")
        print(f"Error patterns: {len(k['error_patterns'])}")
        print(f"Sessions: {k['session_summary']['total_sessions']}")
