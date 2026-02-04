# 发现与决策: Claude Code + OpenClaw + Leo System 集成

> **最后更新**: 2026-02-04
> **官方仓库**: https://github.com/openclaw/openclaw

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
