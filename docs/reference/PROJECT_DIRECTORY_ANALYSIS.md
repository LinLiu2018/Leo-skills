# Leo AI System - 项目目录架构分析报告

> 生成时间: 2026-03-04
> 分析范围: 全项目目录结构
> 总技能数: 247个

---

## 一、项目整体目录结构

```
leo_ai_system/                          # 项目根目录
├── .benchmarks/                        # 性能基准测试数据
├── .claude/                            # Claude Code 配置与技能
│   ├── agents/                         # 子代理定义 (code-reviewer, documenter, researcher)
│   ├── cache/                          # 缓存数据
│   ├── evaluation_results/             # 技能评估结果
│   ├── health/                         # 健康检查报告
│   ├── hooks/                          # 钩子脚本 (memory, tool-start/end)
│   ├── logs/                           # 日志文件
│   ├── memory/                         # 记忆数据 (context, learnings, sessions)
│   ├── plugins/                        # 插件系统 (leo-core)
│   ├── skills/                         # 247个技能目录
│   ├── hooks.json                      # 钩子配置
│   ├── memory.json                     # 记忆索引
│   ├── permissions.md                  # 权限配置
│   ├── session_init.py                 # 会话初始化脚本
│   ├── settings.local.json             # 本地设置
│   └── skill_registry.json             # 技能注册表
├── .cursor-plugin/                     # Cursor 编辑器插件
├── .github/                            # GitHub 配置 (CI/CD, Issue模板)
├── .leo_effects/                       # Leo 特效数据
├── .leo_logs/                          # Leo 系统日志
├── .leo_monitor/                       # Leo 监控数据
├── .leo_snapshots/                     # Leo 系统快照
├── .leo_transactions/                  # Leo 事务记录
├── .mcp/                               # MCP (Model Context Protocol) 配置
├── .openclaw/                          # OpenClaw 工作区状态
├── .pi/                                # PI 配置
├── .playwright-cli/                    # Playwright CLI 配置
├── .playwright-mcp/                    # Playwright MCP 配置
├── .pytest_cache/                      # Pytest 缓存
├── .trash/                             # 回收站
├── .vscode/                            # VSCode 配置
├── config/                             # 系统配置
│   ├── keywords/                       # 关键词配置
│   ├── models/                         # 模型配置
│   └── security/                       # 安全配置
├── data/                               # 数据存储
├── docker/                             # Docker 配置
│   ├── docker-compose.yml              # Docker Compose 配置
│   └── Dockerfile                      # Docker 镜像定义
├── docs/                               # 文档中心
│   ├── assets/                         # 静态资源 (截图、日志)
│   ├── bookmarks/                      # 书签文件
│   ├── guides/                         # 操作指南
│   ├── identity/                       # 身份定义 (HEARTBEAT, SOUL, USER)
│   ├── memory/                         # 记忆日志
│   ├── planning/                       # 任务规划
│   ├── progress/                       # 进度日志
│   ├── reference/                      # 参考文档 (架构、运维手册)
│   └── research/                       # 研究发现
├── examples/                           # 示例项目
│   ├── auto_memory_demo.py             # 自动记忆演示
│   └── demo-dashboard/                 # 演示仪表盘 (React)
├── leo_knowledge/                      # 知识库
│   ├── context/                        # 上下文文件 (QUICK_CONTEXT, user_profile)
│   ├── frameworks/                     # 框架文档
│   ├── memory/auto_storage/            # 自动存储的记忆
│   └── templates/                      # 模板文件
├── leo_wingman/                        # Leo Wingman 模块
│   ├── executor/                       # 执行器 (delivery, pipeline, task_parser)
│   ├── memory/                         # Wingman 记忆
│   └── selfcare/                       # 自我维护 (cleanup, health_check, optimizer)
├── leo-skills-old/                     # 旧技能备份 (空目录)
├── logs/                               # 系统日志
│   ├── feishu/                         # 飞书日志
│   └── repo_watch/                     # 仓库监控日志
├── memory/                             # 自动记忆 (按日期)
├── node_modules/                       # Node.js 依赖
├── output/                             # 输出目录
│   ├── ai_learning_site/               # AI 学习网站输出
│   ├── app/                            # 应用输出
│   ├── book_notes/                     # 读书笔记输出
│   ├── competitor_data/                # 竞品数据
│   ├── delivery/                       # 交付物
│   ├── marketing_docs/                 # 营销文档
│   ├── playwright/                     # Playwright 输出
│   └── reports/                        # 报告输出
├── projects/                           # 项目工作区
│   ├── angel-worm-ai/                  # Angel Worm AI 项目
│   ├── fission/                        # 裂变项目
│   ├── huaian-market/                  # 淮安市场项目
│   ├── jianhua-miniprogram/            # 建华小程序
│   ├── realestate/                     # 房地产项目
│   └── 乐橙荟/                          # 乐橙荟项目
├── reports/                            # 报告中心
│   ├── acceptance/                     # 验收报告
│   ├── integration/                    # 集成测试报告
│   ├── x_platform/                     # X 平台报告
│   └── *.md, *.csv                     # 各类业务报告
├── scripts/                            # 脚本中心
│   ├── business/                       # 业务脚本
│   ├── cron/                           # 定时任务
│   ├── demos/                          # 演示脚本
│   ├── development/                    # 开发脚本
│   ├── maintenance/                    # 维护脚本
│   ├── migration/                      # 迁移脚本
│   ├── openclaw/                       # OpenClaw 运维脚本
│   ├── setup/                          # 安装脚本
│   ├── skills/                         # 技能管理
│   ├── sync/                           # 同步脚本
│   ├── temp/                           # 临时脚本
│   ├── testing/                        # 测试脚本
│   └── utilities/                      # 工具脚本
├── src/                                # 源代码
│   ├── leo_ai_system.egg-info/         # Python 包信息
│   ├── leo_config/                     # 配置管理
│   ├── leo_gateway/                    # 网关模块
│   ├── leo_interface/                  # 接口层
│   └── leo_skills/                     # Leo 技能目录
├── tests/                              # 测试目录
├── webchat/                            # Web 聊天界面 (空目录)
└── 根目录配置文件                       # README, CLAUDE.md, mcp.json 等
```

---

## 二、目录详细说明

### 2.1 核心系统目录

| 目录 | 用途 | 状态 |
|------|------|------|
| `src/leo_gateway/` | 网关核心：消息路由、会话管理、协议处理 | 活跃 |
| `src/leo_config/` | 配置管理：设置、去AI化指南 | 活跃 |
| `src/leo_interface/` | 接口层：CLI、Web、OpenClaw 桥接 | 活跃 |
| `src/leo_skills/` | Leo 技能系统：20+ 技能分类 | 活跃 |
| `.claude/skills/` | Claude 技能：247个技能 | 活跃 |
| `leo_wingman/` | 任务执行与自我维护模块 | 半活跃 |

### 2.2 文档体系

| 目录 | 用途 | 文件数 |
|------|------|--------|
| `docs/guides/` | 操作指南、安装手册 | 20+ |
| `docs/planning/` | 任务规划、架构设计 | 30+ |
| `docs/reference/` | 参考文档、运维手册 | 25+ |
| `docs/progress/` | 进度日志、会话交接 | 10+ |
| `docs/research/` | 研究发现、可行性报告 | 10+ |
| `leo_knowledge/` | 知识库、上下文文件 | 20+ |

### 2.3 脚本体系

| 目录 | 用途 | 脚本数 |
|------|------|--------|
| `scripts/business/` | 业务脚本（房产调研、营销生成） | 9 |
| `scripts/maintenance/` | 维护脚本（健康检查、路径验证） | 20+ |
| `scripts/openclaw/` | OpenClaw 运维脚本 | 20+ |
| `scripts/development/` | 开发脚本（技能创建、验证） | 15+ |
| `scripts/setup/` | 安装配置脚本 | 8 |
| `scripts/testing/` | 测试脚本 | 8 |

---

## 三、问题分析

### 3.1 🔴 空目录/无用目录

| 目录 | 问题 | 建议 |
|------|------|------|
| `leo-skills-old/` | 完全空目录 | **删除** 或归档到 `.trash/` |
| `webchat/` | 空目录 | **删除** 或补充内容 |
| `leo_wingman/memory/interaction_history/` | 仅含 `.gitkeep` | 评估是否需要保留 |
| `.pi/` | 用途不明 | 确认用途或删除 |

### 3.2 🟡 目录重复/功能重叠

| 目录1 | 目录2 | 问题 | 建议 |
|-------|-------|------|------|
| `memory/` | `leo_knowledge/memory/` | 记忆分散在两个位置 | 统一迁移到 `.claude/memory/` |
| `docs/memory/` | `memory/` | 记忆日志分散 | 统一命名规范 |
| `logs/` | `.leo_logs/` | 日志分散 | 合并到 `logs/` |
| `.claude/skills/` | `src/leo_skills/` | 双技能系统 | 明确分工或合并 |
| `data/` | `.leo_*` | 数据分散 | 统一数据目录结构 |

### 3.3 🟠 文件放置不合理

| 文件/目录 | 当前位置 | 问题 | 建议位置 |
|-----------|----------|------|----------|
| `C:Users刘方林.openclawgateway.log` | 根目录 | Windows 路径转义问题 | `logs/openclaw/` |
| `nul` | 根目录 | 空文件，可能是错误创建 | **删除** |
| `package.json` | 根目录 | Node 项目与 Python 项目混合 | 移动到 `src/leo_interface/web_v2/` |
| `node_modules/` | 根目录 | 依赖目录不应在根 | 移动到对应项目目录 |
| `test_fixes.py` | 根目录 | 测试文件应在 tests/ | `tests/test_fixes.py` |
| `IDENTITY.md`, `SOUL.md`, `HEARTBEAT.md` | 根目录 | 重复（docs/identity/ 已有） | **删除** 或统一入口 |
| `USER.md`, `TOOLS.md` | 根目录 | 重复 | 统一使用 `docs/identity/` |

### 3.4 🔵 命名不一致

| 目录/文件 | 当前命名 | 问题 | 建议 |
|-----------|----------|------|------|
| `leo-skills-old/` | kebab-case | 与项目 snake_case 规范不一致 | `leo_skills_old/` |
| `leo_wingman/` | snake_case | 正确 | 保持 |
| `.leo_effects/` | 点前缀 | 隐藏目录，与普通目录混用 | 统一为 `leo_effects/` |
| `.leo_logs/` | 点前缀 | 同上 | 统一为 `logs/leo/` |

---

## 四、最佳实践评估

### 4.1 ✅ 符合最佳实践

| 实践 | 实现情况 | 评分 |
|------|----------|------|
| 文档分层 | docs/guides/, docs/reference/, docs/planning/ 分层清晰 | ⭐⭐⭐⭐⭐ |
| 脚本分类 | 按功能分 business/, maintenance/, setup/ | ⭐⭐⭐⭐⭐ |
| 配置分离 | config/, .env, *.yaml 分离 | ⭐⭐⭐⭐⭐ |
| 项目隔离 | projects/ 下各项目独立 | ⭐⭐⭐⭐⭐ |
| 测试独立 | tests/ 目录集中管理 | ⭐⭐⭐⭐⭐ |
| 知识库 | leo_knowledge/ 独立管理 | ⭐⭐⭐⭐⭐ |

### 4.2 ⚠️ 需要改进

| 实践 | 问题 | 建议 |
|------|------|------|
| 单一职责 | 根目录过于拥挤 | 清理根目录，仅保留入口文件 |
| 隐藏文件规范 | .leo_* 和 普通目录混用 | 统一使用普通目录 |
| 语言一致性 | Python/Node 混合 | 明确各目录的技术栈 |
| 日志集中 | 日志分散在多目录 | 统一 logs/ 目录结构 |
| 记忆管理 | 记忆分散在多位置 | 统一 `.claude/memory/` |

---

## 五、架构优化建议

### 5.1 短期优化（1-2周）

```
1. 清理根目录
   - 删除 nul, leo-skills-old/, webchat/
   - 移动 test_fixes.py 到 tests/
   - 删除重复的 IDENTITY.md, SOUL.md, HEARTBEAT.md

2. 统一命名
   - leo-skills-old/ → .trash/leo_skills_old/
   - .leo_logs/ → logs/leo/
   - .leo_effects/ → data/effects/

3. 修复日志文件
   - 删除/移动 C:Users刘方林.openclawgateway.log
```

### 5.2 中期优化（1个月）

```
1. 统一记忆系统
   - memory/ → .claude/memory/sessions/
   - leo_knowledge/memory/ → .claude/memory/storage/
   - docs/memory/ → .claude/memory/logs/

2. 统一日志系统
   - .leo_logs/ → logs/leo/
   - .leo_monitor/ → logs/monitor/
   - .leo_transactions/ → data/transactions/
   - .leo_snapshots/ → data/snapshots/

3. 清理 Node 依赖
   - 根目录 node_modules/ → src/leo_interface/web_v2/node_modules/
   - 根目录 package.json → src/leo_interface/web_v2/
```

### 5.3 长期规划（3个月）

```
1. 双技能系统整合
   - 评估 .claude/skills/ 和 src/leo_skills/ 的分工
   - 考虑统一技能注册表

2. 数据目录重构
   - data/ 下按业务分类
   - 统一数据库文件位置

3. 配置中心
   - config/ 统一所有配置
   - 支持环境区分 (dev/prod)
```

---

## 六、目录健康评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 结构清晰度 | 85/100 | 整体分层合理，根目录略拥挤 |
| 命名一致性 | 75/100 | 大部分一致，.leo_* 命名需统一 |
| 职责分离 | 80/100 | 功能分离良好，技能系统有重复 |
| 文档完整度 | 90/100 | 文档体系完善，分类清晰 |
| 可维护性 | 78/100 | 空目录和重复文件影响维护 |

**总体评分: 82/100** (良好，有优化空间)

---

## 七、附录：技能分类统计

| 分类 | 数量 | 示例 |
|------|------|------|
| 社交媒体 | 15+ | douyin_skill, xiaohongshu_skill, wechat_skill |
| 电商运营 | 10+ | amazon_skill, aliexpress_skill, shopify_skill |
| 开发工具 | 20+ | github_skill, docker_skill, aws_skill |
| 办公协作 | 15+ | notion_connector_skill, slack_skill, asana_skill |
| 内容创作 | 15+ | article_generator_skill, image_generator_skill |
| 数据分析 | 10+ | analytics_skill, sentiment_analysis_skill |
| 房地产 | 5+ | sales-sop, realestate_listing_skill |
| Superpowers | 14 | brainstorming_skill, writing_plans_skill |

---

*报告生成完成。建议按优先级逐步实施优化方案。*
