# Leo Skills Manifest

**Leo 的 Claude Code 技能清单** - 基于自动发现系统的实时技能索引

---

## 技能总览

| 分类 | 技能数 | 状态 |
|------|--------|------|
| content-creation | 2 | 🟢 活跃 |
| core | 1 | 🟢 活跃 |
| development | 1 | 🟢 活跃 |
| intelligence | 1 | 🟢 活跃 |
| tools | 3 | 🟢 活跃 |
| utilities | 2 | 🟢 活跃 |

**总计**: 10 个活跃技能

---

## 详细清单

### 📁 Content-Creation

#### content_layout_leo_skill
- **路径**: `content-creation/content_layout_leo_skill/`
- **描述**: Skill in content-creation
- **版本**: 1.0.0
- **状态**: 🟢 有效

- **入口点**: `scripts/main.py`

#### realestate_news_publisher_skill
- **路径**: `content-creation/realestate_news_publisher_skill/`
- **描述**: Skill in content-creation
- **版本**: 1.0.0
- **状态**: 🟢 有效

- **入口点**: `scripts/main.py`

### 📁 Core

#### text_generator_skill
- **路径**: `core/text_generator_skill/`
- **描述**: Skill in core
- **版本**: 1.0.0
- **状态**: 🟢 有效

- **入口点**: `scripts/main.py`

### 📁 Development

#### skill_code_generator_skill
- **路径**: `development/skill_code_generator_skill/`
- **描述**: Skill in development
- **版本**: 1.0.0
- **状态**: 🟢 有效

- **入口点**: `scripts/main.py`

### 📁 Intelligence

#### twitter_monitor_skill
- **路径**: `intelligence/twitter_monitor_skill/`
- **描述**: Skill in intelligence
- **版本**: 1.0.0
- **状态**: 🟢 有效

- **入口点**: `scripts/main.py`

### 📁 Tools

#### agent_skill_creator_skill
- **路径**: `tools/agent_skill_creator_skill/`
- **描述**: Skill in tools
- **版本**: 1.0.0
- **状态**: 🟢 有效

- **入口点**: `scripts/main.py`

#### article_to_prototype_skill
- **路径**: `tools/article_to_prototype_skill/`
- **描述**: Skill in tools
- **版本**: 1.0.0
- **状态**: 🟢 有效

- **入口点**: `scripts/main.py`

#### skill_evolution_assistant_skill
- **路径**: `tools/skill_evolution_assistant_skill/`
- **描述**: Skill in tools
- **版本**: 1.0.0
- **状态**: 🟢 有效

- **入口点**: `scripts/main.py`

### 📁 Utilities

#### obsidian_sync_skill
- **路径**: `utilities/obsidian_sync_skill/`
- **描述**: Skill in utilities
- **版本**: 1.0.0
- **状态**: 🟢 有效

- **入口点**: `scripts/main.py`

#### research_assistant_skill
- **路径**: `utilities/research_assistant_skill/`
- **描述**: Skill in utilities
- **版本**: 1.0.0
- **状态**: 🟢 有效

- **入口点**: `scripts/main.py`

---

## 使用指南

### 自动技能管理
```bash
# 更新技能注册表
python scripts/development/manage_skills.py update

# 查看所有技能
python scripts/development/manage_skills.py list

# 搜索技能
python scripts/development/manage_skills.py search --query <关键词>

# 为Claude Code生成技能目录
python scripts/development/manage_skills.py install
```

---

**最后更新**: 2026-01-24 13:15:21
**生成方式**: 技能自动发现系统
**总技能数**: 10

