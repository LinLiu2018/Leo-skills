#!/usr/bin/env python3
"""Detect potentially duplicated skills by keyword similarity."""

from __future__ import annotations

import re
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import List, Set

import yaml


ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = ROOT / "src" / "leo_skills"
SIMILARITY_THRESHOLD = 0.7


@dataclass
class SkillMeta:
    name: str
    path: Path
    tokens: Set[str]


def tokenize(text: str) -> Set[str]:
    tokens = set(re.findall(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]+", text.lower()))
    return {t for t in tokens if len(t) > 1}


def parse_skill(skill_md: Path) -> SkillMeta | None:
    content = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", content, flags=re.S)
    if not match:
        return None

    data = yaml.safe_load(match.group(1)) or {}
    name = data.get("name", skill_md.parent.name)
    description = str(data.get("description", ""))
    keywords = data.get("activation_keywords") or data.get("triggers") or []
    if isinstance(keywords, str):
        keywords = [keywords]

    text = " ".join([name, description, " ".join(map(str, keywords))])
    tokens = tokenize(text)
    return SkillMeta(name=name, path=skill_md, tokens=tokens)


def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def main() -> int:
    if not SKILLS_ROOT.exists():
        print(f"Skills目录不存在: {SKILLS_ROOT}")
        return 1

    metas: List[SkillMeta] = []
    for md in SKILLS_ROOT.rglob("SKILL.md"):
        parsed = parse_skill(md)
        if parsed:
            metas.append(parsed)

    warnings = []
    for left, right in combinations(metas, 2):
        score = jaccard(left.tokens, right.tokens)
        if score >= SIMILARITY_THRESHOLD:
            warnings.append((score, left, right))

    warnings.sort(key=lambda x: x[0], reverse=True)

    print(f"已扫描技能: {len(metas)}")
    print(f"重复报警阈值: {SIMILARITY_THRESHOLD:.2f}")
    if not warnings:
        print("未发现高相似技能对")
        return 0

    print(f"发现疑似重复: {len(warnings)} 组")
    for score, left, right in warnings:
        print(
            f"⚠️ {left.name} <-> {right.name} | 相似度={score:.2f} "
            f"| {left.path} | {right.path}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

