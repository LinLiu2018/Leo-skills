# AI 技术情报系统 × Obsidian 知识复利方案

## 核心理念：从信息到知识的转化

```
Twitter 推文 → 技术提取 → 结构化笔记 → 知识图谱 → 持续复利
```

## 一、Obsidian 集成架构

### 1.1 数据流设计

```
┌─────────────────────────────────────────────────────────┐
│                  技术情报工作流                          │
└─────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
  ┌──────────┐   ┌──────────┐   ┌──────────┐
  │ 推文采集  │   │ 技术提取  │   │ 知识沉淀  │
  └──────────┘   └──────────┘   └──────────┘
        │               │               │
        └───────────────┼───────────────┘
                        ▼
              ┌──────────────────┐
              │  Obsidian Vault  │
              └──────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
  ┌──────────┐   ┌──────────┐   ┌──────────┐
  │ 日记笔记  │   │ 技术卡片  │   │ 知识图谱  │
  └──────────┘   └──────────┘   └──────────┘
```

### 1.2 Obsidian 目录结构

```
Obsidian Vault/
├── 00-Inbox/                    # 收件箱（待处理）
│   └── 2026-01-23-tweets.md
├── 01-Daily/                    # 日记（每日情报）
│   └── 2026-01-23.md
├── 02-Tech/                     # 技术卡片
│   ├── AI-Models/
│   │   ├── Claude-Opus-4.5.md
│   │   └── GPT-4.md
│   ├── Frameworks/
│   │   ├── LangChain.md
│   │   └── LlamaIndex.md
│   └── Tools/
│       ├── Cursor.md
│       └── GitHub-Copilot.md
├── 03-People/                   # 人物卡片
│   ├── Andrej-Karpathy.md
│   └── Yann-LeCun.md
├── 04-Reports/                  # 定期报告
│   ├── Weekly/
│   │   └── 2026-W04.md
│   └── Monthly/
│       └── 2026-01.md
└── 05-MOC/                      # 地图笔记（Map of Content）
    ├── AI-Technology-Map.md
    └── Learning-Path.md
```

## 二、核心功能设计

### 2.1 每日技术情报笔记

**模板**：`templates/daily-tech-intelligence.md`

```markdown
---
date: {{date}}
tags: [tech-intelligence, daily, ai]
aliases: [{{date}}-AI情报]
---

# {{date}} AI 技术情报

## 📊 今日概览

- 采集推文：{{tweet_count}} 条
- 识别技术：{{tech_count}} 个
- 重点关注：{{highlight_count}} 项

## 🔥 重点技术

{{#each highlights}}
### [[{{name}}]]

**来源**：[@{{author}}]({{tweet_url}})
**分类**：{{category}}
**描述**：{{description}}

**为什么重要**：
{{why_important}}

**相关技术**：{{#each related}}[[{{this}}]]{{/each}}

---
{{/each}}

## 📝 全部技术

{{#each technologies}}
- [[{{name}}]] - {{description}} (来源：[@{{author}}]({{tweet_url}}))
{{/each}}

## 🔗 相关笔记

- [[{{yesterday}}]] ← 昨日情报
- [[{{tomorrow}}]] → 明日情报
- [[2026-W04]] ← 本周汇总
- [[AI-Technology-Map]] ← 技术地图

## 💡 思考与行动

### 值得深入研究
- [ ] {{action_item_1}}
- [ ] {{action_item_2}}

### 可以尝试的项目
- [ ] {{project_idea_1}}
- [ ] {{project_idea_2}}

---

*由 AI 技术情报系统自动生成*
*最后更新：{{timestamp}}*
```

### 2.2 技术卡片笔记

**模板**：`templates/tech-card.md`

```markdown
---
title: {{tech_name}}
category: {{category}}
tags: [tech, {{category}}, ai]
first_seen: {{first_seen_date}}
last_updated: {{last_updated}}
status: {{status}}  # learning/using/mastered
priority: {{priority}}  # 1-10
---

# {{tech_name}}

## 📌 基本信息

- **分类**：{{category}}
- **官网**：{{official_url}}
- **文档**：{{docs_url}}
- **GitHub**：{{github_url}}
- **首次发现**：{{first_seen_date}}

## 📝 技术描述

{{description}}

## 🎯 核心特性

{{#each features}}
- {{this}}
{{/each}}

## 💡 使用场景

{{#each use_cases}}
### {{title}}
{{description}}
{{/each}}

## 🔗 相关技术

{{#each related_techs}}
- [[{{this}}]]
{{/each}}

## 📚 学习资源

{{#each resources}}
- [{{title}}]({{url}})
{{/each}}

## 🚀 实践项目

{{#each projects}}
- [ ] {{this}}
{{/each}}

## 📊 发展历程

{{#each timeline}}
- **{{date}}**：{{event}}
{{/each}}

## 💬 社区讨论

{{#each discussions}}
### {{date}} - [@{{author}}]({{url}})
{{content}}
{{/each}}

## 🤔 个人思考

{{personal_notes}}

---

*首次创建：{{created_at}}*
*最后更新：{{updated_at}}*
```

### 2.3 周报/月报模板

**模板**：`templates/weekly-report.md`

```markdown
---
title: {{year}}-W{{week}} AI 技术周报
date: {{week_start}} to {{week_end}}
tags: [tech-intelligence, weekly, ai]
---

# {{year}}-W{{week}} AI 技术周报

> {{week_start}} - {{week_end}}

## 📊 本周数据

- 采集推文：{{total_tweets}} 条
- 识别技术：{{total_techs}} 个
- 新增技术：{{new_techs}} 个
- 活跃博主：{{active_bloggers}} 人

## 🔥 本周热点

{{#each hot_topics}}
### {{rank}}. [[{{name}}]]

**热度指数**：{{heat_score}}
**讨论次数**：{{mention_count}}
**关键观点**：
{{key_points}}

**代表推文**：
{{#each tweets}}
- [@{{author}}]({{url}})：{{content}}
{{/each}}

---
{{/each}}

## 🆕 新技术发现

{{#each new_technologies}}
### [[{{name}}]]

**分类**：{{category}}
**首次发现**：{{first_seen}}
**描述**：{{description}}

**值得关注的原因**：
{{why_notable}}

---
{{/each}}

## 👥 活跃博主

{{#each active_bloggers}}
- **[@{{username}}]({{profile_url}})** - {{tweet_count}} 条推文
  - 主要话题：{{topics}}
{{/each}}

## 📈 技术趋势

### 上升趋势
{{#each rising_trends}}
- [[{{name}}]] ↑ {{growth}}%
{{/each}}

### 持续热门
{{#each hot_trends}}
- [[{{name}}]] 🔥 {{heat_score}}
{{/each}}

## 💡 本周洞察

{{insights}}

## 🎯 下周关注

{{#each next_week_focus}}
- [ ] {{this}}
{{/each}}

## 🔗 相关笔记

- [[{{prev_week}}]] ← 上周
- [[{{next_week}}]] → 下周
- [[{{month}}]] ← 本月汇总
- [[AI-Technology-Map]] ← 技术地图

---

*自动生成时间：{{generated_at}}*
```

## 三、实现方案

### 3.1 创建 obsidian-sync-cskill

**核心功能**：
1. **写入日记**：每日技术情报自动写入 Daily 笔记
2. **创建技术卡片**：为新技术自动创建卡片
3. **更新技术卡片**：为已有技术添加新的讨论
4. **生成周报/月报**：定期汇总技术趋势
5. **维护知识图谱**：自动创建双向链接

**关键特性**：
- 支持 YAML frontmatter
- 自动创建双向链接 `[[技术名称]]`
- 支持标签系统 `#tech #ai`
- 模板引擎（Jinja2）
- 增量更新（不覆盖手动编辑）

### 3.2 工作流集成

**tech-intelligence-pipeline 增强**：

```yaml
steps:
  # ... 前面的步骤 ...

  # 步骤7：同步到 Obsidian（新增）
  - name: "obsidian_sync"
    description: "同步到 Obsidian 知识库"
    agent: "task-agent"
    skill: "obsidian-sync-cskill"
    action: "sync_daily"
    params:
      technologies: "{{ steps.tech_filtering.result }}"
      tweets: "{{ steps.twitter_monitoring.result }}"
      vault_path: "~/Documents/Obsidian/AI-Intelligence"
      template: "daily-tech-intelligence"

  # 步骤8：更新技术卡片
  - name: "update_tech_cards"
    agent: "task-agent"
    skill: "obsidian-sync-cskill"
    action: "update_cards"
    params:
      technologies: "{{ steps.tech_filtering.result }}"
      vault_path: "~/Documents/Obsidian/AI-Intelligence"

  # 步骤9：生成周报（条件执行：每周日）
  - name: "generate_weekly_report"
    agent: "task-agent"
    skill: "obsidian-sync-cskill"
    action: "generate_weekly"
    condition: "{{ is_sunday }}"
    params:
      vault_path: "~/Documents/Obsidian/AI-Intelligence"
```

## 四、知识复利的关键机制

### 4.1 渐进式知识积累

```
第1天：发现新技术 → 创建技术卡片
第2天：看到相关讨论 → 更新卡片
第7天：生成周报 → 识别趋势
第30天：生成月报 → 形成洞察
第90天：回顾复盘 → 指导实践
```

### 4.2 知识关联网络

**自动创建双向链接**：
- 技术之间的关联：`[[LangChain]]` ↔ `[[Claude]]`
- 技术与人物的关联：`[[Andrej Karpathy]]` → `[[GPT]]`
- 技术与项目的关联：`[[Cursor]]` → `[[我的AI项目]]`

### 4.3 定期回顾机制

**自动生成回顾提醒**：
```markdown
## 📅 回顾提醒

- [ ] 本周学到了什么新技术？
- [ ] 哪些技术值得深入研究？
- [ ] 有哪些可以应用到实际项目？
- [ ] 需要调整学习方向吗？
```

## 五、实施步骤

### 第一步：创建 obsidian-sync-cskill

```bash
# 目录结构
leo_skills/utilities/obsidian-sync-cskill/
├── scripts/
│   ├── main.py              # 主入口
│   ├── writers/
│   │   ├── daily_writer.py  # 日记写入
│   │   ├── card_writer.py   # 卡片写入
│   │   └── report_writer.py # 报告生成
│   ├── templates/
│   │   ├── daily-tech-intelligence.md
│   │   ├── tech-card.md
│   │   └── weekly-report.md
│   └── utils/
│       ├── markdown_utils.py
│       └── link_utils.py
├── config/
│   └── config.yaml
├── SKILL.md
└── requirements.txt
```

### 第二步：配置 Obsidian Vault

```yaml
# config/config.yaml
obsidian:
  vault_path: "~/Documents/Obsidian/AI-Intelligence"

  directories:
    inbox: "00-Inbox"
    daily: "01-Daily"
    tech: "02-Tech"
    people: "03-People"
    reports: "04-Reports"
    moc: "05-MOC"

  templates:
    daily: "templates/daily-tech-intelligence.md"
    tech_card: "templates/tech-card.md"
    weekly: "templates/weekly-report.md"

  auto_link: true
  auto_tag: true
  backup_before_write: true
```

### 第三步：集成到工作流

修改 `tech-intelligence-pipeline` 添加 Obsidian 同步步骤。

### 第四步：设置定时任务

```python
# 每天 8:30 同步到 Obsidian
scheduler.add_job(
    sync_to_obsidian,
    trigger='cron',
    hour='8',
    minute='30'
)

# 每周日生成周报
scheduler.add_job(
    generate_weekly_report,
    trigger='cron',
    day_of_week='sun',
    hour='20',
    minute='0'
)
```

## 六、知识复利效果

### 短期（1-4 周）
- ✅ 每日技术情报自动归档
- ✅ 技术卡片持续积累
- ✅ 形成技术学习习惯

### 中期（1-3 月）
- ✅ 技术知识图谱初步形成
- ✅ 识别技术发展趋势
- ✅ 指导学习和项目方向

### 长期（3-12 月）
- ✅ 建立完整的技术知识体系
- ✅ 形成独特的技术洞察
- ✅ 提升技术决策能力

## 七、下一步行动

您希望我：

1. **立即实现 obsidian-sync-cskill**？
   - 创建完整的 Obsidian 同步技能
   - 包含所有模板和功能

2. **先完成 tech-extractor-cskill**？
   - 先实现技术提取功能
   - 再集成 Obsidian

3. **创建一个简化版 MVP**？
   - 只实现核心功能（日记 + 技术卡片）
   - 快速验证可行性

请告诉我您的选择，我会立即开始实现！

---

*方案设计时间：2026-01-23*
