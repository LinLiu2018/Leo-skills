#!/usr/bin/env python3
"""Scaffold a new skill directory with standard files."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = ROOT / "src" / "leo_skills"


def to_snake_case(name: str) -> str:
    name = name.strip().replace("-", "_").replace(" ", "_")
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    name = re.sub(r"_+", "_", name).strip("_").lower()
    return name


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold(name: str, category: str) -> Path:
    base_name = to_snake_case(name)
    category_name = to_snake_case(category)
    skill_name = base_name if base_name.endswith("_skill") else f"{base_name}_skill"

    target = SKILLS_ROOT / category_name / skill_name
    if target.exists():
        raise FileExistsError(f"目标目录已存在: {target}")

    module_name = skill_name
    class_name = "".join(x.capitalize() for x in skill_name.split("_"))

    write_file(
        target / "SKILL.md",
        f"""---
name: {skill_name}
version: 1.0.0
category: {category_name}
description: {skill_name} capability
triggers:
  - "{base_name}"
  - "{category_name}"
author: Leo Liu
---

# {skill_name}

Skill description.
""",
    )

    write_file(
        target / "__init__.py",
        f'"""Package for {skill_name}."""\n\nfrom .{module_name} import {class_name}\n',
    )

    write_file(
        target / f"{module_name}.py",
        f"""class {class_name}:
    \"\"\"{skill_name} implementation.\"\"\"

    def execute(self, **kwargs):
        return {{"status": "ok", "skill": "{skill_name}", "params": kwargs}}
""",
    )

    write_file(
        target / "config" / "config.yaml",
        f"""skill:
  name: {skill_name}
  version: 1.0.0
  category: {category_name}

execution:
  timeout: 300
  retry: 1
""",
    )

    write_file(
        target / "evolution.json",
        json.dumps(
            {
                "version": "1.0.0",
                "evolution_history": [
                    {"version": "1.0.0", "date": "2026-02-26", "changes": "Initial scaffold"}
                ],
                "learned_tips": [],
                "learned_errors": [],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )

    write_file(
        target / "scripts" / "main.py",
        f"""#!/usr/bin/env python3
from {module_name} import {class_name}


if __name__ == "__main__":
    print({class_name}().execute())
""",
    )

    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a new skill")
    parser.add_argument("--name", required=True, help="Skill name, e.g. weekly_report")
    parser.add_argument("--category", required=True, help="Skill category, e.g. content_creation")
    args = parser.parse_args()

    target = scaffold(args.name, args.category)
    print(f"Created skill scaffold: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

