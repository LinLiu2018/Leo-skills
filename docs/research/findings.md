# 发现与决策: Claude Code + OpenClaw + Leo System 集成

> **最后更新**: 2026-02-28
> **官方仓库**: https://github.com/openclaw/openclaw

---

## 2026-02-28 行业调研：个人 AI 助手系统 & Claude Code 技能系统最佳实践

### 一、Claude Code Skills/Agents 最佳实践（2025-2026）

#### 1.1 CLAUDE.md 最佳实践（官方推荐）

来源：[Claude Code 官方最佳实践](https://code.claude.com/docs/en/best-practices)

核心原则：**CLAUDE.md 必须精简，只放 Claude 无法从代码推断的信息**。

| 应该放 | 不应该放 |
|--------|----------|
| Claude 猜不到的 Bash 命令 | Claude 读代码就能知道的东西 |
| 与默认不同的代码风格规则 | 标准语言规范 |
| 测试指令和首选测试运行器 | 详细 API 文档（改为链接） |
| 仓库规范（分支命名、PR 约定） | 经常变化的信息 |
| 项目特有的架构决策 | 长篇教程 |
| 开发环境怪癖（必需的环境变量） | 逐文件的代码库描述 |
| 常见陷阱或非显而易见的行为 | "写干净代码"之类的废话 |

关键警告：
- **CLAUDE.md 太长 = Claude 忽略你的指令**。如果 Claude 反复违反某条规则，说明文件太长，规则被淹没了
- 把 CLAUDE.md 当代码维护：定期审查、修剪、测试
- 用 `@path/to/import` 语法引用其他文件，而不是把所有内容塞进 CLAUDE.md
- 领域知识和偶尔用到的工作流应该放 Skills（按需加载），不要放 CLAUDE.md

#### 1.2 Skills 架构最佳实践

来源：[Claude Skills 架构指南](https://www.mmntm.net/articles/claude-code-skills)、[Claude Skills 可控性问题](https://paddo.dev/blog/claude-skills-controllability-problem/)

SKILL.md 标准结构：
```markdown
---
name: skill-name
description: 一句话描述
disable-model-invocation: true  # 有副作用的工作流必须手动触发
---
# 技能标题
具体指令...
```

关键模式：
- **Skills = 按需加载的领域知识**，不占用每次会话的上下文
- **Subagents = 隔离的执行环境**，有独立上下文窗口，不污染主对话
- **Hooks = 确定性保证**，不像 CLAUDE.md 是"建议性"的，Hooks 是"强制性"的
- **Plugins = 社区打包的技能+工具+钩子集合**

可控性问题（paddo.dev 分析）：
- Skills 的激活是概率性的，不是确定性的
- 解决方案：用 `disable-model-invocation: true` + 手动 `/skill-name` 调用
- 复杂工作流应该拆分为多个小 Skills，而不是一个巨大的 SKILL.md

#### 1.3 Subagents 最佳实践

```markdown
.claude/agents/security-reviewer.md
---
name: security-reviewer
description: Reviews code for security vulnerabilities
tools: Read, Grep, Glob, Bash
model: opus
---
```

- Subagents 在独立上下文中运行，不消耗主对话的上下文窗口
- 适合：代码审查、安全扫描、大规模代码库探索
- 模式：Writer/Reviewer 双会话模式（一个写代码，一个审查）

#### 1.4 上下文管理最佳实践

- **上下文窗口是最重要的资源**，性能随上下文填满而下降
- 不相关任务之间用 `/clear` 重置
- 纠正 Claude 超过 2 次 → `/clear` + 写更好的初始提示
- 用 Subagents 做调研，避免主对话被文件内容填满
- 用 `/compact <指令>` 自定义压缩行为

### 二、OpenClaw 最佳实践

#### 2.1 成本优化（97% 降本方案）

来源：[OpenClaw 成本优化](https://bitrebels.com/technology/openclaw-cost-cut-97-with-five-practical-fixes-that-save-thousands/)、[LinkedIn 97% 降本](https://www.linkedin.com/pulse/slashing-openclaw-api-costs-97-rod-rivera-tgt0e)

5 个关键优化：
1. **精简 System Prompt**：移除冗余指令，减少每次请求的 token 消耗
2. **使用更便宜的模型做简单任务**：路由层判断任务复杂度，简单任务用小模型
3. **缓存频繁查询**：对重复问题使用本地缓存
4. **限制上下文长度**：设置 `maxContextTokens` 避免无限增长
5. **批量处理**：合并多个小请求为一个大请求

#### 2.2 Agent 配置最佳实践

来源：[OpenClaw Agent 指南](https://o-mega.ai/articles/openclaw-creating-the-ai-agent-workforce-ultimate-guide-2026)

- 每个 Agent 应该有明确的职责边界
- System Prompt 要简洁、具体、可测试
- 使用 `customInstructions` 而不是在 System Prompt 中塞所有内容
- 定时任务用 `openclaw cron add`，不要在配置文件中手写

#### 2.3 OpenClaw vs 竞品

来源：[OpenClaw vs Memu.bot](https://ai.plainenglish.io/the-era-of-local-autonomous-agents-a-comprehensive-comparative-analysis-of-openclaw-and-memu-bot-963d4f4bee92)

| 维度 | OpenClaw | Memu.bot | Nanobot |
|------|----------|----------|---------|
| Stars | 223K+ | 15K+ | 8K+ |
| 定位 | 通用个人 AI 助手 | 记忆增强 AI 助手 | 轻量级 AI Agent |
| 多渠道 | 12+ 平台 | 5 平台 | 3 平台 |
| 插件生态 | 丰富 (ClawdHub) | 中等 | 较少 |
| 成本控制 | 需要优化 | 内置优化 | 低成本 |
| 记忆系统 | 基础 | 核心优势 | 无 |

### 三、开源 AI Agent 框架对比（2026）

来源：[框架对比](https://dev.to/pockit_tools/langgraph-vs-crewai-vs-autogen-the-complete-multi-agent-ai-orchestration-guide-for-2026-2d63)、[Firecrawl 框架评测](https://www.firecrawl.dev/blog/best-open-source-agent-frameworks)

#### 3.1 主流框架对比

| 框架 | Stars | 核心优势 | 适用场景 | 学习曲线 |
|------|-------|---------|---------|---------|
| **LangGraph** | 12K+ | 状态图编排、精细控制 | 复杂多步骤工作流 | 高 |
| **CrewAI** | 25K+ | 角色扮演、简单易用 | 多 Agent 协作 | 低 |
| **AutoGen** (微软) | 40K+ | 对话驱动、企业级 | 企业多 Agent 系统 | 中 |
| **OpenAI Agents SDK** | 30K+ | 官方支持、Swarm 模式 | OpenAI 生态 | 低 |
| **Claude Agent SDK** | 新 | Anthropic 官方 | Claude 生态 | 低 |
| **Mastra** | 8K+ | TypeScript 原生 | 前端/全栈开发者 | 中 |
| **Agno** | 20K+ | 极速、模型无关 | 高性能场景 | 中 |

#### 3.2 架构模式趋势

来源：[Vellum AI 工作流指南](https://www.vellum.ai/blog/agentic-workflows-emerging-architectures-and-design-patterns)

2026 年主流架构模式：
1. **Router Pattern**：意图识别 → 路由到专业 Agent
2. **Orchestrator-Worker**：编排器分配任务，Worker 并行执行
3. **Evaluator-Optimizer**：生成 → 评估 → 优化循环
4. **Tool-Use Agent**：Agent 自主选择和调用工具
5. **Multi-Agent Debate**：多个 Agent 辩论得出最优方案

### 四、AI 技能商业化案例

#### 4.1 AI Skills Marketplace 概念

来源：[BuildAloud AI Skills Marketplace](https://buildaloud.ai/blog/2026-02-21-the-brainstorm-an-ai-skills-marketplace/)

商业模式设想：
- **技能市场**：开发者创建 Skills，用户付费使用
- **订阅制**：按月/年订阅技能包
- **按次计费**：每次调用收费
- **企业定制**：为企业定制专属技能

#### 4.2 已有的技能生态

来源：[Awesome Claude Skills](https://awesomeclaude.ai/awesome-claude-skills)、[LobeHub Skills](https://lobehub.com/zh/skills/openclaw-skills-skillzmarket)

最受欢迎的技能类别：
1. **代码生成/审查** - 开发者刚需
2. **内容创作** - 营销/写作自动化
3. **数据分析** - 商业智能
4. **项目管理** - 任务规划/进度跟踪
5. **安全审计** - 代码安全扫描

#### 4.3 商业化路径

来源：[5 种 AI 技能变现方式](https://medium.com/@neurominimal/5-practical-ways-engineers-are-monetizing-ai-skills-in-2026-b0b8367ed789)

1. **AI 自动化咨询**：帮企业搭建 AI 工作流（$150-300/小时）
2. **AI 技能包销售**：打包行业专属技能出售
3. **SaaS 产品**：基于 AI 技能构建垂直 SaaS
4. **培训/课程**：教别人如何构建 AI 系统
5. **开源 + 增值服务**：核心开源，高级功能收费

### 五、代码质量和项目结构最佳实践

#### 5.1 Python AI 项目结构

来源：[Python 项目结构指南](https://www.youtube.com/watch?v=b-LJ1xzIo8Q)、[AI Agent 架构](https://www.gocodeo.com/post/building-ai-agents-with-python-tools-frameworks-and-architecture)

推荐结构：
```
project/
├── src/                    # 源代码
│   ├── agents/             # Agent 定义
│   ├── skills/             # 技能实现
│   ├── orchestrator/       # 编排层
│   ├── memory/             # 记忆系统
│   └── interfaces/         # 接口层
├── tests/                  # 测试
├── docs/                   # 文档
├── scripts/                # 脚本
├── pyproject.toml          # 项目配置（替代 setup.py）
└── CLAUDE.md               # AI 上下文
```

#### 5.2 Monorepo 最佳实践

- 使用 `pyproject.toml` 统一管理依赖
- 每个模块有独立的 `__init__.py` 和 `README.md`
- 共享代码放 `src/common/` 或 `src/core/`
- 测试镜像源代码结构
- CI/CD 只构建变更的模块

---

## 六、综合分析：Leo System 的定位与差距

### 6.1 当前最强的同类系统

| 排名 | 系统 | 做对了什么 |
|------|------|-----------|
| 1 | **OpenClaw + Claude Code** | 生态整合最好，多渠道+编程能力+插件市场 |
| 2 | **CrewAI** | 多 Agent 协作最简单，角色扮演模式直觉化 |
| 3 | **LangGraph** | 状态管理最精细，适合复杂工作流 |
| 4 | **AutoGen** | 企业级最成熟，微软背书 |
| 5 | **Memu.bot** | 记忆系统最强，长期对话体验最好 |

### 6.2 Leo System 与它们的差距

| 差距维度 | 具体问题 | 严重程度 |
|---------|---------|---------|
| **CLAUDE.md 过于臃肿** | 当前 CLAUDE.md 超过 400 行，包含运维日志、故障案例等应该放 Skills 的内容 | 高 |
| **Skills 数量多但质量参差** | 98 个 Skills 中很多是脚手架生成的模板，缺乏实际验证 | 高 |
| **缺乏测试覆盖** | 几乎没有自动化测试，无法验证 Skills 是否正常工作 | 高 |
| **上下文工程未落地** | planning_with_files 方法论写了但实际使用率低 | 中 |
| **OpenClaw 集成脆弱** | 频繁出现网关崩溃、配置错误、认证冲突 | 中 |
| **缺乏成本控制** | 没有 token 使用监控和优化机制 | 中 |
| **没有社区/生态** | 纯个人项目，没有外部贡献者或用户 | 低（当前阶段） |

### 6.3 最有商业价值的方向

按可行性和市场需求排序：

| 优先级 | 方向 | 预期价值 | 实施难度 |
|--------|------|---------|---------|
| P0 | **房产行业 AI 自动化咨询** | 直接变现，$200+/小时 | 低（已有技能基础） |
| P0 | **Claude Code Skills 包** | 打包 Leo 的最佳 Skills 发布到社区 | 低（已有内容） |
| P1 | **AI 工作流搭建培训** | 课程/咨询收入 | 中 |
| P1 | **垂直行业 SaaS** | 基于 Leo 技能构建房产/电商 SaaS | 高 |
| P2 | **开源社区建设** | 长期品牌价值 | 中 |
| P2 | **AI Skills Marketplace** | 平台收入 | 高 |

### 6.4 下一步行动建议

1. **精简 CLAUDE.md**：从 400+ 行压缩到 100 行以内，运维日志移到 Skills
2. **质量优先于数量**：从 98 个 Skills 中筛选 20 个核心 Skills，补充测试
3. **OpenClaw 成本优化**：实施 5 步降本方案，预计降低 80%+ token 消耗
4. **打包发布 Skills**：选 5-10 个最佳 Skills 发布到 awesome-claude-skills
5. **房产 AI 咨询产品化**：将房产相关技能打包为可交付的咨询方案

## 需求
- 通过飞书聊天机器人访问Leo AI System
- 支持自然语言交互调用Skills/Agents/Workflows
- 支持定时任务自动运转
- 实现7x24小时自动化运营

---

## 🔥 最新研究: Claude Code vs OpenClaw vs Leo System 架构对比 (2026-02-04)

### 一、系统概览

| 维度 | Claude Code | OpenClaw | Leo System |
|------|-------------|----------|------------|
| **定位** | Anthropic 官方 AI 编程工具 | 开源多渠道 AI 代理框架 | 个人 AI 智能体系统 |
| **核心能力** | 代码编辑、调试、理解 | 多平台消息路由、任务执行 | 业务自动化、内容创作 |
| **部署方式** | CLI/IDE 插件/Web | 本地自托管 (Docker) | 本地 Python 服务 |
| **开源状态** | 闭源 (Anthropic 产品) | 开源 (GitHub) | 私有项目 |

### 二、架构对比

#### 2.1 Claude Code 架构
```
┌─────────────────────────────────────────────────────────┐
│                    Claude Code                          │
├─────────────────────────────────────────────────────────┤
│  入口层: CLI | VSCode | JetBrains | Slack | Web        │
├─────────────────────────────────────────────────────────┤
│  工具层: Read | Write | Edit | Bash | Glob | Grep      │
├─────────────────────────────────────────────────────────┤
│  扩展层: MCP Tools (外部集成)                           │
├─────────────────────────────────────────────────────────┤
│  上下文层: CLAUDE.md | settings.json | Subagents       │
├─────────────────────────────────────────────────────────┤
│  技能层: .claude/skills/*.md (Markdown 定义)           │
└─────────────────────────────────────────────────────────┘
```

#### 2.2 OpenClaw 架构
```
┌─────────────────────────────────────────────────────────┐
│                    OpenClaw                             │
├─────────────────────────────────────────────────────────┤
│  渠道层: 飞书|WhatsApp|Telegram|Discord|Slack|微信     │
├─────────────────────────────────────────────────────────┤
│  Gateway: WebSocket 控制平面 (ws://127.0.0.1:18789)    │
├─────────────────────────────────────────────────────────┤
│  Brain: 模型无关 (Claude/GPT/Llama/本地模型)           │
├─────────────────────────────────────────────────────────┤
│  Sandbox: Docker 隔离执行环境                          │
├─────────────────────────────────────────────────────────┤
│  Skills: JS/TS 函数 + ClawdHub 技能市场                │
└─────────────────────────────────────────────────────────┘
```

#### 2.3 Leo System 架构
```
┌─────────────────────────────────────────────────────────┐
│                    Leo AI System                        │
├─────────────────────────────────────────────────────────┤
│  入口层: Claude Code | OpenClaw (飞书) | MCP Server    │
├─────────────────────────────────────────────────────────┤
│  编排层: Leo Orchestrator (意图识别+任务路由)          │
├─────────────────────────────────────────────────────────┤
│  代理层: 9 个 Agents (研究/房产/创作/分析/架构...)     │
├─────────────────────────────────────────────────────────┤
│  技能层: 98 个 Skills (13 大分类)                      │
├─────────────────────────────────────────────────────────┤
│  工作流层: 5 个 Workflows (内容/房产/分析/研究/电商)   │
├─────────────────────────────────────────────────────────┤
│  知识层: leo_knowledge (用户画像/开发规范/框架模板)    │
└─────────────────────────────────────────────────────────┘
```

### 三、核心能力对比

| 能力维度 | Claude Code | OpenClaw | Leo System |
|---------|-------------|----------|------------|
| **代码编辑** | ⭐⭐⭐⭐⭐ 原生支持 | ⭐⭐ 通过 Sandbox | ⭐⭐⭐ 通过 Claude Code |
| **多渠道消息** | ⭐⭐ Slack 集成 | ⭐⭐⭐⭐⭐ 12+ 平台 | ⭐⭐⭐ 飞书 (通过 OpenClaw) |
| **技能系统** | ⭐⭐⭐ Markdown 定义 | ⭐⭐⭐⭐ JS/TS + 市场 | ⭐⭐⭐⭐⭐ 98 个 Python 技能 |
| **代理系统** | ⭐⭐⭐ Subagents | ⭐⭐ 单一 Brain | ⭐⭐⭐⭐⭐ 9 个专业代理 |
| **工作流** | ⭐⭐ 手动编排 | ⭐⭐⭐ Lobster 管道 | ⭐⭐⭐⭐ 5 个自动化流水线 |
| **上下文管理** | ⭐⭐⭐⭐ 分层配置 | ⭐⭐⭐ 本地持久化 | ⭐⭐⭐⭐⭐ 五层记忆架构 |
| **MCP 支持** | ⭐⭐⭐⭐⭐ 原生支持 | ⭐⭐⭐ 可集成 | ⭐⭐⭐⭐ MCP Server 暴露 |
| **业务定制** | ⭐⭐ 通用工具 | ⭐⭐⭐ 可扩展 | ⭐⭐⭐⭐⭐ 房产/电商/内容 |

### 四、知识管理对比

| 维度 | Claude Code | OpenClaw | Leo System |
|------|-------------|----------|------------|
| **记忆机制** | CLAUDE.md 项目记忆 | 本地文件持久化 | 五层记忆架构 |
| **用户画像** | 无 | 无 | user_profile.md |
| **开发规范** | 项目级 settings | 无 | development_guide.md |
| **框架模板** | 无 | 无 | frameworks/ + templates/ |
| **上下文工程** | 基础支持 | 无 | planning_with_files 方法论 |

### 五、Leo System 独特优势

#### 5.1 业务深度定制
- **房产经纪**: realestate_agent + 市场调研工作流
- **内容创作**: creative_agent + 内容流水线 (8 步自动化)
- **AI 眼镜电商**: ecommerce_agent + 电商工作流

#### 5.2 上下文工程方法论
```
Context Window = RAM (易失、有限)
Filesystem = Disk (持久、无限)
```
- `docs/planning/task_plan.md` - 任务规划
- `docs/research/findings.md` - 研究发现
- `docs/progress/progress.md` - 进度日志

#### 5.3 三层能力体系
```
Skills (98) → 原子能力
    ↓
Agents (9) → 专业执行者
    ↓
Workflows (5) → 自动化流水线
```

#### 5.4 统一 MCP 暴露
通过 `.mcp/leo_mcp_server.py`，所有能力可被 Claude Code 和 OpenClaw 共享调用。

### 六、系统协作关系图

```
┌─────────────────────────────────────────────────────────┐
│                    用户交互层                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ VSCode IDE  │  │  飞书消息   │  │  终端 CLI   │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
└─────────┼────────────────┼────────────────┼────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────┐  ┌─────────────┐  ┌─────────────────┐
│   Claude Code   │  │  OpenClaw   │  │   直接调用      │
│   (编程助手)    │  │  (消息路由) │  │   (Python)      │
└────────┬────────┘  └──────┬──────┘  └────────┬────────┘
         │                  │                   │
         └──────────────────┼───────────────────┘
                            │ MCP Protocol
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  Leo AI System                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Leo MCP Server                      │   │
│  │         (.mcp/leo_mcp_server.py)                │   │
│  └─────────────────────┬───────────────────────────┘   │
│                        │                                │
│  ┌─────────────────────▼───────────────────────────┐   │
│  │              Leo Orchestrator                    │   │
│  │           (意图识别 + 任务路由)                  │   │
│  └─────────────────────┬───────────────────────────┘   │
│           ┌────────────┼────────────┐                  │
│           ▼            ▼            ▼                  │
│  ┌─────────────┐ ┌──────────┐ ┌──────────────┐        │
│  │ Skills (98) │ │Agents (9)│ │Workflows (5) │        │
│  └─────────────┘ └──────────┘ └──────────────┘        │
└─────────────────────────────────────────────────────────┘
```

### 七、总结与建议

#### 7.1 当前状态评估

| 系统 | 成熟度 | 适用场景 |
|------|--------|----------|
| **Claude Code** | 生产级 | 日常编程、代码审查、调试 |
| **OpenClaw** | 生产级 | 多渠道消息、飞书机器人 |
| **Leo System** | 开发中 | 业务自动化、内容创作、房产分析 |

#### 7.2 Leo System 改进建议

1. **完善 MCP Server**: 确保所有 98 个 Skills 都能正确暴露
2. **增强 Orchestrator**: 提升意图识别准确率
3. **云端部署**: 将 OpenClaw Gateway 迁移到 Vultr 提高稳定性
4. **技能进化**: 利用 evolution 系统持续优化技能表现

#### 7.3 三系统协同价值

- **Claude Code**: 提供强大的编程能力和 MCP 协议支持
- **OpenClaw**: 提供多渠道消息路由和飞书集成
- **Leo System**: 提供业务定制能力和领域知识

三者结合实现了 **"一人 = 10亿级公司生产力"** 的愿景基础设施。

### 八、参考资源

- [Claude Code 官方页面](https://claude.com/product/claude-code)
- [Claude Code Cheatsheet](https://shipyard.build/blog/claude-code-cheat-sheet/)
- [OpenClaw 架构介绍](https://macaron.im/en/blog/what-is-openclaw)
- [OpenClaw 开发者指南](https://aimlapi.com/blog/openclaw-a-practical-guide-to-local-ai-agents-for-developers)
- [OpenClaw 2026.2.2 发布](https://blockchain.news/ainews/openclaw-2026-2-2-release-feishu-integration-security-hardening-and-faster-builds-latest-ai-chat-client-advances)

---

## 历史研究发现

### OpenClaw 核心能力 (2026-01)
- **Gateway控制平面**: WebSocket网络，统一管理所有渠道
- **多渠道支持**: 12+平台（包含飞书原生支持）
- **技能平台**: 支持bundled、managed、workspace三种技能类型
- **定时任务**: 内置Cron作业支持
- **安全模型**: DM配对策略、沙箱隔离

### 飞书集成
- **连接方式**: WebSocket长连接（推荐）
- **消息支持**: 私聊、群聊、@mention触发
- **媒体处理**: 图片、文件、PDF（入站+出站）
- **渲染模式**: auto/raw/card三种
- **配置方式**: `channels.feishu` 内置支持

### Planning-with-files方法论
- **核心理念**: Context Window = RAM, Filesystem = Disk
- **三文件模式**: task_plan.md + findings.md + progress.md
- **关键规则**: 2-动作规则、3-Strike错误协议、5问题重启测试
- **价值**: 解决AI代理的上下文丢失、目标漂移问题

### 技术决策
| 决策 | 理由 |
|------|------|
| 采用 OpenClaw 作为中间层 | 统一多渠道、内置定时任务、技能管理 |
| 使用内置飞书支持 | 官方支持，稳定可靠 |
| 命令行方式集成Leo System | 快速验证，Python与Node.js解耦 |
| 将planning_with_files升级为核心技能 | 提升整个系统的上下文工程能力 |

### 三层架构
```
用户层: 飞书/微信/Telegram → 自然语言交互
编排层: OpenClaw Gateway → 技能管理、定时任务、多渠道路由
能力层: Leo System → Skills/Agents/Workflows
```

### 资源
- OpenClaw官网: https://www.openclaw.dev/
- OpenClaw GitHub: https://github.com/openclaw/openclaw
- Planning-with-files: https://github.com/OthmanAdi/planning-with-files
- 飞书开放平台: https://open.feishu.cn/
- obra/superpowers: https://github.com/obra/superpowers (TDD/调试/协作技能库)

---

*每2次查看/浏览/搜索操作后更新此文件*

---

## 2026-02-28 OpenClaw 最佳实践深度调研

### 一、OpenClaw 推荐架构与配置最佳实践

#### 1.1 四层网关架构（Gateway Architecture）

OpenClaw 采用以 Gateway 为核心的 Hub-and-Spoke 架构，分为四层：

```
┌─────────────────────────────────────────────────────┐
│  1. Channel Layer (渠道层)                           │
│     飞书 | WhatsApp | Telegram | Discord | Slack     │
├─────────────────────────────────────────────────────┤
│  2. Gateway Layer (网关层)                            │
│     WebSocket 控制平面 + 会话管理 + 消息调度           │
│     Lane Queue 可靠性队列                             │
├─────────────────────────────────────────────────────┤
│  3. Agent Core (智能核心)                             │
│     意图解析 + 行动规划 + 记忆管理 + 推理编排          │
├─────────────────────────────────────────────────────┤
│  4. Execution Layer (执行层)                          │
│     OS 交互 + 文件操作 + 命令执行 + 沙箱环境           │
└─────────────────────────────────────────────────────┘
```

关键设计原则：
- **Lane Queue 系统**：确保消息处理稳定性，防止崩溃丢消息
- **会话隔离**：per-channel-peer 模式，每个用户在每个渠道有独立会话
- **模型层可插拔**：支持动态注册 LLM（Anthropic/OpenAI/Gemini/本地模型）

#### 1.2 配置最佳实践

| 配置项 | 推荐做法 | 反模式 |
|--------|---------|--------|
| API Keys | 存环境变量，不要放配置文件 | 硬编码在 .json/.yaml 中 |
| 网关绑定 | `gateway.bind: "loopback"` 仅本地监听 | 直接暴露到公网 |
| 模型配置 | 同一家族 2-3 个模型（如全用 Anthropic） | 混用太多不同家族模型 |
| 技能目录 | `skills.load.extraDirs` 配置额外技能路径 | 所有技能堆在一个目录 |
| 权限控制 | 最小权限原则，禁用不需要的工具 | 保留默认全开权限 |
| 端口安全 | 防火墙限制 18789 和 18791 | 向公网暴露这些端口 |

#### 1.3 成本优化最佳实践

1. **精简 System Prompt**：移除冗余指令，减少每次请求的 token 消耗
2. **模型路由**：简单任务用小模型，复杂任务用大模型
3. **缓存频繁查询**：对重复问题使用本地缓存
4. **限制上下文长度**：设置 `maxContextTokens` 避免无限增长
5. **批量处理**：合并多个小请求为一个大请求

### 二、插件/技能开发最佳模式

#### 2.1 Tools vs Skills 的区别

| 概念 | 定义 | 类比 |
|------|------|------|
| **Tools（工具）** | 定义 OpenClaw "能做什么"，是核心能力 | 器官 |
| **Skills（技能）** | 教 OpenClaw "怎么组合工具来完成任务" | 教科书 |

Tools 示例：`read`、`write`、`exec`、`web_search`、`web_fetch`、`browser`
Skills 示例：`daily-standup-generator`、`code-review`、`web-search`

**关键理解**：安装 Skill 不会授予新权限，Skill 只是利用已启用的 Tools 的操作指南。

#### 2.2 SKILL.md 标准结构

```markdown
---
name: daily-standup-generator
description: 从记忆文件生成每日站会摘要
metadata:
  openclaw:
    primaryEnv:
      - OPENCLAW_MEMORY_PATH
---
## Purpose
从记忆文件生成每日站会摘要

## Steps
1. 读取 memory/episodic/YYYY-MM-DD.md（今天和昨天）
2. 提取：已完成项、受阻项、计划项
3. 格式化为站会更新
4. 保存到 memory/standups/YYYY-MM-DD.md
5. 如果渠道可用，发送摘要

## Example Output
**昨天：**
- 部署了 dashboard v2.1
- 修复了心跳循环的内存泄漏
**今天：**
- 发布邮件引擎 v2
- 审查广告表现
**阻碍：**
- GCP 账单暂停，需要更新付款方式
```

#### 2.3 技能开发最佳实践

1. **命名规范**：小写字母 + 数字 + 连字符，64 字符以内，动词开头
2. **描述简洁**：metadata 简短且具描述性，确保可靠触发
3. **指令精炼**：使用简洁的程序化指令，大型参考材料放单独文件
4. **手动触发**：有副作用的工作流用 `disable-model-invocation: true`
5. **拆分粒度**：复杂工作流拆分为多个小 Skills，不要做一个巨大的 SKILL.md

#### 2.4 技能加载优先级

```
workspace skills (最高优先级)
  ↓
managed/local skills (~/.openclaw/skills)
  ↓
bundled skills (最低优先级，随安装包附带)
```

#### 2.5 自修改技能（Self-modifying Skills）

OpenClaw 的独特功能：Agent 可以观察用户模式，识别重复工作流，然后自动编写或编辑 SKILL.md 文件。这些自创技能跨会话和系统重启持久保存。

### 三、飞书/Lark 渠道集成最佳方式

#### 3.1 推荐配置流程

**方法一：引导向导（推荐新用户）**
```bash
openclaw onboard
# 跟随引导创建飞书应用、配置凭证、启动网关
```

**方法二：CLI 手动配置**
```bash
# 安装飞书插件
openclaw plugins install @openclaw/feishu

# 添加渠道
openclaw channels add
# 选择 Feishu → 输入 App ID 和 App Secret
```

#### 3.2 飞书应用配置要点

| 步骤 | 操作 | 注意事项 |
|------|------|---------|
| 1. 创建应用 | 飞书开放平台 → 创建企业应用 | 记录 App ID 和 App Secret |
| 2. 配置权限 | 添加消息相关权限 | 按需授权，不要过度 |
| 3. 启用机器人 | 开启 Bot 能力 | 必须步骤 |
| 4. 事件订阅 | 配置消息事件 → WebSocket 长连接 | 不需要公网 webhook |
| 5. 发布应用 | 提交审核发布 | 发布后才能生效 |

#### 3.3 飞书集成架构

```
飞书用户 → 飞书云 → WebSocket → bridge.mjs → Gateway → AI Agent
```

关键优势：
- **WebSocket 长连接**：无需公网 webhook URL，无需 ngrok
- **SDK 外连**：飞书 SDK 主动连接外部，不需要入站端口或公网 IP
- **会话映射**：每个飞书聊天自动映射到一个 OpenClaw 会话

#### 3.4 飞书集成注意事项

- feishu 是 **Channel**（渠道），不是 **Plugin**（插件），不要放在 `plugins.entries` 中
- 配置位于 `channels.feishu`
- 运行 `openclaw doctor --fix` 后必须检查是否被误修改
- 2026.2.3 版本中直接消息的"新话题"功能可能缺失

### 四、生产环境部署关键注意事项

#### 4.1 安全部署清单（CVE-2026-25253 教训）

**严重漏洞回顾**：CVE-2026-25253（CVSS 8.8），1-Click RCE Kill Chain
- 影响：2026.1.29 之前版本，Control UI 解析 URL 中的 `gatewayUrl` 参数自动建立 WebSocket 连接并发送认证 token
- 修复：升级到 2026.1.29+

**部署安全清单**：

| 优先级 | 检查项 | 具体操作 |
|--------|--------|---------|
| P0 | 版本更新 | 升级到 2026.1.29+ |
| P0 | Token 轮换 | 轮换所有认证 token 和 API key |
| P0 | 网络隔离 | 防火墙限制 18789/18791 端口 |
| P0 | 本地绑定 | `gateway.bind: "loopback"` |
| P1 | 最小权限 | 禁用 "god mode"，限制 Agent 权限 |
| P1 | 日志监控 | 监控异常 WebSocket 连接 |
| P1 | URL 校验 | 验证所有 `gatewayUrl` 参数 |
| P2 | 沙箱隔离 | 使用 Docker 容器运行 |
| P2 | 密钥管理 | 使用密钥管理器，不硬编码 |
| P2 | 用户教育 | 避免点击可疑链接 |

#### 4.2 SIEM 监控规则

需要配置的告警规则：
- WebSocket 连接到非本地/非审批域名
- 网关配置变更无对应本地认证事件
- Bearer token 在首次出现后 5 秒内从外部 IP 使用
- 应用日志中的 WebSocket 外连尝试

#### 4.3 生产环境推荐部署方式

| 部署方式 | 适用场景 | 风险等级 |
|---------|---------|---------|
| Docker + 硬化配置 | 开发者自托管 | 中 |
| 托管服务（如 xCloud） | 非技术用户 | 低 |
| VPS + Cloudflare Tunnel | 远程访问需求 | 中 |
| 本地 + Tailscale | 个人使用 | 低 |

#### 4.4 稳定性保障

- **Watchdog 脚本**：定期 ping 网关健康端点，无响应时自动重启
- **Anti-loop 规则**：在 AGENTS.md 或 SOUL.md 中设置防循环规则
  - 同一错误失败 2 次后停止
  - 限制连续工具调用次数
  - 检测到重复动作时停止
- **内存管理**：MEMORY.md 超过 2KB 时修剪，日常笔记用日期文件

### 五、记忆管理最佳实践

#### 5.1 Markdown 记忆架构

| 文件 | 用途 | 最佳实践 |
|------|------|---------|
| `MEMORY.md` | 持久化关键事实和偏好 | 保持小而结构化，不是垃圾桶 |
| `SOUL.md` | Agent 的"宪法"，不可变规则 | 极少修改，定义不可做的事 |
| `memory/YYYY-MM-DD.md` | 日常笔记和会话日志 | 按日期分文件 |
| `memory/standups/` | 站会摘要 | 技能自动生成 |

#### 5.2 记忆安全规则

- **不要自动写身份文件**：SOUL.md 不应被 Agent 自动修改
- **防止记忆投毒**：不可信内容不应直接改变身份文件
- **管理记忆生命周期**：未管理的记忆会变成技术债务
- **语义搜索**：可对 MEMORY.md 和日志文件建立向量索引

### 六、OpenClaw vs Memu.bot 对比分析

| 维度 | OpenClaw | Memu.bot |
|------|----------|----------|
| **定位** | "God-mode" 万能工具 | "最聪明" 主动助手 |
| **架构** | Hub-and-Spoke Gateway | 本地优先 + 知识图谱 |
| **记忆** | 上下文窗口填充（昂贵） | 本地知识图谱（真正长期记忆） |
| **成本** | 高（$300-750/月常规使用） | 低（上下文优化） |
| **执行力** | 极强（系统命令+应用构建） | 较弱 |
| **易用性** | 需要中级开发技能 | 相对容易 |
| **安全** | 全系统访问，技能市场风险 | 本地运行，隐私优先 |
| **社区** | 223K+ Stars，活跃社区 | 15K+ Stars，增长中 |
| **渠道** | 12+ 平台 | 5 平台 |

**结论**：
- 需要强执行力和丰富生态 → 选 OpenClaw
- 需要智能记忆和成本控制 → 选 Memu.bot
- Leo System 的策略：用 OpenClaw 做多渠道路由，借鉴 Memu.bot 的记忆理念

### 七、常见反模式和应避免的做法

#### 7.1 安全反模式

| 反模式 | 风险 | 正确做法 |
|--------|------|---------|
| API Key 放配置文件 | 密钥泄露 | 用环境变量 + .env + gitignore |
| 保留默认权限 | 过度暴露 | 逐个启用需要的权限 |
| 不设速率限制 | 一个 bug 打爆 API | 设请求限制+并发限制+执行超时 |
| 开发/生产共享 Key | 互相影响 | 分开的 Key，定期轮换 |
| 不用沙箱 | 系统被完全攻破 | Docker 容器隔离 |
| 直接暴露到公网 | 远程攻击 | Cloudflare Tunnel 或 Tailscale |

#### 7.2 配置反模式

| 反模式 | 后果 | 正确做法 |
|--------|------|---------|
| 一次配置所有功能 | 难以排查问题 | 逐个安装测试 |
| 混用太多模型 | 输出不可预测 | 同家族 2-3 个模型 |
| GUI 配置模型 | 可能不生效 | 在配置文件中设置 |
| Channel 当 Plugin | 启动报错 | 分清 Channel vs Plugin |
| 依赖 `doctor --fix` | 自动修复可能破坏配置 | 修复后手动检查 |

#### 7.3 运营反模式

| 反模式 | 后果 | 正确做法 |
|--------|------|---------|
| 指令太模糊 | Agent 乱跑 | AGENTS.md 中写明确规则 |
| 不设防循环规则 | API 费用爆炸 | 失败 2 次停止，限制连续调用 |
| 不管理记忆 | 记忆膨胀 | MEMORY.md 定期修剪，按日期分文件 |
| 不用子 Agent | 主 Agent 超时/卡住 | 长任务/并行任务用子 Agent |
| 不监控日志 | 问题发现太晚 | 启用详细日志，定期审查 |
| 7.1% ClawHub 技能泄露凭证 | 供应链攻击 | 审查第三方技能源码 |

### 八、Leo System 对标改进建议

基于本次调研，Leo System 应重点改进：

1. **记忆系统升级**：借鉴 Memu.bot 的知识图谱理念，将 `shared_memory.py` 升级为智能检索而非全量上下文填充
2. **安全加固**：实施 CVE-2026-25253 后的完整安全清单，特别是网关端口保护
3. **成本控制**：实施模型路由策略，简单任务用小模型
4. **防循环规则**：在 AGENTS.md 中添加明确的防循环和失败退出规则
5. **技能质量**：审查所有 98 个技能，移除未验证的，保留 20-30 个核心技能
6. **Watchdog 脚本**：完善 `openclaw_guardian.ps1`，确保自动恢复能力

### 九、参考来源

- [OpenClaw Security Best Practices](https://repello.ai/blog/technical-best-practices-to-securely-deploy-openclaw)
- [OpenClaw Skills Guide (DigitalOcean)](https://www.digitalocean.com/resources/articles/what-are-openclaw-skills)
- [CVE-2026-25253 Analysis (Hunt.io)](https://hunt.io/blog/cve-2026-25253-openclaw-ai-agent-exposure)
- [OpenClaw Production Deployment Discussion](https://github.com/openclaw/openclaw/discussions/13684)
- [OpenClaw Enterprise Setup Guide](https://voxturrlabs.com/blog/openclaw-enterprise-setup-guide/)
- [OpenClaw vs Memu.bot Comparison](https://ai.plainenglish.io/the-era-of-local-autonomous-agents-a-comprehensive-comparative-analysis-of-openclaw-and-memu-bot-963d4f4bee92)
- [OpenClaw Complete Setup Guide (JSMastery)](https://jsmastery.com/blogs/how-to-deploy-your-own-ai-agent-the-complete-openclaw-setup-guide)
- [Awesome OpenClaw Skills](https://github.com/VoltAgent/awesome-openclaw-skills)
- [OpenClaw Security Guide (LumaDock)](https://lumadock.com/tutorials/openclaw-security-best-practices-guide)
- [OpenClaw Anti-patterns (Reddit)](https://www.reddit.com/r/AiForSmallBusiness/comments/1r4uyrh/the_ultimate_openclaw_setup_guide/)
- [OpenClaw Feishu Channel (官方文档)](https://docs.openclaw.ai/)
- [OpenClaw vs Memu vs Nanobot (Agent Wars 2026)](https://evoailabs.medium.com/agent-wars-2026-openclaw-vs-memu-vs-nanobot-which-local-ai-should-you-run-8ef0869b2e0c)
- [Memu.bot Official Comparison](https://memu.bot/compare/openclaw)
- [OpenClaw Memory Management Best Practices](https://dev.to/) (多篇文章汇总)

---

## 2026-02-27 WebUI��������ʵ�����䣨Leo Web v2��

### ���ش��������ۣ�ժҪ��
1. `src/leo_interface/web_v2/api/.env` ����������Կ���߷��գ���
2. `src/leo_interface/web_v2/api/main.py` ���������ִ�нӿ�ȱ��ͳһ��Ȩ/��Ȩ������
3. `create_skill` ֱ��ƴ�� `skill.category`/`skill.name` ���ļ�ϵͳ·��������·�����ݷ��ա�
4. `execute_skill` / `execute_agent` ��¶ traceback ���ڲ�����ϸ�ڡ�
5. ǰ�� `SmartExecutor.tsx` ���ڶദ `(response as any).data`��������ԼƯ�Ʒ��ոߡ�
6. ���� `web`(streamlit) �� `web_v2`(react+fastapi) ���� UI���߽�δ����������

### �������ʵ����Դ���ٷ���
- FastAPI Security OAuth2/JWT: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- FastAPI CORS: https://fastapi.tiangolo.com/tutorial/cors/
- FastAPI Handling Errors: https://fastapi.tiangolo.com/tutorial/handling-errors/
- FastAPI Generate Clients (OpenAPI -> TS SDK): https://fastapi.tiangolo.com/advanced/generate-clients/
- OWASP API Security Top 10 (2023): https://owasp.org/API-Security/editions/2023/en/0x11-t10/
- OWASP API8 Security Misconfiguration: https://owasp.org/API-Security/editions/2023/en/0xa8-security-misconfiguration/
- Vite Env & Modes: https://vite.dev/guide/env-and-mode
- TypeScript noImplicitAny: https://www.typescriptlang.org/tsconfig/noImplicitAny.html
- typescript-eslint no-explicit-any: https://typescript-eslint.io/rules/no-explicit-any/
- W3C WAI-ARIA APG: https://www.w3.org/WAI/ARIA/apg/
- 12-Factor Config: https://www.12factor.net/config
- GitHub Secret Cleanup: https://docs.github.com/articles/remove-sensitive-data
