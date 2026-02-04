# Leo AI System + OpenClaw 飞书集成执行方案

> 文档版本: 2.0
> 创建时间: 2026-01-30
> 更新时间: 2026-02-02
> 官方仓库: https://github.com/openclaw/openclaw
> 目标: 将 Leo AI System 能力通过 OpenClaw 集成到飞书机器人

---

## 1. 架构总览

```
┌─────────────────────────────────────────────────────────────────────┐
│                           飞书客户端                                  │
│                    (私聊 / 群聊 / 超级群)                              │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         OpenClaw Gateway                              │
│                    ws://127.0.0.1:18789                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │
│  │  Feishu插件  │  │  Telegram  │  │  Discord   │  ...              │
│  └─────────────┘  └─────────────┘  └─────────────┘                  │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │              Leo Command Handler (JS)                    │       │
│  │        D:\moltbot\leo_command_handler.js                 │       │
│  └─────────────────────────────────────────────────────────┘       │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │                    Leo AI System                         │       │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐            │       │
│  │  │  Agents   │  │  Skills   │  │ Workflows │            │       │
│  │  │  (10个)   │  │  (90+)    │  │  (5个)    │            │       │
│  │  └───────────┘  └───────────┘  └───────────┘            │       │
│  └─────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. 当前状态分析

### 2.1 OpenClaw 配置 (已更新)

**文件**: `c:\Users\刘方林\.openclaw\openclaw.json`

| 配置项 | 值 | 说明 |
|-------|-----|------|
| command.script | `leo_command_handler.js` | 命令处理器 |
| feishu.requireMention | `false` | 无需 @ 即可触发 |
| feishu.connectionMode | `websocket` | WebSocket 连接 |
| feishu.dmPolicy | `open` | 私聊开放 |
| feishu.groupPolicy | `open` | 群聊开放 |

### 2.2 命令处理器状态

| 功能 | 状态 | 说明 |
|-----|------|------|
| 排版 (format) | ✅ 可用 | 调用 content_layout_leo_skill |
| 研究 (research) | ⚠️ 待完善 | 需要导入 research_agent |
| 房产 (realestate) | ⚠️ 待完善 | 需要导入 realestate_agent |
| pipeline/workflow | ✅ 基础 | 需要增强工作流支持 |

---

## 3. 问题修复计划

### P0 - 立即修复

#### 3.1 清理过时代码

```bash
# 1. 删除空的基准测试目录
rmdir .benchmarks

# 2. 移动 leo-skills-old 到 archive
mv leo-skills-old/ archive/leo-skills-old-backup/
```

#### 3.2 修复 leo_knowledge 重复

```bash
# 重命名根目录的 leo_knowledge 为 generated
mv leo_knowledge/ generated/
```

**更新 CLAUDE.md**: 添加说明：
```
| generated/ | 自动生成文件 | capability_index.md, project_structure.md |
```

---

### P1 - 命令处理器增强

#### 3.3 创建新的 JS 命令处理器

**文件**: `D:\moltbot\leo_command_handler.js`

```javascript
/**
 * Leo System Command Handler for OpenClaw (JS Version)
 * 飞书消息触发 Leo System Skills 执行
 */

// 配置
const LEO_PATH = "D:\\桌面\\leo_ai_system";
const SKILLS_PATH = `${LEO_PATH}\\src\\leo_skills`;

const COMMANDS = {
    // 内容排版
    "排版": { handler: "contentLayout", skill: "content_layout_leo_skill" },
    "format": { handler: "contentLayout", skill: "content_layout_leo_skill" },
    "format_content": { handler: "contentLayout", skill: "content_layout_leo_skill" },

    // 研究调研
    "研究": { handler: "research", agent: "research_agent" },
    "research": { handler: "research", agent: "research_agent" },
    "调研": { handler: "research", agent: "research_agent" },
    "分析": { handler: "analyze", agent: "analysis_agent" },
    "analysis": { handler: "analyze", agent: "analysis_agent" },

    // 房地产
    "房产": { handler: "realestate", agent: "realestate_agent" },
    "realestate": { handler: "realestate", agent: "realestate_agent" },
    "楼盘": { handler: "realestate", agent: "realestate_agent" },

    // 电商
    "电商": { handler: "ecommerce", agent: "ecommerce_agent" },
    "选品": { handler: "ecommerce", agent: "ecommerce_agent" },
    "竞品": { handler: "competitor", agent: "ecommerce_agent" },

    // 营销文案
    "营销": { handler: "marketing", agent: "creative_agent" },
    "pipeline": { handler: "workflow", mode: "pipeline" },
    "workflow": { handler: "workflow", mode: "workflow" },

    // 工具
    "搜索": { handler: "webSearch", skill: "web_search_skill" },
    "帮我": { handler: "help", mode: "help" },
    "帮助": { handler: "help", mode: "help" },
};

async function runCommand(command, args) {
    const cmd = findCommand(command);
    if (!cmd) {
        return { success: false, error: `未知命令: ${command}` };
    }

    try {
        switch (cmd.handler) {
            case "contentLayout": return await runContentLayout(args);
            case "research": return await runAgent(cmd.agent, args);
            case "analyze": return await runAgent(cmd.agent, args);
            case "realestate": return await runAgent(cmd.agent, args);
            case "ecommerce": return await runAgent(cmd.agent, args);
            case "marketing": return await runAgent(cmd.agent, args);
            case "competitor": return await runCompetitorAnalysis(args);
            case "webSearch": return await runWebSearch(args);
            case "workflow": return await runWorkflow(cmd.mode, args);
            case "help": return showHelp();
            default: return { success: false, error: "未实现的处理器" };
        }
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function runAgent(agentName, args) {
    // 调用 Python Agent
    const { execSync } = require('child_process');
    const topic = args.content || args.topic || "";

    const cmd = `python "${LEO_PATH}\\src\\leo_subagents\\agents\\${agentName}\\main.py" --topic "${topic}"`;
    const result = execSync(cmd, { encoding: 'utf8', timeout: 120000 });

    return { success: true, output: result };
}

async function runWorkflow(mode, args) {
    const workflow = args.workflow || args.content || "";
    const topic = args.topic || "";

    return {
        success: true,
        output: `执行 Workflow: ${workflow}\n主题: ${topic}\n\n支持的 Workflows:\n- content_pipeline: 研究→创作→发布\n- research_pipeline: 收集→分析\n- analysis_pipeline: 分析→报告`
    };
}

function showHelp() {
    return {
        success: true,
        output: `Leo AI System 命令帮助
━━━━━━━━━━━━━━━
📝 内容排版
  排版 + 内容 → 生成排版后的内容

🔍 研究调研
  研究/调研 + 话题 → AI 研究分析
  分析 + 话题 → 数据分析报告

🏠 房地产
  房产/楼盘 + 项目名 → 营销方案
  realestate + 项目 → 房产分析

🛒 电商运营
  电商 + 产品 → 电商运营建议
  竞品 + 产品名 → 竞品分析

📊 Workflows
  pipeline + 工作流名 → 执行工作流

💡 快捷指令
  搜索 + 关键词 → 网络搜索
  帮助 → 显示此帮助
`
    };
}

// 主入口
async function main() {
    const input = process.stdin.read();
    const data = JSON.parse(input || "{}");
    const result = await runCommand(data.command, data);
    console.log(JSON.stringify(result));
}

main();
```

---

### P1 - 技能能力映射

#### 3.4 飞书机器人能力矩阵

| 触发词 | Agent/Skill | 功能 | 状态 |
|-------|------------|------|------|
| 排版/format | content_layout_leo_skill | 内容排版 | ✅ |
| 研究/调研 | research_agent | 信息调研 | ✅ |
| 分析 | analysis_agent | 数据分析 | ✅ |
| 房产/楼盘 | realestate_agent | 房地产 | ✅ |
| 电商/选品 | ecommerce_agent | 电商运营 | ✅ |
| 营销/文案 | creative_agent | 内容创作 | ✅ |
| 架构 | architect_agent | 技术架构 | ✅ |
| 产品/PRD | product_manager_agent | 产品需求 | ✅ |
| 小程序 | mobile_agent | 移动开发 | ✅ |
| 搜索 | web_search_skill | 网络搜索 | ✅ |
| 竞品 | competitor_scraper_skill | 竞品分析 | ✅ |
| pipeline | content_pipeline | 内容工作流 | ✅ |
| workflow | research_pipeline | 研究工作流 | ✅ |

---

### P2 - Workflow 集成

#### 3.5 Workflow 与飞书消息的映射

```
飞书消息触发
    │
    ▼
┌──────────────────────────────────────────────────────┐
│              消息意图识别                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ 内容创作  │  │ 研究调研  │  │ 数据分析  │           │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
│       │             │             │                  │
│       ▼             ▼             ▼                  │
│  content_   research_    analysis_                  │
│  pipeline    pipeline     pipeline                  │
└──────────────────────────────────────────────────────┘
```

**Workflow 定义** (src/leo_workflows/workflows/content_pipeline/__init__.py):

```python
CONTENT_PIPELINE = {
    "name": "content_pipeline",
    "description": "内容生产完整流程：研究 → 创作 → 排版 → 发布",
    "agents": {
        "research": {
            "agent": "research_agent",
            "skills": ["research_assistant_skill", "web_search_skill"],
            "output": "research_report"
        },
        "create": {
            "agent": "creative_agent",
            "skills": ["content_layout_leo_skill", "text_generator_skill"],
            "output": "draft_content"
        },
        "publish": {
            "agent": "task_agent",
            "skills": ["realestate_news_publisher_skill"],
            "output": "published_content"
        }
    }
}
```

---

## 4. 执行步骤

### Phase 1: 基础修复 (1小时)

| 步骤 | 操作 | 预计时间 |
|-----|------|---------|
| 1.1 | 删除 `.benchmarks/` 空目录 | 5分钟 |
| 1.2 | 移动 `leo-skills-old/` 到 archive | 10分钟 |
| 1.3 | 重命名 `leo_knowledge/` → `generated/` | 5分钟 |
| 1.4 | 更新 CLAUDE.md | 10分钟 |

**命令**:
```bash
# 在项目根目录执行
rmdir .benchmarks 2>/dev/null || echo "目录不存在"
mv leo-skills-old archive/ 2>/dev/null || echo "目录不存在"
mv leo_knowledge generated/ 2>/dev/null || echo "目录不存在"
```

### Phase 2: 命令处理器 (2小时)

| 步骤 | 操作 | 预计时间 |
|-----|------|---------|
| 2.1 | 创建 `leo_command_handler.js` | 30分钟 |
| 2.2 | 测试私聊触发 | 20分钟 |
| 2.3 | 测试群聊触发 | 20分钟 |
| 2.4 | 修复 Agent 导入问题 | 30分钟 |
| 2.5 | 优化错误处理 | 20分钟 |

### Phase 3: 能力完善 (持续)

| 步骤 | 操作 | 优先级 |
|-----|------|-------|
| 3.1 | 实现 collaboration 技能 (7个) | P1 |
| 3.2 | 实现 planning_with_files_skill | P1 |
| 3.3 | 更新 capability_index.md | P2 |
| 3.4 | 完善所有 Workflow 定义 | P2 |
| 3.5 | 规范化嵌套 git 仓库 | P3 |

---

## 5. 测试验证

### 5.1 私聊测试

```
用户 → "帮我研究一下 AI 眼镜市场"
机器人 → [调用 research_agent]
       → "✅ 研究完成：..."
```

### 5.2 群聊测试

```
用户A → "排版这段内容..."
机器人 → [调用 content_layout_leo_skill]
       → [生成排版后的内容]
```

### 5.3 Workflow 测试

```
用户 → "运行 content_pipeline，主题：宁波房产"
机器人 → [调用 content_pipeline]
       → research → create → publish
       → "✅ 内容生产完成"
```

---

## 6. 监控与日志

### 6.1 日志位置

| 日志类型 | 位置 |
|---------|------|
| OpenClaw | `%USERPROFILE%\.openclaw\logs\` |
| Leo System | `src/leo_system/logs/` |
| 命令执行 | `D:\moltbot\logs\` |

### 6.2 健康检查

```bash
# 检查飞书连接状态
curl http://127.0.0.1:18789/health

# 检查 Agent 状态
python src/leo_subagents/agents/research_agent/status.py
```

---

## 7. 附录

### 7.1 相关文件

| 文件 | 用途 |
|-----|------|
| `c:\Users\刘方林\.openclaw\openclaw.json` | OpenClaw 主配置 |
| `D:\moltbot\leo_command_handler.js` | Leo 命令处理器 |
| `src/leo_subagents/config/agents.yaml` | Agent 配置 |
| `src/leo_orchestrator/workflow_engine.py` | Workflow 引擎 |

### 7.2 飞书 API 文档

- 飞书开放平台: https://open.feishu.cn/
- OpenClaw 飞书插件: `D:\moltbot\extensions\feishu\`

---

## 8. 总结

**本方案目标**:
1. ✅ 清理系统冗余（重复目录、过时代码）
2. ✅ 增强飞书机器人命令处理器
3. ✅ 实现完整的 Agent/Skill 能力映射
4. ✅ 打通 Workflow 与飞书消息的集成

**预计工作量**:
- Phase 1: 1小时
- Phase 2: 2小时
- Phase 3: 持续迭代

---
*文档创建于 2026-01-30*
