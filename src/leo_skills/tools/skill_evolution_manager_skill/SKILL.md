# Skill Evolution Manager Skill (技能持续改进管理器)

## 技能描述

基于用户反馈持续改进技能。核心流程：会话回顾→经验提取→持久化到evolution.json→智能缝合到SKILL.md。与现有进化框架深度集成。

## 核心能力

- **会话回顾**: 分析技能使用会话，提取学习点
- **经验提取**: 从用户反馈中识别可复用的经验
- **持久化存储**: 自动保存到evolution.json
- **智能缝合**: 将经验智能合并到SKILL.md
- **批量进化**: 批量处理多个技能的进化

## 使用方法

```python
from skill_evolution_manager_skill import SkillEvolutionManagerSkill

manager = SkillEvolutionManagerSkill(
    skill_name="skill_evolution_manager",
    config_path="skill_evolution_manager_skill/config/config.yaml"
)

# 从会话记录进化
result = manager.execute(
    action="evolve_from_session",
    session_log="path/to/session.log"
)

# 从反馈进化
result = manager.execute(
    action="evolve_from_feedback",
    skill_name="web_search_skill",
    feedback="Add timeout handling for slow requests"
)

# 批量进化所有技能
result = manager.execute(action="batch_evolve")

# 获取进化历史
result = manager.execute(
    action="get_history",
    skill_name="web_search_skill"
)
```

## 与现有框架集成

本技能与 `leo_skills.core.evolution.EvolvableSkill` 深度集成：

1. **读取经验**: 从各技能的 `evolution.json` 读取进化数据
2. **写入经验**: 将新经验写入对应技能的 evolution.json
3. **更新文档**: 自动更新 SKILL.md 的进化部分
4. **分析趋势**: 识别技能进化模式和最佳实践

## 配置文件

参考 `config/config.yaml`

## 协作流程

```
skill_evolution_manager
        ↓
   协调三个技能协作
        ↓
┌───────────────┬───────────────┬───────────────┐
│ github_to_    │  skill_       │  现有进化     │
│ skills        │  manager      │  框架         │
└───────────────┴───────────────┴───────────────┘
        ↓
   创建 → 维护 → 持续进化
```
