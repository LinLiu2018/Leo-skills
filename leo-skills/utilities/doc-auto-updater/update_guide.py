#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档自动更新器 - 自动更新零基础入门指南
运行方式: python update_guide.py
"""

import sys
import io
from pathlib import Path
from datetime import datetime
import yaml

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
GUIDE_PATH = PROJECT_ROOT / "docs" / "guides" / "Leo系统零基础入门指南.md"
CONFIG_PATH = PROJECT_ROOT / "leo-config" / "settings" / "config.yaml"


def load_config():
    """加载主配置文件"""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


def scan_skills(config):
    """从配置扫描技能"""
    skills = []
    categories = {
        "content-creation": "内容创作类",
        "tools": "工具类",
        "utilities": "研究分析类",
        "data-analysis": "数据分析类"
    }

    for skill in config.get('skills', []):
        skills.append({
            "name": skill.get('name', ''),
            "category": categories.get(skill.get('category', ''), '其他'),
            "description": skill.get('metadata', {}).get('description', '')
        })

    return skills


def scan_agents(config):
    """从配置扫描代理"""
    agents = []
    for agent in config.get('agents', []):
        agents.append({
            "name": agent.get('name', ''),
            "type": agent.get('type', ''),
            "description": agent.get('metadata', {}).get('description', '')
        })
    return agents


def scan_workflows(config):
    """从配置扫描工作流"""
    workflows = []
    for name, info in config.get('workflows', {}).items():
        workflows.append({
            "name": name,
            "display_name": info.get('name', name),
            "description": info.get('description', ''),
            "steps": info.get('steps', [])
        })
    return workflows


def generate_guide():
    """生成入门指南"""
    config = load_config()
    skills = scan_skills(config)
    agents = scan_agents(config)
    workflows = scan_workflows(config)

    guide = f"""# Leo AI系统 - 零基础入门指南

**复制粘贴即用 | 不需要懂代码 | 中文激活**

> 本文档自动生成，最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 先搞懂三个概念

| 概念 | 通俗解释 | 类比 |
|------|---------|------|
| **Skills（技能）** | 具体干活的工具 | 公司里的各种软件工具 |
| **Agents（代理）** | 会用工具的员工 | 不同部门的专业员工 |
| **Workflows（工作流）** | 多人协作的流程 | 跨部门协作的SOP |

---

## 一、Skills（技能）- {len(skills)}个工具

"""

    # 按类别分组Skills
    by_category = {}
    for skill in skills:
        cat = skill['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(skill)

    for category, skill_list in by_category.items():
        guide += f"### {category}\n\n"
        for skill in skill_list:
            guide += f"- **{skill['name']}**：{skill['description']}\n"
        guide += "\n"

    guide += f"""---

## 二、Agents（代理）- {len(agents)}个员工

| Agent | 类型 | 说明 |
|-------|------|------|
"""

    for agent in agents:
        guide += f"| {agent['name']} | {agent['type']} | {agent['description']} |\n"

    guide += f"""
### 怎么用Agent？

**自动选择**：直接说需求，系统自动选择
```
分析宁波房地产市场
```

**指定Agent**：
```
用research-agent帮我调研AI眼镜市场
```

---

## 三、Workflows（工作流）- {len(workflows)}条流水线

"""

    for wf in workflows:
        steps_str = " → ".join([s.get('name', '') for s in wf.get('steps', [])])
        guide += f"### {wf['display_name']}（{wf['name']}）\n"
        guide += f"**说明**：{wf['description']}\n"
        guide += f"**流程**：{steps_str}\n"
        guide += f"```\n运行{wf['name']}，主题是xxx\n```\n\n"

    guide += """---

## 四、快速对照表

| 我想... | 说什么 |
|--------|-------|
| 排版文章 | `帮我排版这篇文章` |
| 发布房产资讯 | `帮我发布房产资讯` |
| 生成营销手册 | `生成项目营销手册` |
| 搜索信息 | `搜索xxx` |
| 分析数据 | `分析这组数据` |
| 做完整调研 | `运行research-pipeline，主题是xxx` |
| 写文章并发布 | `运行content-pipeline，主题是xxx` |

---

**记住**：用中文说出你的需求就行！

---

*本文档由 doc-auto-updater 自动生成*
"""

    return guide


def main():
    """主函数"""
    print("正在扫描系统组件...")

    config = load_config()
    skills = scan_skills(config)
    agents = scan_agents(config)
    workflows = scan_workflows(config)

    print(f"发现 {len(skills)} 个Skills")
    print(f"发现 {len(agents)} 个Agents")
    print(f"发现 {len(workflows)} 个Workflows")

    guide = generate_guide()

    GUIDE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(GUIDE_PATH, 'w', encoding='utf-8') as f:
        f.write(guide)

    print(f"✓ 入门指南已更新: {GUIDE_PATH}")


if __name__ == "__main__":
    main()
