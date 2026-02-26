#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
能力索引自动更新脚本
====================
自动扫描并更新 capability_index.md
"""

import os
import re
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


# 能力索引模板
CAPABILITY_INDEX_TEMPLATE = """# Leo AI System - 能力索引

> **自动生成** - {timestamp}
>
> 本文件由 `scripts/update_capability_index.py` 自动生成
> 请勿手动编辑，运行脚本即可更新

---

## 📊 统计概览

| 类型 | 数量 | 描述 |
|------|------|------|
| 🛠️ Skills | {skill_count} | 可执行技能 |
| 🤖 Agents | {agent_count} | 智能代理 |
| 🔄 Workflows | {workflow_count} | 工作流定义 |

**总计**: {total_count} 个能力单元

---

## 🛠️ Skills 索引

{skills_section}

---

## 🤖 Agents 索引

{agents_section}

---

## 🔄 Workflows 索引

{workflows_section}

---

## 📁 快速导航

### 按分类浏览 Skills

{categories_section}

---

## 📝 使用说明

### 通过意图识别调用

系统会根据用户输入自动匹配最合适的技能或代理：

```python
from leo_orchestrator.intent_recognizer import get_intent_recognizer

recognizer = get_intent_recognizer()
match = recognizer.recognize("帮我研究量子计算")

# 返回：IntentMatch(intent_type='agent', target='research_agent', confidence=0.9)
```

### 直接通过 Registry 调用

```python
from leo_orchestrator.registry import get_registry

registry = get_registry()
skill = registry.get_skill('web_search_skill')
agent = registry.get_agent('research_agent')
```

### 执行工作流

```python
from leo_orchestrator.workflow_engine import WorkflowEngine

engine = WorkflowEngine(agents)
result = engine.execute_from_yaml('src/leo_workflows/definitions/content_pipeline.yaml')
```

---

*最后更新: {timestamp}*
"""


def parse_yaml_frontmatter(content: str) -> Optional[Dict]:
    """解析 YAML frontmatter"""
    if not content.startswith('---'):
        return None

    try:
        # 提取 frontmatter
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if match:
            return yaml.safe_load(match.group(1))
    except Exception:
        pass

    return None


def discover_skills(base_path: Path) -> List[Dict]:
    """发现所有 Skills"""
    skills = []

    for skill_md in base_path.rglob("SKILL.md"):
        # 跳过 references/examples
        if 'references' in skill_md.parts or 'examples' in skill_md.parts:
            continue

        try:
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()

            # 尝试解析 YAML frontmatter
            metadata = parse_yaml_frontmatter(content)

            # 从路径推断信息
            parts = skill_md.parts
            category = "unknown"
            if 'leo_skills' in parts:
                idx = parts.index('leo_skills')
                if idx + 1 < len(parts):
                    category = parts[idx + 1]

            skill_info = {
                "name": metadata.get('name', skill_md.parent.name) if metadata else skill_md.parent.name,
                "category": metadata.get('category', category) if metadata else category,
                "description": metadata.get('description', '') if metadata else '',
                "triggers": metadata.get('triggers', []) if metadata else [],
                "version": metadata.get('version', '1.0.0') if metadata else '1.0.0',
                "path": str(skill_md.parent.relative_to(base_path.parent))
            }

            skills.append(skill_info)

        except Exception as e:
            print(f"  ⚠️ 解析 {skill_md} 失败: {e}")

    return sorted(skills, key=lambda x: (x['category'], x['name']))


def discover_agents(base_path: Path) -> List[Dict]:
    """发现所有 Agents"""
    agents = []
    agents_dir = base_path / "src" / "leo_subagents" / "agents"

    if not agents_dir.exists():
        return agents

    for agent_dir in agents_dir.iterdir():
        if not agent_dir.is_dir() or agent_dir.name.startswith('__'):
            continue

        agent_md = agent_dir / "AGENT.md"
        if not agent_md.exists():
            continue

        try:
            with open(agent_md, 'r', encoding='utf-8') as f:
                content = f.read()

            # 尝试解析 YAML frontmatter
            metadata = parse_yaml_frontmatter(content)

            agent_info = {
                "name": metadata.get('name', agent_dir.name) if metadata else agent_dir.name,
                "type": metadata.get('type', 'general') if metadata else 'general',
                "description": metadata.get('description', '') if metadata else '',
                "triggers": metadata.get('triggers', []) if metadata else [],
                "priority": metadata.get('priority', 5) if metadata else 5,
                "skills": metadata.get('skills', []) if metadata else [],
                "path": str(agent_dir.relative_to(base_path))
            }

            agents.append(agent_info)

        except Exception as e:
            print(f"  ⚠️ 解析 {agent_md} 失败: {e}")

    return sorted(agents, key=lambda x: x['priority'])


def discover_workflows(base_path: Path) -> List[Dict]:
    """发现所有 Workflows"""
    workflows = []
    workflows_dir = base_path / "src" / "leo_workflows" / "definitions"

    if not workflows_dir.exists():
        return workflows

    for workflow_yaml in workflows_dir.glob("*.yaml"):
        try:
            with open(workflow_yaml, 'r', encoding='utf-8') as f:
                metadata = yaml.safe_load(f)

            workflow_info = {
                "name": metadata.get('name', workflow_yaml.stem),
                "description": metadata.get('description', ''),
                "version": metadata.get('version', '1.0'),
                "steps_count": len(metadata.get('steps', [])),
                "path": str(workflow_yaml.relative_to(base_path))
            }

            workflows.append(workflow_info)

        except Exception as e:
            print(f"  ⚠️ 解析 {workflow_yaml} 失败: {e}")

    return sorted(workflows, key=lambda x: x['name'])


def generate_skills_section(skills: List[Dict]) -> str:
    """生成 Skills 部分"""
    if not skills:
        return "暂无 Skills"

    lines = []

    # 按分类分组
    by_category = {}
    for skill in skills:
        cat = skill['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(skill)

    for category, cat_skills in sorted(by_category.items()):
        lines.append(f"\n### {category}\n")

        for skill in cat_skills:
            lines.append(f"#### {skill['name']}")
            lines.append(f"- **描述**: {skill['description'] or 'N/A'}")
            if skill['triggers']:
                lines.append(f"- **触发词**: {', '.join(skill['triggers'][:3])}")
            lines.append(f"- **路径**: `{skill['path']}`")
            lines.append('')

    return '\n'.join(lines)


def generate_agents_section(agents: List[Dict]) -> str:
    """生成 Agents 部分"""
    if not agents:
        return "暂无 Agents"

    lines = []

    for agent in agents:
        lines.append(f"\n### {agent['name']}")
        lines.append(f"- **类型**: {agent['type']}")
        lines.append(f"- **描述**: {agent['description'] or 'N/A'}")
        lines.append(f"- **优先级**: {agent['priority']}")
        if agent['triggers']:
            lines.append(f"- **触发词**: {', '.join(agent['triggers'][:5])}")
        if agent['skills']:
            lines.append(f"- **技能**: {', '.join(agent['skills'][:3])}")
        lines.append(f"- **路径**: `{agent['path']}`")
        lines.append('')

    return '\n'.join(lines)


def generate_workflows_section(workflows: List[Dict]) -> str:
    """生成 Workflows 部分"""
    if not workflows:
        return "暂无 Workflows"

    lines = []

    for workflow in workflows:
        lines.append(f"\n### {workflow['name']}")
        lines.append(f"- **描述**: {workflow['description'] or 'N/A'}")
        lines.append(f"- **版本**: {workflow['version']}")
        lines.append(f"- **步骤数**: {workflow['steps_count']}")
        lines.append(f"- **路径**: `{workflow['path']}`")
        lines.append('')

    return '\n'.join(lines)


def generate_categories_section(skills: List[Dict]) -> str:
    """生成分类导航部分"""
    if not skills:
        return "暂无分类"

    categories = {}
    for skill in skills:
        cat = skill['category']
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1

    lines = []
    for cat, count in sorted(categories.items()):
        lines.append(f"- **{cat}**: {count} 个技能")

    return '\n'.join(lines)


def update_capability_index(base_path: Optional[str] = None):
    """更新能力索引"""
    if base_path is None:
        base_path = Path(__file__).parent.parent
    else:
        base_path = Path(base_path)

    print("🔍 扫描 Skills...")
    skills = discover_skills(base_path / "src" / "leo_skills")
    print(f"  发现 {len(skills)} 个 Skills")

    print("🔍 扫描 Agents...")
    agents = discover_agents(base_path)
    print(f"  发现 {len(agents)} 个 Agents")

    print("🔍 扫描 Workflows...")
    workflows = discover_workflows(base_path)
    print(f"  发现 {len(workflows)} 个 Workflows")

    # 生成索引内容
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    content = CAPABILITY_INDEX_TEMPLATE.format(
        timestamp=timestamp,
        skill_count=len(skills),
        agent_count=len(agents),
        workflow_count=len(workflows),
        total_count=len(skills) + len(agents) + len(workflows),
        skills_section=generate_skills_section(skills),
        agents_section=generate_agents_section(agents),
        workflows_section=generate_workflows_section(workflows),
        categories_section=generate_categories_section(skills)
    )

    # 保存索引文件
    index_path = base_path / "leo_knowledge" / "context" / "capability_index.md"
    index_path.parent.mkdir(parents=True, exist_ok=True)

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✅ 能力索引已更新: {index_path}")
    print(f"📊 总计: {len(skills)} Skills, {len(agents)} Agents, {len(workflows)} Workflows")


if __name__ == "__main__":
    import sys

    base_path = sys.argv[1] if len(sys.argv) > 1 else None
    update_capability_index(base_path)
