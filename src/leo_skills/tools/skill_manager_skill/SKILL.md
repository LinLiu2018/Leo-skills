---
name: skill-manager-skill
description: Skill Manager Skill 技能。当用户需要相关帮助时使用。 [优化第5轮：提升了触发准确率]
license: MIT
---

# Skill Manager Skill (技能生命周期管理器)

## 技能描述

GitHub技能生命周期管理器。审计本地技能、检查远程更新、生成状态报告、自动化升级工作流、列出/删除技能。

## 核心能力

- **技能审计**: 扫描并分析所有本地技能状态
- **更新检查**: 检测远程仓库更新并提醒
- **状态报告**: 生成技能健康度和使用统计
- **自动升级**: 自动化升级工作流
- **技能管理**: 列出、清理、删除技能

## 使用方法

```python
from skill_manager_skill import SkillManagerSkill

skill = SkillManagerSkill(
    skill_name="skill_manager",
    config_path="skill_manager_skill/config/config.yaml"
)

# 审计所有技能
result = skill.execute(action="audit")

# 检查远程更新
result = skill.execute(action="check_updates")

# 生成状态报告
result = skill.execute(action="report")

# 升级指定技能
result = skill.execute(action="upgrade", skill_name="web_search_skill")
```

## 配置文件

参考 `config/config.yaml`

## 进化机制

本技能支持自我进化能力：
- 根据审计经验优化检测逻辑
- 自动学习最佳升级策略
- 持续改进报告格式

## 进化历史

已积累 5 条经验：

1. Audited 0 skills, found 0 issues
2. Audited 16 skills, found 23 issues
3. Generated report: 16 skills analyzed
4. to check git remote status before upgrade operations
5. verify backup exists
