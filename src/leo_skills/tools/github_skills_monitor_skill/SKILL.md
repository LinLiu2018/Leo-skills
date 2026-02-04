# GitHub Skills Monitor Skill (GitHub技能监控器)

## 技能描述

实时监控GitHub上的Claude Code Skills、Agents、Workflows，自动检测优质项目并触发加载流程。

## 核心能力

- **实时监控**: 定期扫描指定数据源的更新
- **智能发现**: 检测新的高星项目、热门技能
- **自动分类**: 判断是Skill、Agent还是Workflow
- **触发加载**: 调用 github_to_skills_skill 自动转换
- **去重检测**: 避免重复加载已有技能

## 使用方法

```python
from github_skills_monitor_skill import GitHubSkillsMonitorSkill

skill = GitHubSkillsMonitorSkill()

# 扫描所有数据源
result = skill.execute(
    action="scan_all"
)

# 扫描单个数据源
result = skill.execute(
    action="scan",
    source="awesome-claude-skills"
)

# 检测并加载新技能
result = skill.execute(
    action="detect_and_import",
    min_stars=50  # 最低星标数
)

# 列出监控的数据源
result = skill.execute(action="list_sources")
```

## 监控数据源

| 数据源 | 类型 | URL |
|--------|------|-----|
| anthropics/skills | 官方技能 | github.com/anthropics/skills |
| obra/superpowers | 社区技能库 | github.com/obra/superpowers |
| awesome-claude-skills | 技能汇总 | github.com/travisvn/awesome-claude-skills |
| awesome-claude-code-agents | 代理汇总 | github.com/hesreallyhim/awesome-claude-code-agents |

## 工作逻辑

```
1. 定时扫描 → 2. 获取更新 → 3. 智能分类 → 4. 去重检测 → 5. 自动加载
```

## 配置

参考 `config/config.yaml`
