---
description:
alwaysApply: true
---

# Leo AI System - Context Registry

> **Attention Strategy**: 按需读取，不要一次性加载所有引用文件。
> **规范加载**: 每次会话优先加载 `docs/reference/BEST_PRACTICE_STANDARD.md`

## 0. 上下文工程 (Context Engineering)

> **"Context Window = RAM, Filesystem = Disk"**

复杂任务（3+步骤）使用 planning_with_files_skill：

| 文件 | 用途 |
|------|------|
| `docs/planning/task_plan.md` | 阶段、进度、决策 |
| `docs/research/findings.md` | 研究发现 |
| `docs/progress/progress.md` | 会话日志 |

**规则**: 复杂任务先建计划 → 每2次搜索后更新发现 → 决策前重读计划 → 记录错误不重复

---

## 1. Context Map (静态上下文) - 加载优先级

### P0 - 每次会话必读 (已自动加载)
| Module | Path | 说明 |
| :--- | :--- | :--- |
| **USER.md** | `~/.openclaw/workspace/USER.md` | OpenClaw 加载 |
| **QUICK_CONTEXT** | `leo_knowledge/context/QUICK_CONTEXT.md` | 快速加载 (<50行) |

### P1 - 重要 (按需读取)
| Module | Path |
| :--- | :--- |
| **User Profile** | `leo_knowledge/context/user_profile.md` |
| **Dev Guide** | `leo_knowledge/context/development_guide.md` |

### P2 - 参考
| Module | Path |
| :--- | :--- |
| **Architecture** | `leo_knowledge/context/system_architecture.md` |
| **Project Tree** | `leo_knowledge/context/project_structure.md` |
| **All Capabilities** | `leo_knowledge/context/capability_index.md` |
| **Skill Levels** | `leo_knowledge/context/skill_levels.md` |

## 2. Active Work (动态状态)

- **Current Task**: `docs/planning/task_plan.md` (优先检查)
- **Findings**: `docs/research/findings.md`
- **Progress**: `docs/progress/progress.md`

## 3. 文件路径规则

```
根目录 (只放入口和配置):
├── CLAUDE.md, README.md, AGENTS.md
├── src/                   # 源代码
│   └── docker/           # Docker 配置
├── scripts/               # 脚本 (按功能分子目录)
├── tests/                 # 测试
├── projects/              # 项目文件
│   ├── output/           # 输出文件
│   └── reports/          # 报告文件
├── leo_knowledge/        # 知识库
├── config/                # 配置文件
├── data/                  # 数据文件
└── docs/                  # 所有文档
    ├── identity/          # 身份
    ├── reference/         # 索引、清单、运维手册
    ├── guides/            # 操作指南
    ├── planning/          # 任务规划
    ├── progress/          # 进度日志
    ├── research/          # 研究发现
    └── assets/            # 静态资源
```

**新建文件**: 先判断类型 → 放到 `docs/` 对应目录 → 禁止放根目录

---

## 4. Quick Actions

1. 检查 `docs/planning/task_plan.md` 获取当前任务状态
2. 新项目先读 `leo_knowledge/context/user_profile.md`
3. 写代码前查 `leo_knowledge/context/capability_index.md` 避免重复
4. 查看 `leo_knowledge/context/skill_levels.md` 了解技能成熟度（A/B/C/D 四级）
5. 复杂任务用 planning_with_files_skill

---

## 5. 集成系统

### OpenClaw (飞书 AI 助手)

| 项目 | 信息 |
|------|------|
| **本地目录** | `D:\openclaw` |
| **版本** | 2026.3.2 |
| **USER.md** | `~/.openclaw/workspace/USER.md` (已更新v2.1) |
| **运维手册** | `docs/reference/OPENCLAW_OPS.md` |
| **启动命令** | `cd D:\openclaw && node openclaw.mjs gateway --port 18789` |

**核心规则**: feishu 是 Channel 不是 Plugin；`doctor --fix` 后必须人工检查配置

**故障案例库**:

| 日期 | 症状 | 根因 | 修复方案 |
|------|------|------|----------|
| 2026-03-01 | `Message ordering conflict` 反复出现 | 会话历史 1000+ 条，compaction 超时失败，状态损坏 | 1. 删除 `~/.openclaw/agents/leo-assistant/sessions/*`<br>2. 重启网关<br>3. 部署定时清理脚本 `scripts/openclaw/session_maintenance.ps1` |
| 2026-03-01 | MiniMax API 401 | 配置使用旧 API Key (`sk-api-`)，Coding Plan 需用 `sk-cp-` Key | 更新 `openclaw.json` 中的 apiKey 和 baseUrl |

**预防性维护**:
- 定期在飞书发送 `/reset` 或 `/new` 重置会话
- 每周运行一次 `session_maintenance.ps1` 清理大文件
- 监控 `~/.openclaw/agents/leo-assistant/sessions/` 目录大小

### Superpowers (v4.3.1)

| 项目 | 说明 |
|------|------|
| **Leo 技能** | `src/leo_skills/` (唯一技能来源) |
| **Hook** | `.claude/hooks.json` SessionStart 自动注入 |
| **同步脚本** | `scripts/sync/sync_superpowers.py` |

### Claude Code (v2.1.70)

| 项目 | 说明 |
|------|------|
| **版本** | 2.1.81 (最新) |
| **安装/更新** | `winget install Anthropic.ClaudeCode` |
| **安装路径** | `C:\Users\admin\AppData\Local\Microsoft\WinGet\Packages\Anthropic.ClaudeCode_Microsoft.Winget.Source_8wekyb3d8bbwe` |
| **Agents** | `.claude/agents/` (code-reviewer, researcher, documenter) |
| **MCP** | `mcp.json` |
| **沙箱** | 已启用 |
| **Agent SDK** | `.claude/sdk/` (Python/TypeScript 示例) |

### Claude Code 完整能力清单

| 模块 | 状态 | 文档 |
|------|------|------|
| CLI 命令 (15+) | ✅ | 内置 |
| CLI Flags (60+) | ✅ 已配置 | `docs/reference/CLAUDE_CODE_CLI_FLAGS.md` |
| 斜杠命令 (65+) | ✅ 清单 | `docs/reference/CLAUDE_CODE_SLASH_COMMANDS.md` |
| 权限模式 (6种) | ✅ | `settings.local.json` |
| 配置作用域 (4层) | ✅ | Local + Project 已配 |
| MCP 服务器 | ✅ 3个 | `mcp.json` |
| Agent SDK | ✅ 已配置 | `.claude/sdk/` |
| 沙箱模式 | ✅ 已启用 | `settings.local.json` |
| 平台集成 | ⚠️ | VSCode + Terminal |
| 企业功能 | ❌ | 需要付费订阅 |

### 浏览器自动化能力（无订阅最佳实践）

> **优先级**：OpenCLI 优先 → OpenCLI 没有才回退 → CDP Proxy

#### 能力状态

| 工具 | 状态 | 说明 |
|------|------|------|
| **OpenCLI** | ✅ 已就绪 | 零配置、零Token消耗、87+平台 |
| **CDP Proxy** | ✅ 已就绪 | Chrome远程调试已开启，OpenCLI回退方案 |
| **Playwright MCP** | ⚠️ 可选 | 高频确定性任务，按需安装 |

#### 工具选择规则（强制）

```
规则：浏览器操作优先使用 OpenCLI，回退顺序：适配器 → generate → browser → CDP Proxy

1. OpenCLI 有适配器？ → ✅ 直接用（零成本）
   ├─ 社交媒体：twitter, xiaohongshu, bilibili, weibo, reddit
   ├─ 电商：amazon, 1688, jd
   ├─ 新闻：hackernews, 36kr, v2ex
   └─ AI工具：cursor, notion, codex

2. OpenCLI 没有适配器？ → 尝试 OpenCLI 通用能力
   ├─ opencli generate <url> --goal "目标"  # 一键生成适配器
   ├─ opencli explore <url> --site <名称>   # 探索网站 API
   └─ opencli browser                         # 直接控制浏览器（通用）

3. OpenCLI 通用能力也无法实现？ → 回退到 CDP Proxy
   └─ curl http://localhost:3456 操作浏览器

4. CDP 也无法实现？ → 考虑 Playwright MCP（按需安装）
```

#### OpenCLI 通用能力（适配器之外的选项）

```bash
# 1. 一键生成适配器（最优先尝试）
opencli generate https://目标网站.com --goal "获取内容"

# 2. 探索网站 API
opencli explore https://目标网站.com --site mysite
opencli synthesize mysite

# 3. 直接控制浏览器（通用，无需适配器）
opencli browser open https://目标网站.com
opencli browser state
opencli browser click <N>
opencli browser type <N> "文本"
opencli browser eval "JS代码"
opencli browser network
opencli browser screenshot

# 4. 浏览器控制快捷命令
opencli open <url>    # 打开URL
opencli state         # 获取状态
opencli click <N>     # 点击元素
opencli type <N> "x"  # 输入文本
```

#### 回退检查清单

执行浏览器任务前：
1. [ ] `opencli list -f json | grep <平台>` 检查是否有适配器
2. [ ] 有适配器？直接用 OpenCLI
3. [ ] 没有适配器？尝试 `opencli generate <url> --goal "目标"`
4. [ ] generate 也不行？尝试 `opencli browser open <url>` + 操作命令
5. [ ] browser 也不行？回退到 CDP Proxy

#### OpenCLI 常用命令

```bash
# 社交媒体
opencli bilibili hot --limit 10 -f json
opencli xiaohongshu search "关键词" -f json
opencli twitter trending -f json
opencli reddit hot -f json

# 电商
opencli amazon bestsellers electronics -f json
opencli 1688 search "商品" -f json

# 新闻
opencli hackernews top -f json
opencli v2ex hot -f json

# 诊断
opencli doctor
opencli list -f json | grep <平台名>
```

#### CDP Proxy API

```bash
# 基础操作
curl -s http://localhost:3456/targets              # 列出标签页
curl -s "http://localhost:3456/info?target=ID"    # 页面信息
curl -s "http://localhost:3456/eval?target=ID" -d 'document.title'  # 执行JS

# 浏览器控制
curl -s "http://localhost:3456/navigate?target=ID&url=https://example.com"
curl -s -X POST "http://localhost:3456/click?target=ID" -d '.button'
curl -s "http://localhost:3456/screenshot?target=ID&file=/tmp/shot.png"
```

#### LEO 集成代码

```python
# 方式1：直接调用封装工具（推荐）
import sys
sys.path.insert(0, 'e:/桌面/leo_ai_system')
from scripts.browser import OpenCLIClient, CDPClient

# OpenCLI
client = OpenCLIClient()
data = client.bilibili_hot(limit=10)
data = client.xiaohongshu_search("关键词")

# CDP
cdp = CDPClient()
tabs = cdp.list_tabs()
cdp.screenshot(tab_id, "/tmp/shot.png")

# 方式2：直接调用（无需导入）
import subprocess
import json
import requests

# OpenCLI 调用
def opencli(platform, cmd, *args, limit=10):
    cmd = ["opencli.cmd" if os.name == 'nt' else "opencli", platform, cmd, "-f", "json", "--limit", str(limit), *args]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return json.loads(result.stdout) if result.returncode == 0 else {"error": result.stderr}

# CDP Proxy 调用
CDP = "http://localhost:3456"
def list_tabs():
    return requests.get(f"{CDP}/targets").json()
def eval_js(target_id, js):
    return requests.post(f"{CDP}/eval?target={target_id}", data=js).json()
```

#### 相关文档

- [OpenCLI完整学习文档](docs/research/OpenCLI完整学习文档.md)
- [GEOFlow学习文档](docs/research/GEOFlow学习文档.md)

### Telegram Channels 配置 (2026-03-24) ❌ 已移除

| 项目 | 信息 |
|------|------|
| **状态** | ❌ 配置失败，channels 功能需要 Teams/Enterprise 订阅 |
| **Bot Token** | `8308099484:AAEjqZp5VFu5Gt5IQ1NKW5V3SD7YPOTRTmU` (已清除) |
| **清理日期** | 2026-03-24 |

**失败原因**:
- `--channels` 参数显示 "Channels are not currently available"
- Claude Code CLI 的 channels 功能需要付费订阅

**已清理**:
- [x] 删除 `~/.claude/channels/telegram/` 目录
- [x] 禁用 `telegram@claude-plugins-official` 插件
- [x] 移除 `settings.json` 中的 Telegram 配置
- [x] 删除 `scripts/telegram_*.bat/py` 文件

**替代方案**: 使用 OpenClaw（飞书）作为代理路由

### cc-switch (AI 工具统一配置中心)

> **核心功能**: 一站式管理 Claude/Codex/Gemini 等所有 AI 工具的 API 密钥和配置

| 项目 | 信息 |
|------|------|
| **配置目录** | `~/.cc-switch/` |
| **数据库** | `~/.cc-switch/cc-switch.db` |
| **设置文件** | `~/.cc-switch/settings.json` |
| **VSCode 同步** | 自动同步到 VSCode 插件设置 |

#### API 密钥配置流程

**1. 获取 API 密钥**

| 服务商 | 获取地址 | 密钥格式 |
|--------|----------|----------|
| **Claude (Anthropic)** | https://console.anthropic.com/ | `sk-ant-xxxxx` |
| **OpenAI (Codex)** | https://platform.openai.com/api-keys | `sk-xxxxx` |
| **Google (Gemini)** | https://makersuite.google.com/app/apikey | `AIxxxxx` |

**2. 在 cc-switch 中添加密钥**

```bash
# 启动 cc-switch 面板
cd ~/.cc-switch && cc-switch

# 或在 PowerShell 中直接运行
cc-switch
```

操作步骤：
1. 点击 **"Add Provider"** 添加服务商
2. 选择 **Claude / OpenAI / Gemini**
3. 粘贴 API 密钥
4. 点击 **"Test"** 验证密钥有效性
5. 点击 **"Save"** 保存

**3. 同步配置到所有工具**

```bash
# 一键同步到 VSCode、Claude Code、Codex 等
cc-switch sync

# 强制重新同步
cc-switch sync --force
```

同步后的配置位置：
- **Claude Code**: `~/.claude/settings.json`
- **Codex**: `~/.codex/config.json`
- **VSCode**: `settings.json` 中的 AI 插件配置

#### 多电脑迁移流程

**迁移前（旧电脑）**：
```powershell
# 确保 cc-switch 数据库已备份
# 默认位置: ~/.cc-switch/cc-switch.db
```

**迁移后（新电脑）**：

| 步骤 | 操作 |
|------|------|
| 1 | 复制 `~/.cc-switch/` 文件夹到新电脑 `C:\Users\[新用户名]\` |
| 2 | 运行路径更新脚本 `update_leo_system.ps1` 修复用户名路径 |
| 3 | 打开 cc-switch 验证 API 密钥仍然有效 |
| 4 | 运行 `cc-switch sync` 重新同步所有配置 |
| 5 | 验证 VSCode 插件已正确加载配置 |

**重要：项目路径配置**

如果你的 LEO 项目不在默认位置（如放在 E 盘桌面），需要更新 cc-switch 中的项目路径：

```json
// ~/.cc-switch/settings.json
{
  "projectPaths": {
    "leo-ai-system": "E:\\桌面\\leo_ai_system"
  }
}
```

或在 cc-switch GUI 中：
**Settings** → **Project Paths** → 添加/修改 `leo-ai-system` 路径为 `E:</桌面>\leo_ai_system`

**常见问题**：

| 问题 | 原因 | 解决 |
|------|------|------|
| `cc-switch sync` 报错找不到路径 | 用户名变更导致路径不匹配 | 运行 `update_leo_system.ps1` 修复路径 |
| API 密钥失效 | 密钥过期或被封 | 重新到官网生成新密钥并更新 |
| VSCode 插件不同步 | 插件未启用 cc-switch 集成 | 检查 VSCode 设置中 `cc-switch.enabled: true` |

---

## 6. 用户偏好与记忆 (2026-03-04 更新)

### 用户偏好 (来自 USER.md v2.1)
- **语言**: 简体中文 ONLY
- **反馈方式**: 直接给结果，不要铺垫
- **方案风格**: 务实优先，给可执行的具体方案
- **错误处理**: 报错同时给解决方案

### AI 回复规则（强制）
- **思考过程**: 必须使用简体中文
- **所有输出**: 必须使用简体中文
- **禁止**: 不要输出英文，所有回复都要是简体中文

### 用户记忆存储
| 类型 | 位置 | 说明 |
|------|------|------|
| **长期** | `~/.openclaw/workspace/USER.md` | 基础档案、业务、目标 |
| **中期** | `docs/progress/` | 本周任务和进度 |
| **短期** | 当前会话上下文 | 当前任务、修改意见 |
| **教训** | `leo_knowledge/context/learning_log.md` | 用户纠正的错误 |

### 记忆调用规则
1. 每次会话: 先读 USER.md 加载长期记忆
2. 任务开始: 检查 docs/progress/ 加载中期记忆
3. 用户反馈: 立即更新到 learning_log.md

---

## 7. 会话驱动规则 (原6)

1. **先读后写**: 修改文件前必须先 Read，批量操作每个文件都要读
2. **路径验证**: 重构后执行 `PYTHONUTF8=1 python scripts/maintenance/validate_paths.py`
3. **统一 Bash**: 禁止 PowerShell，脚本用 `.sh` 或 `.py`

---

## 8. 简体中文规则（强制）

- AI 回复全部使用简体中文
- 代码注释用中文，文件名/变量名保持英文
- 技术术语保留英文原词，括号附中文解释
- Git 提交信息使用中文
- 用大白话解释，给可直接执行的命令，步骤数字编号

---

## 9. 双引擎协作（Claude Code + Codex）

> 详细规范见 `AGENTS.md`

**简单记忆**: Claude 想 → Claude 拆 → Codex 干 → Claude 查 → Claude 收

| Claude Code (大脑) | Codex (双手) |
|---|---|
| 架构设计、代码审查、重构、规划 | 脚手架搭建、模板生成、批量修改 |

**冲突避免**: 不同时编辑同一文件；Codex 不改 CLAUDE.md；Claude 不做批量创建

---

## 10. Hermes Agent ( Nous Research AI 助手)

> **安装日期**: 2026-04-11
> **官方文档**: https://hermes-agent.nousresearch.com/
> **GitHub**: https://github.com/nousresearch/hermes-agent
> **重要**: Windows 原生不支持，必须使用 WSL2

### 环境状态

| 项目 | 状态 |
|------|------|
| WSL2 | ✅ Ubuntu-22.04.5 LTS |
| 安装位置 | `/home/adminhermes/.hermes/` |
| hermes 版本 | ✅ v0.8.0 |
| PATH | ✅ 已配置 |
| MiniMax 模型 | ✅ 已配置 |
| Skills Hub | ✅ 64 内置 + 9 本地 |
| 核心功能 | ✅ 完全可用 |

### 启动命令

```bash
source ~/.config/hermes/proxy.sh && ALL_PROXY=http://127.0.0.1:7897 hermes chat
```

### 已解决问题

1. **base_url 乱码**：修复 `~/.hermes/.env` 中的 `MINIMAX_CN_BASE_URL`
2. **config.yaml 乱码**：重建正确配置
3. **代理未生效**：hermes 需显式传 `ALL_PROXY` 环境变量

### 配置文件位置

- 主配置：`~/.hermes/config.yaml`
- 环境变量：`~/.hermes/.env`
- 代理脚本：`~/.config/hermes/proxy.sh`

### 已知配置（来自 config.yaml）

| 项目 | 值 |
|------|-----|
| 默认模型 | MiniMax-M2.7 |
| 默认 Provider | minimax-cn |
| 配置文件 | `/home/adminhermes/.hermes/config.yaml` |

### 快速启动

```bash
# 打开 WSL Ubuntu 终端
# 激活代理（如果需要）
source ~/.config/hermes/proxy.sh

# 进入目录
cd /home/adminhermes/.hermes

# 启动 hermes
hermes chat
```
