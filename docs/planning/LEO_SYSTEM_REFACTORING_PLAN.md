# Leo AI System 重构规划

> 基于 OpenClaw + Claude Code 最佳实践
> 生成时间: 2026-03-03

---

## 一、架构对比分析

### OpenClaw 核心架构

```
┌─────────────────────────────────────────────────────────┐
│                    Gateway (网关)                        │
│  - 消息路由、会话管理、通道连接                          │
├──────────┬──────────┬──────────┬──────────┬────────────┤
│ Channels │  Agents  │  Skills  │  Memory  │  Plugins   │
│   30+    │   系统    │   系统    │   系统    │   系统     │
├──────────┴──────────┴──────────┴──────────┴────────────┤
│                   工具层                                │
│  Browser | CLI | Exec | MCP | Sub-Agents              │
└─────────────────────────────────────────────────────────┘
```

### Claude Code 核心能力

```
┌─────────────────────────────────────────────────────────┐
│                   CLI + IDE 集成                        │
├──────────┬──────────┬──────────┬──────────┬────────────┤
│  Skills  │ Subagents│   Hooks  │    MCP   │  Memory    │
├──────────┴──────────┴──────────┴──────────┴────────────┤
│                  权限系统                                │
└─────────────────────────────────────────────────────────┘
```

### Leo System 现状

```
┌─────────────────────────────────────────────────────────┐
│                 src/leo_skills/                        │
│  242+ 技能，18个分类                                    │
├──────────┬──────────┬──────────┬──────────┬────────────┤
│ collaboration│ testing │ devops  │  core   │ business   │
├──────────┴──────────┴──────────┴──────────┴────────────┤
│                  待整合                                  │
│  .claude/agents | mcp.json | hooks.json               │
└─────────────────────────────────────────────────────────┘
```

---

## 二、重构目标

### 2.1 统一架构

采用 "Gateway + Channel" 模式：

```
┌─────────────────────────────────────────────────────────┐
│                  Leo Gateway                            │
│  - 会话管理 (Sessions)                                   │
│  - 消息路由 (Routing)                                    │
│  - 状态管理 (State)                                      │
├─────────────────────────────────────────────────────────┤
│  Channel 层 (输入)                                       │
│  - CLI Channel (Claude Code)                            │
│  - MCP Channel (MCP Server)                             │
│  - Web Channel (Web UI)                                 │
│  - OpenClaw Channel (飞书等)                            │
├─────────────────────────────────────────────────────────┤
│  Agent 层                                                │
│  - 主 Agent (Leo)                                        │
│  - 子 Agents (code-reviewer, researcher, etc.)         │
├─────────────────────────────────────────────────────────┤
│  Skill 层                                               │
│  - Superpowers 14 核心技能                              │
│  - Leo 扩展技能 (242+)                                   │
├─────────────────────────────────────────────────────────┤
│  Tool 层                                                │
│  - Claude Code Tools                                    │
│  - MCP Tools                                            │
│  - Custom Tools                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.2 目录结构重构

```
leo_ai_system/
├── .claude/                    # Claude Code 配置
│   ├── agents/                 # 子代理定义
│   ├── hooks/                  # Hook 脚本
│   ├── memory/                  # 自动记忆
│   ├── plugins/                 # 插件
│   ├── settings.json           # 配置文件
│   └── permissions.md          # 权限文档
│
├── src/                        # 源代码
│   ├── leo_skills/            # 技能系统 (保留)
│   │   ├── collaboration/       # 协作技能
│   │   ├── testing/            # 测试技能
│   │   ├── devops/             # DevOps技能
│   │   └── core/               # 核心技能
│   │
│   ├── leo_gateway/           # 网关系统 (新建)
│   │   ├── __init__.py
│   │   ├── router.py           # 消息路由
│   │   ├── session.py          # 会话管理
│   │   ├── state.py            # 状态管理
│   │   └── channel/            # 通道
│   │       ├── cli.py
│   │       ├── mcp.py
│   │       └── web.py
│   │
│   ├── leo_agents/            # Agent 系统 (新建)
│   │   ├── base.py
│   │   ├── leo.py             # 主 Agent
│   │   └── subagents/         # 子代理
│   │
│   ├── leo_tools/             # 工具系统 (新建)
│   │   ├── base.py
│   │   ├── browser.py
│   │   ├── file_ops.py
│   │   └── mcp_tools.py
│   │
│   ├── leo_memory/            # 记忆系统 (新建)
│   │   ├── __init__.py
│   │   ├── session.py          # 会话记忆
│   │   ├── context.py          # 上下文
│   │   └── learnings.py        # 学习积累
│   │
│   └── leo_plugins/           # 插件系统 (新建)
│       ├── __init__.py
│       ├── manifest.py
│       └── registry.py
│
├── mcp/                        # MCP 配置
│   ├── servers.json            # 服务器配置
│   └── plugins/               # MCP 插件
│
├── docs/                       # 文档
│   ├── architecture/          # 架构文档
│   ├── guides/                # 操作指南
│   └── reference/             # 参考
│
└── scripts/                    # 脚本
    ├── sync/                  # 同步脚本
    ├── maintenance/           # 维护脚本
    └── gateway/               # 网关脚本
```

---

## 三、重构阶段

### 阶段 1: 基础架构 (Week 1)

| 任务 | 说明 | 优先级 |
|------|------|--------|
| 创建 `leo_gateway/` 模块 | 基础网关框架 | P0 |
| 创建 `leo_agents/` 模块 | Agent 系统 | P0 |
| 整合 `mcp/` 目录 | MCP 配置 | P1 |
| 完善 `hooks/` 脚本 | Hook 增强 | P1 |

### 阶段 2: 核心功能 (Week 2)

| 任务 | 说明 | 优先级 |
|------|------|--------|
| 会话管理系统 | Session 管理 | P0 |
| 消息路由系统 | Router | P0 |
| 子代理系统 | Subagents 完善 | P0 |
| 记忆系统 | Memory 增强 | P1 |

### 阶段 3: 集成 (Week 3)

| 任务 | 说明 | 优先级 |
|------|------|--------|
| OpenClaw 集成 | 飞书通道 | P0 |
| MCP 集成 | MCP 工具 | P0 |
| Claude Code 集成 | CLI 集成 | P0 |
| 插件系统 | Plugin 系统 | P1 |

### 阶段 4: 优化 (Week 4)

| 任务 | 说明 | 优先级 |
|------|------|--------|
| 性能优化 | 缓存、并发 | P2 |
| 监控完善 | 日志、指标 | P2 |
| 文档完善 | API 文档 | P2 |

---

## 四、关键设计决策

### 4.1 Gateway 模式

采用事件驱动架构：

```python
class LeoGateway:
    def __init__(self):
        self.channels = ChannelRegistry()
        self.router = MessageRouter()
        self.session_mgr = SessionManager()

    async def handle_message(self, channel, message):
        # 1. 路由消息
        agent = self.router.route(message)

        # 2. 查找/创建会话
        session = self.session_mgr.get_or_create(
            channel=channel,
            user=message.user
        )

        # 3. 执行 Agent
        response = await agent.execute(session, message)

        # 4. 返回结果
        await channel.send(response)
```

### 4.2 Channel 抽象

```python
class Channel(ABC):
    @abstractmethod
    async def send(self, message: Message): ...

    @abstractmethod
    async def receive(self) -> Message: ...

class CLIClannel(Channel):
    """Claude Code CLI 通道"""

class MCPChannel(Channel):
    """MCP 协议通道"""

class WebChannel(Channel):
    """Web UI 通道"""

class OpenClawChannel(Channel):
    """飞书等消息通道"""
```

### 4.3 技能加载

```python
class SkillRegistry:
    def __init__(self):
        self.skills = {}

    def load_from_directory(self, path: Path):
        for skill_dir in path.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                self.skills[skill_dir.name] = SkillLoader.load(skill_dir)

    def get_skill(self, name: str) -> Optional[Skill]:
        return self.skills.get(name)
```

---

## 五、迁移策略

### 5.1 保留项

- `src/leo_skills/` - 所有现有技能
- `.claude/hooks.json` - Hook 配置
- `mcp.json` - MCP 配置
- 文档和配置

### 5.2 新增项

- `src/leo_gateway/` - 网关模块
- `src/leo_agents/` - Agent 模块
- `src/leo_tools/` - 工具模块
- `src/leo_memory/` - 记忆模块
- `src/leo_plugins/` - 插件模块

### 5.3 清理项

- `leo-skills-old/` - 旧技能目录
- `leo_wingman/` - 旧 wingman
- 重复配置文件

---

## 六、验证清单

- [x] Gateway 模块可正常启动 (`src/leo_gateway/`)
- [x] CLI Channel 可接收消息 (`channel/base.py`)
- [x] Session 持久化 (`session.py`)
- [x] Router 智能路由 (`router.py`)
- [ ] Skill 系统正常工作 (已有)
- [ ] 子代理可被调用 (已有 `.claude/agents/`)
- [ ] Hook 脚本正常执行 (已有)
- [ ] MCP 工具可用 (已有)

---

## 七、相关文档

- OpenClaw 架构: https://docs.openclaw.ai/concepts/architecture.md
- Claude Code 能力: ../reference/CLAUDE_CODE_CAPABILITIES.md
- 当前架构报告: ../reference/LEO_SYSTEM_ARCHITECTURE_REPORT.md
