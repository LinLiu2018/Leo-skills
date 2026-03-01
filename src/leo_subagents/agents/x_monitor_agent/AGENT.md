# X Monitor Agent - X 平台博主监控代理

## 代理描述

监控 X 平台 (Twitter) 优质博主，追踪每日更新，转化为学习和实战依据。

## 能力范围

- **博主监控**: 追踪指定博主的每日推文
- **内容筛选**: 筛选高质量、有实战价值的内容
- **知识转化**: 将推文转化为学习笔记
- **实战依据**: 生成可执行的行动计划
- **趋势分析**: 分析博主内容趋势和热点

## 触发词

- X 平台监控
- Twitter 监控
- 博主更新
- 向阳乔木
- 优质内容
- 学习转化

## 监控博主清单

| 博主 | 领域 | 优先级 |
|------|------|--------|
| @向阳乔木 | AI 技能/OpenClaw | P0 |
| @openclaw | OpenClaw 官方 | P0 |
| @anthropic | Anthropic 官方 | P1 |
| @github | GitHub 官方 | P1 |
| 其他 AI 博主 | AI/开发 | P2 |

## 依赖的 Skills

- `twitter_monitor_skill` - Twitter/X 监控
- `web_search_skill` - 网络搜索
- `summarize_skill` - 内容总结
- `knowledge_site_creator_skill` - 知识网站创建

## 定时任务

| 任务 | 频率 | 时间 |
|------|------|------|
| 博主更新检查 | 每日 | 8:00, 20:00 |
| 周报生成 | 每周 | 周日 21:00 |
| 月度分析 | 每月 | 1 日 9:00 |

## 绑定模型

- **主模型**: qwen3.5-plus

## 工作空间

`~/.openclaw/workspace-x-monitor`

---

*版本：1.0.0 | 创建时间：2026-02-27*
