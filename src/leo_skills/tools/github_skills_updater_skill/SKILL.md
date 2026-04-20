---
name: github-skills-updater-skill
description: Github Skills Updater Skill 技能。当用户需要相关帮助时使用。 [优化第5轮：提升了触发准确率]
license: MIT
---

# GitHub Skills Updater Skill (GitHub技能自动更新器)

## 技能描述

实时检测已从GitHub加载到Leo AI System的技能/代理/工作流，自动更新到最新版本。

## 核心能力

- **跟踪管理**: 管理所有GitHub来源的技能清单
- **更新检测**: 定期检测这些技能的远程更新
- **自动更新**: 自动拉取最新代码并更新系统
- **变更记录**: 记录更新历史，便于回滚
- **去重更新**: 避免重复更新同一技能

## 使用方法

```python
from github_skills_updater_skill import GitHubSkillsUpdaterSkill

skill = GitHubSkillsUpdaterSkill()

# 检测所有已注册技能的更新
result = skill.execute(action="check_updates")

# 检测并自动更新
result = skill.execute(action="update_all")

# 更新单个技能
result = skill.execute(
    action="update",
    skill_name="superpowers_test_driven_development_skill"
)

# 查看已注册的GitHub技能清单
result = skill.execute(action="list_registered")

# 查看更新历史
result = skill.execute(action="history")
```

## 工作流程

```
1. 获取已注册技能列表 → 2. 检测远程版本 → 3. 比较版本差异 → 4. 自动更新 → 5. 记录历史
```

## 注册来源

以下技能会被自动跟踪：
- `obra/superpowers` 转化的所有技能
- `anthropics/skills` 转化的所有技能
- 其他GitHub项目转化的技能

## 配置

参考 `config/config.yaml`
