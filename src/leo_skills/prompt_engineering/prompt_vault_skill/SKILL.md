---
name: prompt-vault-skill
description: 提示词库管理技能 - 保存、版本控制、标签分类、搜索和Obsidian同步。当用户需要提示词工程相关帮助时使用。 [优化第5轮：提升了触发准确率]
category: prompt_engineering
triggers:
- 保存prompt
- 保存提示词
- 提示词库
- 管理提示词
- prompt vault
- 导出提示词
actions:
- save
- search
- list
- get
- update
- export_to_obsidian
- import_presets
metadata:
  version: 1.0.0
license: MIT
---

# Prompt Vault Skill - 提示词库管理

## 功能

管理可复用的提示词库，支持版本控制、质量评分、标签分类和 Obsidian 同步。

## 使用场景

- 实操过程中保存有效的提示词
- 搜索和复用历史提示词
- 将提示词导出到 Obsidian 知识库沉淀
- 导入 GitHub 精选预置提示词

## Actions

| 动作 | 说明 | 参数 |
|------|------|------|
| `save` | 保存提示词（自动评分） | title, content, category, framework, tags |
| `search` | 搜索提示词 | query, category, tags |
| `list` | 列出所有提示词 | category, sort_by |
| `get` | 获取单个提示词 | prompt_id |
| `update` | 更新提示词（版本自增） | prompt_id, content, tags |
| `export_to_obsidian` | 导出到 Obsidian | prompt_id 或 all=True |
| `import_presets` | 导入预置提示词 | source |

## 框架支持

- CO-STAR（内容创作）
- RISEN（多步骤流程）
- TIDD-EC（高精度任务）
- chain_of_thought（推理链）
- few_shot（少样本）
- xml_structure（XML结构化）
- custom（自定义）