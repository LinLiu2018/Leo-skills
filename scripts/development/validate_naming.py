#!/usr/bin/env python3
"""Validate naming conventions for skills, agents, and workflows."""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple


ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = ROOT / "src" / "leo_skills"
AGENTS_ROOT = ROOT / "src" / "leo_subagents"
WORKFLOWS_ROOT = ROOT / "src" / "leo_workflows"
EXCLUDE_PATTERNS = {
    "stock-analyzer-cskill",  # 第三方参考示例
    "agents",  # leo_subagents 结构性目录
}


def invalid_reason(name: str, required_suffix: str) -> List[str]:
    reasons: List[str] = []
    if "-" in name:
        reasons.append("包含连字符")
    if " " in name:
        reasons.append("包含空格")
    if name and name[0].isupper():
        reasons.append("以大写字母开头")
    if not name.endswith(required_suffix):
        reasons.append(f"未以 {required_suffix} 结尾")
    return reasons


def collect_skill_dirs() -> List[Path]:
    dirs: List[Path] = []
    if not SKILLS_ROOT.exists():
        return dirs
    for md in SKILLS_ROOT.rglob("SKILL.md"):
        dirs.append(md.parent)
    return sorted({d for d in dirs if d.name not in EXCLUDE_PATTERNS})


def collect_agent_dirs() -> List[Path]:
    dirs: List[Path] = []
    if not AGENTS_ROOT.exists():
        return dirs
    for md in AGENTS_ROOT.rglob("AGENT.md"):
        dirs.append(md.parent)
    for py in AGENTS_ROOT.rglob("*_agent.py"):
        dirs.append(py.parent)
    return sorted({d for d in dirs if d.name not in EXCLUDE_PATTERNS})


def collect_workflow_dirs() -> List[Path]:
    dirs: List[Path] = []
    if not WORKFLOWS_ROOT.exists():
        return dirs
    for wf in WORKFLOWS_ROOT.rglob("workflow.yaml"):
        dirs.append(wf.parent)
    for py in WORKFLOWS_ROOT.rglob("*_pipeline.py"):
        dirs.append(py.parent)
    return sorted({d for d in dirs if d.name not in EXCLUDE_PATTERNS})


def validate(items: List[Path], suffix: str) -> Tuple[int, int]:
    passed = 0
    failed = 0
    for item in items:
        name = item.name
        reasons = invalid_reason(name, suffix)
        if reasons:
            failed += 1
            print(f"[FAIL] 违规: {name} ({'，'.join(reasons)})")
        else:
            passed += 1
            print(f"[PASS] 通过: {name}")
    return passed, failed


def main() -> int:
    skill_dirs = collect_skill_dirs()
    agent_dirs = collect_agent_dirs()
    workflow_dirs = collect_workflow_dirs()

    print("=== Skills ===")
    _, skill_failed = validate(skill_dirs, "_skill")
    print("=== Agents ===")
    _, agent_failed = validate(agent_dirs, "_agent")
    print("=== Workflows ===")
    _, workflow_failed = validate(workflow_dirs, "_pipeline")

    total_failed = skill_failed + agent_failed + workflow_failed
    print(
        f"总计: {len(skill_dirs)} 个技能, {len(agent_dirs)} 个代理, {len(workflow_dirs)} 个工作流"
    )
    print(f"违规: {total_failed} 个")
    return 1 if total_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
