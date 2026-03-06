# Auto Dispatcher Skill

智能技能分发器。自动识别用户需求，匹配最佳技能/代理/工作流，供用户确认后执行。

**Version:** 1.0.0
**Author:** Leo AI System
**Compatibility:** claude-code, openclaw

---

## What This Skill Does

当你描述一个需求时，自动识别匹配的技能、代理和工作流：

1. **关键词提取** - 从用户输入提取关键意图词
2. **模糊匹配** - 支持同义词、近义词匹配
3. **候选排序** - 按相关性排序候选技能
4. **确认流程** - 生成确认消息，等待用户确认
5. **执行回调** - 用户确认后自动执行

---

## When To Use

### 需求识别场景

```
"帮我分析一下宁波别墅市场"
"写一篇关于房贷计算的文章"
"监控一下抖音账号数据"
"创建一个Python API"
"生成一个项目文档"
```

### 能力查询场景

```
"我需要做市场分析，用什么技能？"
"帮我找一个写文章的技能"
"有哪些代理可以做电商？"
```

---

## How To Use

### 基本调用

```
@Leo 分析宁波别墅市场
```

系统会自动识别并展示候选列表：

```
┌─────────────────────────────────────┐
│ 识别到以下能力，请确认:             │
│                                     │
│ [1] villa_agent (推荐) ⭐          │
│     别墅项目专家                   │
│                                     │
│ [2] market_analysis_skill          │
│     市场分析                       │
│                                     │
│ [3] realestate_agent              │
│     房地产市场分析                 │
│                                     │
│ 请回复数字、"全部执行"或"取消"    │
└─────────────────────────────────────┘
```

### 手动触发

```
/auto_dispatcher
或
@Leo /auto_dispatcher
```

---

## 匹配规则

### 关键词映射

| 关键词 | 匹配技能/代理 |
|--------|---------------|
| 别墅、 villa | villa_agent |
| 住宅、购房 | residential_agent |
| 商业、写字楼 | commercial_agent |
| 法拍、拍卖 | auction_agent |
| 租赁、租 | leasing_agent |
| 贷款、房贷、利率 | loan_agent, mortgage_calculator_skill |
| 电商、亚马逊、shopify | ecommerce_agent, amazon_skill, shopify_skill |
| 文章、写作、文案 | copywriting_skill, article_generator_skill |
| 市场、分析 | market_analysis_skill, analysis_agent |
| 监控、监测 | monitor_skill, video_monitor_skill |
| 开发、代码、API | architect_agent, mobile_agent |
| 测试、验证 | test_driven_development_skill |
| 搜索、研究 | research_agent, research_assistant_skill |
| 内容、排版 | content_layout_leo_skill |
| 翻译 | translate_skill |
| 天气 | weather_skill_skill |

### 权重规则

1. **精确匹配** (权重 100) - 关键词完全匹配技能名称
2. **描述匹配** (权重 80) - 关键词匹配技能描述
3. **分类匹配** (权重 60) - 关键词匹配技能分类
4. **同义词匹配** (权重 40) - 关键词匹配同义词库

---

## 输出格式

### 候选列表格式

```markdown
## 识别结果

**提取关键词**: 宁波, 别墅, 市场分析

### 技能匹配 (3个)

| # | 名称 | 类型 | 匹配度 | 说明 |
|---|------|------|--------|------|
| 1 | villa_agent | 代理 | ⭐⭐⭐ | 别墅项目专家 |
| 2 | market_analysis_skill | 技能 | ⭐⭐ | 市场分析 |
| 3 | realestate_agent | 代理 | ⭐ | 房地产市场分析 |

### 请确认

请回复：
- 数字 (如 "1") - 执行单个
- "全部" - 执行全部
- "取消" - 取消操作
```

---

## 配置

### 关键词词库

技能内置业务关键词库，覆盖：
- 房产业务 (别墅、住宅、商业、法拍、租赁)
- 金融业务 (贷款、房贷、投资)
- 电商业务 (亚马逊、Shopify、速卖通)
- 内容创作 (文章、视频、SEO)
- 开发工具 (API、前端、后端)

### 阈值设置

- **最小匹配度**: 40 (低于40分不显示)
- **最大候选数**: 5 (只显示前5个)
- **自动执行**: 单一匹配时直接执行

---

## Examples

### Example 1: 房产需求

```
用户: "帮我看看宁波的别墅市场"
系统: 识别关键词 [宁波, 别墅, 市场]
匹配:
  1. villa_agent (95分) ⭐
  2. market_analysis_skill (75分)
  3. realestate_agent (60分)
用户: "1"
系统: 执行 villa_agent
```

### Example 2: 电商需求

```
用户: "我想做亚马逊电商"
系统: 识别关键词 [亚马逊, 电商]
匹配:
  1. amazon_skill (95分) ⭐
  2. ecommerce_agent (85分)
  3. copywriting_skill (60分)
用户: "1"
系统: 执行 amazon_skill
```

### Example 3: 单一匹配

```
用户: "帮我计算房贷"
系统: 识别关键词 [房贷, 计算]
匹配:
  1. mortgage_calculator_skill (98分) ⭐⭐
用户: (自动执行，直接输出计算器)
```

---

## Dependencies

- Python 3.8+
- pyyaml
- skill_registry.json (技能注册表)
- agents.yaml (代理配置)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-04 | Initial release |

---

## License

MIT
