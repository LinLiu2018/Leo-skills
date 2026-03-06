# OpenClaw + VSCode 插件 (Claude Code + Codex + Gemini) Windows 集成最佳实践

> 调研时间: 2026-03-04
> 适用环境: Windows 11 + VSCode + Claude Code 2.1.63
> 业务场景: 房地产经纪 | 商业地产 | 贷款金融 | 跨境电商 | 内容运营
> 用户背景: 零代码基础，通过 VSCode+Claude 学习实践
> 来源: 官方文档 + Leo AI System 实践

---

## 零、快速开始（5分钟上手）

### 你的 AI 分身配置

| 时间 | 你在做什么 | AI 在做什么 | 使用工具 |
|------|-----------|------------|---------|
| **6:00-7:30** | 晨跑训练 | 自动生成昨日数据报表 | OpenClaw + 飞书 |
| **8:00-12:00** | 房产业务（带看/谈判） | 分析房源数据、生成营销文案 | Claude + VSCode |
| **13:00-18:00** | 多业务管理 | 自动化脚本执行、竞品监控 | Codex + 定时任务 |
| **19:00-23:00** | 学习/开发 | 代码教学、项目搭建 | Claude Code 扩展 |

### 一句话记忆
> **"Claude 想、Claude 拆、Codex 干、Claude 查、飞书收"**

---

## 一、整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              用户工作流层                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │  VSCode      │    │  Claude Code │    │  飞书/钉钉    │                  │
│  │  扩展面板     │◄──►│  扩展        │◄──►│  IM 客户端    │                  │
│  └──────────────┘    └──────┬───────┘    └──────┬───────┘                  │
│                             │                    │                          │
│                             ▼                    ▼                          │
│                     ┌─────────────────────────────────────┐                │
│                     │         OpenClaw Gateway            │                │
│                     │   (飞书 AI 助手网关 - 本地部署)        │                │
│                     └──────────────┬──────────────────────┘                │
│                                    │                                        │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           业务场景层 (你的实际工作)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐ │
│  │ 🏠 房产经纪  │ │ 🏢 商业地产  │ │ 💰 贷款金融  │ │ 🌐 跨境电商  │ │ 📝 内容 │ │
│  │  房源分析   │ │  不良资产   │ │  CRM集成   │ │  智能穿戴   │ │  运营  │ │
│  │  客户画像   │ │  摊位招商   │ │  利率计算   │ │  产品上架   │ │  多平台 │ │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └───┬────┘ │
│         └─────────────────┴─────────────────┴─────────────────┘            │
│                                    │                                        │
│                                    ▼                                        │
│┌──────────────────────────────────────────────────────────────────────────┐│
││                              AI 能力层                                     ││
│├──────────────────────────────────────────────────────────────────────────┤│
││                                                                          ││
││  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────┐  ││
││  │ Claude Code  │   │ OpenAI Codex │   │ Google Gemini│   │ 国产模型  │  ││
││  │ (主大脑-规划) │   │ (双手-生成)  │   │ (查询-补充)  │   │ (Qwen/   │  ││
││  │  复杂任务拆解 │   │  批量代码生成 │   │  长文档分析  │   │ DeepSeek)│  ││
││  │  架构设计审查 │   │  自动化脚本  │   │  实时信息检索 │   │          │  ││
││  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘   └─────┬────┘  ││
││         └──────────────────┴──────────────────┴─────────────────┘        ││
││                                    │                                     ││
│└────────────────────────────────────┼─────────────────────────────────────┘│
└────────────────────────────────────┼───────────────────────────────────────┘
```

---

## 二、各组件安装配置

### 2.1 Claude Code VSCode 扩展（核心）

#### 安装方式（零代码友好）
```powershell
# 方式1: 官方推荐 - 原生安装 (PowerShell)
# 复制以下命令到 PowerShell 执行
irm https://claude.ai/install.ps1 | iex

# 方式2: WinGet (Windows 自带包管理器)
winget install Anthropic.ClaudeCode

# 方式3: VSCode 扩展市场 (图形界面)
# 1. 打开 VSCode
# 2. Ctrl+Shift+X (打开扩展面板)
# 3. 搜索 "Claude Code"
# 4. 点击安装
```

#### 首次登录
```
1. 安装完成后，VSCode 底部状态栏会出现 "✱ Claude Code"
2. 点击它，或按 Ctrl+Shift+P 输入 "Claude Code"
3. 按提示完成 Anthropic 账号登录
4. 登录成功后即可开始使用
```

#### VSCode 扩展配置
```json
// settings.json (VSCode)
{
  "claudeCode.selectedModel": "default",
  "claudeCode.initialPermissionMode": "default",
  "claudeCode.preferredLocation": "panel",
  "claudeCode.autosave": true,
  "claudeCode.useCtrlEnterToSend": false,
  "claudeCode.enableNewConversationShortcut": true,
  "claudeCode.respectGitIgnore": true
}
```

#### 快捷键配置 (Windows)
```json
// keybindings.json
[
  {
    "key": "ctrl+shift+`",
    "command": "claudeCode.openInNewTab"
  },
  {
    "key": "ctrl+esc",
    "command": "claudeCode.focusInput"
  },
  {
    "key": "alt+k",
    "command": "claudeCode.insertMention"
  }
]
```

### 2.2 Claude Code 共享配置

```json
// ~/.claude/settings.json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "env": {
    "CLAUDE_CODE_GIT_BASH_PATH": "C:\\Program Files\\Git\\bin\\bash.exe"
  },
  "autoUpdatesChannel": "latest",
  "allowedTools": [
    "Bash",
    "Edit",
    "Read",
    "Write",
    "Glob",
    "Grep"
  ]
}
```

### 2.3 OpenClaw 网关（飞书集成）

#### 部署步骤
```bash
# 1. 克隆 OpenClaw 项目
cd D:\openclaw

# 2. 安装依赖
npm install

# 3. 配置 openclaw.json
# 参见下方配置示例

# 4. 启动网关
node openclaw.mjs gateway --port 18789

# 5. 管理面板
openclaw dashboard
```

#### OpenClaw 配置 (openclaw.json)
```json
{
  "apiKey": "sk-cp-xxxxxxxxxxxxxxxx",
  "baseUrl": "https://api.minimax.chat/v1",
  "gateway": {
    "port": 18789,
    "cors": true
  },
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "cli_xxxxxxxx",
      "appSecret": "xxxxxxxx"
    }
  }
}
```

---

## 三、业务场景化 AI 工作流

### 3.1 按时段的工作流（配合作息）

#### 🌅 晨间时段 (6:00-7:30) - 跑步+自动报表
```
你在: 跑步训练
AI 在: 自动生成昨日业务数据报表

使用方法:
1. 跑步前在飞书发送: "@Claude 生成昨日数据报表"
2. OpenClaw 自动触发 Leo 系统的数据分析技能
3. 跑完步在飞书查看结果

涉及技能: property_valuation_skill, analytics_skill
```

#### 🏠 房产时段 (8:00-12:00) - 核心业务
```
你在: 带看、客户谈判
AI 在: 准备房源资料、分析客户意向

使用方法:
1. VSCode 中问 Claude: "分析这个客户的历史行为和偏好"
2. Claude 读取口袋助理 CRM 数据，生成客户画像
3. 带看前问: "生成这套房源的 3 个卖点话术"

涉及技能: customer-portrait, sales-sop, realestate_listing_skill
```

#### 🌐 多业务时段 (13:00-18:00) - 批量处理
```
你在: 管理多个业务线
AI 在: 执行自动化任务、生成内容

使用方法:
1. Codex: "为抖音/小红书/视频号生成本周的 7 条内容脚本"
2. Claude: "审核这些内容是否符合各平台调性"
3. 飞书中: "@Claude 发布今天的房产朋友圈文案"

涉及技能: content_generator_skill, social-auto-publish, douyin_skill
```

#### 📚 学习时段 (19:00-23:00) - 技术提升
```
你在: 学习编程、搭建系统
AI 在: 手把手教学、代码审查

使用方法:
1. Claude Code 扩展中: "教我如何用 Python 读取 Excel 文件"
2. 跟着 Claude 的步骤操作，不懂随时问
3. 完成一个功能后: "审查我刚才写的代码"

涉及技能: code_review_skill, test_driven_development_skill
```

### 3.2 五大业务的 AI 分工

| 业务场景 | AI 主责 | 使用方式 | 示例指令 |
|---------|--------|---------|---------|
| **🏠 房产经纪** | Claude | 客户画像、房源分析 | "分析客户 XXX 的购房偏好，推荐 3 套房源" |
| **🏢 商业地产** | Claude | 市场分析、招商方案 | "生成乐橙荟的摊位招商方案" |
| **💰 贷款金融** | Codex | 计算脚本、报表生成 | "生成贷款利率对比表" |
| **🌐 跨境电商** | Codex | 产品上架、多语言翻译 | "把这款产品信息翻译成英文/日文" |
| **📝 内容运营** | Claude+Codex | 脚本生成、多平台适配 | "生成抖音爆款口播脚本" |

### 3.3 角色分工

#### 模式一: Claude 主导 + Codex 执行
```
Claude (大脑)
    ↓ 拆解任务，输出 SPEC
Codex (双手) → 生成代码文件
    ↓
Claude (审查) → 代码质量检查
```

#### 模式二: 并行互补
```
        ┌→ Claude: 架构分析
问题 ──┼→ Codex: 代码实现
        └→ Gemini: 文档查询
               ↓
          结果整合 (Claude)
```

### 3.3 VSCode 中切换快捷键

```json
// keybindings.json - 快速切换 AI 工具
{
  "key": "ctrl+shift+1",
  "command": "workbench.view.extension.claude-code"
},
{
  "key": "ctrl+shift+2",
  "command": "command palette: openai codex"
},
{
  "key": "ctrl+shift+3",
  "command": "command palette: gemini"
}
```

### 3.4 双屏协作流（飞书 + VSCode）

#### 场景一: 外出带看 + 远程分析
```
┌─────────────────┐     ┌─────────────────┐
│   手机飞书      │◄───►│   电脑 VSCode   │
│                 │     │                 │
│ 你: "客户想要    │     │ Claude:         │
│     200万以内    │     │  1. 查询数据库   │
│     3房2卫"     │     │  2. 筛选房源    │
│                 │     │  3. 生成对比表   │
│ Claude:         │     │                 │
│  "收到，正在     │     │ 你回来后在      │
│   分析..."      │     │ VSCode 查看完整 │
│                 │     │ 分析报告        │
└─────────────────┘     └─────────────────┘
```

#### 场景二: 晨跑听报表
```
1. 跑步前飞书发送: "@Claude 生成昨日业务数据简报"
2. Claude 分析数据，生成语音友好的摘要
3. 跑步时用飞书语音播放
4. 有想法随时语音回复，Claude 记录待办
```

---

## 四、Windows 环境最佳实践

### 4.1 前置依赖

| 组件 | 版本要求 | 用途 |
|------|---------|------|
| Git for Windows | 最新版 | Claude Code 依赖 |
| Node.js | 18+ | OpenClaw 运行 |
| VSCode | 1.98.0+ | Claude Code 扩展 |
| PowerShell | 5.1+ | 脚本执行 |

### 4.2 Git Bash 路径配置

```json
// ~/.claude/settings.json
{
  "env": {
    "CLAUDE_CODE_GIT_BASH_PATH": "C:\\Program Files\\Git\\bin\\bash.exe",
    "GIT_BASH_PATH": "C:\\Program Files\\Git\\bin\\bash.exe"
  }
}
```

### 4.3 环境变量统一

```powershell
# 添加到系统环境变量
[System.Environment]::SetEnvironmentVariable(
  "CLAUDE_CODE_GIT_BASH_PATH",
  "C:\Program Files\Git\bin\bash.exe",
  "User"
)

# 添加到 PATH
$currentPath = [System.Environment]::GetEnvironmentVariable("PATH", "User")
$newPath = $currentPath + ";C:\Users\$env:USERNAME\.local\bin"
[System.Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
```

### 4.4 自动启动脚本（业务版）

#### 晨间启动脚本 (6:00)
```powershell
# scripts/startup/start_morning_routine.ps1
# 晨间启动：自动报表 + OpenClaw

Write-Host "🌅 启动晨间 AI 工作流..." -ForegroundColor Green

# 1. 启动 OpenClaw 网关
$openclawPath = "D:\openclaw"
$gatewayProcess = Start-Process -FilePath "node" `
  -ArgumentList "openclaw.mjs", "gateway", "--port", "18789" `
  -WorkingDirectory $openclawPath `
  -WindowStyle Hidden -PassThru

Write-Host "✅ OpenClaw Gateway 已启动" -ForegroundColor Cyan

# 2. 自动发送昨日报表请求到飞书
# 需要配置飞书 webhook
$feishuWebhook = "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
$reportRequest = @{
  msg_type = "text"
  content = @{ text = "@Claude 生成昨日业务数据简报" }
} | ConvertTo-Json

Invoke-RestMethod -Uri $feishuWebhook -Method Post -Body $reportRequest -ContentType "application/json"

Write-Host "📊 已发送报表生成请求到飞书" -ForegroundColor Cyan
Write-Host "🎉 晨间流程完成！你可以去跑步了，跑完查看报表" -ForegroundColor Green
```

#### 工作时段启动脚本 (8:00)
```powershell
# scripts/startup/start_work_day.ps1
# 工作时段启动：完整 AI 环境

Write-Host "🚀 启动工作时段 AI 环境..." -ForegroundColor Green

# 1. 检查 OpenClaw 是否已运行
$openclawRunning = Get-Process | Where-Object {$_.CommandLine -like "*openclaw*"}
if (-not $openclawRunning) {
    Start-Process -FilePath "node" `
      -ArgumentList "openclaw.mjs", "gateway", "--port", "18789" `
      -WorkingDirectory "D:\openclaw" `
      -WindowStyle Hidden
    Write-Host "✅ OpenClaw Gateway 已启动" -ForegroundColor Cyan
}

# 2. 启动 VSCode 并打开 Leo 项目
Start-Process -FilePath "code" -ArgumentList "D:\桌面\leo_ai_system"
Write-Host "✅ VSCode 已启动" -ForegroundColor Cyan

# 3. 打开 Claude Code 面板（需要手动点击或使用 VSCode 命令）
Write-Host ""
Write-Host "📋 今日工作流建议:" -ForegroundColor Yellow
Write-Host "  1. 按 Ctrl+Shift+` 打开 Claude Code" -ForegroundColor Gray
Write-Host "  2. 查看晨间报表" -ForegroundColor Gray
Write-Host "  3. 开始房产业务工作" -ForegroundColor Gray
Write-Host ""
Write-Host "🏠 房产工作快捷指令:" -ForegroundColor Cyan
Write-Host '     "分析今日客户预约"' -ForegroundColor Gray
Write-Host '     "生成房源推荐清单"' -ForegroundColor Gray
Write-Host '     "准备客户 XX 的带看资料"' -ForegroundColor Gray
```

#### 学习时段启动脚本 (19:00)
```powershell
# scripts/startup/start_learning_mode.ps1
# 学习时段启动：专注编程学习

Write-Host "📚 进入学习模式..." -ForegroundColor Green

# 1. 启动 VSCode
Start-Process -FilePath "code" -ArgumentList "D:\桌面\leo_ai_system"

# 2. 显示今日学习目标建议
Write-Host ""
Write-Host "🎯 建议学习路径:" -ForegroundColor Yellow
Write-Host "  1. Python 基础 → 文件读写" -ForegroundColor Gray
Write-Host "  2. 数据处理 → Excel/CSV 操作" -ForegroundColor Gray
Write-Host "  3. 自动化 → 脚本编写" -ForegroundColor Gray
Write-Host ""
Write-Host "💡 Claude Code 学习模式:" -ForegroundColor Cyan
Write-Host "  - 直接问：'教我如何用 Python 做 XX'" -ForegroundColor Gray
Write-Host "  - 跟着 Claude 的步骤一步一步做" -ForegroundColor Gray
Write-Host "  - 不懂随时打断问" -ForegroundColor Gray
Write-Host ""
Write-Host "⌨️ 常用快捷键:" -ForegroundColor Yellow
Write-Host "  Ctrl+Shift+` : 打开 Claude Code" -ForegroundColor Gray
Write-Host "  Ctrl+Esc     : 切换焦点" -ForegroundColor Gray
Write-Host "  Alt+K        : 引用当前选中代码" -ForegroundColor Gray
```

---

## 五、项目集成配置 (Leo AI System 业务版)

### 5.1 CLAUDE.md 项目规范

```markdown
# Leo AI System - Context Registry

## 集成系统

### Claude Code (v2.1.63)
| 项目 | 说明 |
|------|------|
| **版本** | 2.1.63 (最新) |
| **子代理** | `.claude/agents/` |
| **MCP配置** | `mcp.json` |
| **Hooks** | `.claude/hooks.json` |

### OpenClaw (飞书 AI 助手)
| 项目 | 信息 |
|------|------|
| **本地目录** | `D:\openclaw` |
| **版本** | 2026.03.03 |
| **启动命令** | `node openclaw.mjs gateway --port 18789` |
| **管理面板** | `openclaw dashboard` |

## 双引擎协作规则

**简单记忆**: Claude 想 → Claude 拆 → Codex 干 → Claude 查 → Claude 收

| Claude Code (大脑) | Codex (双手) |
|---|---|
| 架构设计、代码审查、重构、规划 | 脚手架搭建、模板生成、批量修改 |

**冲突避免**: 不同时编辑同一文件；Codex 不改 CLAUDE.md；Claude 不做批量创建
```

### 5.2 MCP 配置 (mcp.json)

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@executeautomation/playwright-mcp-server"],
      "description": "浏览器自动化 - 用于房产网站数据采集"
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-github"],
      "description": "GitHub 集成 - 代码托管和协作"
    },
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "data/leo_business.db"],
      "description": "本地数据库 - 房产客户数据、业务数据"
    }
  }
}
```

### 5.3 业务技能快速索引

根据你的五大业务，这是推荐使用的技能：

```markdown
# 业务技能速查表

## 🏠 房产经纪 (优先级: P0)
| 技能 | 用途 | 调用方式 |
|------|------|---------|
| customer-portrait | 客户画像分析 | "分析客户 XX 的购房偏好" |
| realestate_listing_skill | 房源管理 | "生成房源推荐清单" |
| sales-sop | 销售流程指导 | "准备带看话术" |
| property_valuation_skill | 房产估值 | "评估这套房子的市场价" |

## 🏢 商业地产 (优先级: P1)
| 技能 | 用途 | 调用方式 |
|------|------|---------|
| market_analysis_skill | 市场分析 | "分析乐橙荟周边商业环境" |
| leasing_management_skill | 招商管理 | "生成摊位招商方案" |
| competitor_monitor_skill | 竞品监控 | "监控周边商业项目动态" |

## 💰 贷款金融 (优先级: P1)
| 技能 | 用途 | 调用方式 |
|------|------|---------|
| loan_calculator_skill | 贷款计算 | "计算月供和总利息" |
| mortgage_calculator_skill | 房贷计算 | "对比等额本息和等额本金" |
| interest_calculator_skill | 利息计算 | "计算提前还款节省金额" |
| credit_check_skill | 信用查询 | "评估客户贷款资质" |
| pocket_assistant_skill | 口袋助理集成 | "同步客户到 CRM" |

## 🌐 跨境电商 (优先级: P2)
| 技能 | 用途 | 调用方式 |
|------|------|---------|
| amazon_skill | 亚马逊运营 | "优化产品 listing" |
| shopify_skill | 独立站搭建 | "生成 Shopify 店铺结构" |
| aliexpress_skill | 速卖通运营 | "生成多语言产品描述" |
| translate_skill | 多语言翻译 | "翻译成英文/日文/德文" |
| price_analysis_skill | 价格分析 | "分析竞品定价策略" |

## 📝 内容运营 (优先级: P1)
| 技能 | 用途 | 调用方式 |
|------|------|---------|
| content_generator_skill | 内容生成 | "生成抖音口播脚本" |
| douyin_skill | 抖音发布 | "发布房产短视频" |
| xiaohongshu_skill | 小红书发布 | "生成小红书爆款笔记" |
| wechat_skill | 微信运营 | "生成朋友圈文案" |
| video_skill | 视频处理 | "批量添加字幕" |
| copywriting_skill | 文案生成 | "写 10 条房产标题" |
```

### 5.4 快捷指令模板

在 VSCode 中，你可以直接复制这些指令使用：

```
【房产工作】
- "分析今日预约客户的背景，生成带看准备清单"
- "根据客户预算 200 万、3 房需求，推荐 5 套房源并对比"
- "生成这套别墅的小红书推广文案"

【商业工作】
- "生成乐橙荟 Q2 招商方案，包含摊位规划、定价策略"
- "分析周边 3 公里内竞品商业项目"

【贷款工作】
- "计算贷款 100 万、30 年、利率 3.8% 的月供和总利息"
- "对比等额本息和等额本金 10 年期的差异"
- "评估客户月收入 2 万、负债 5000 的贷款资质"

【内容工作】
- "生成本周抖音内容日历，7 条视频脚本"
- "把这套房源介绍改写成小红书风格"
- "生成 5 条房产朋友圈文案，不同风格"

【学习编程】
- "教我如何用 Python 读取 Excel 文件并筛选数据"
- "解释这段代码的作用，一步一步讲"
- "帮我调试这个错误：[粘贴错误信息]"
```

---

## 六、故障排除

### 6.1 常见问题

| 问题 | 症状 | 解决方案 |
|------|------|---------|
| Git Bash 未找到 | "Cannot find bash" | 设置 `CLAUDE_CODE_GIT_BASH_PATH` |
| 扩展不显示 | Spark 图标缺失 | 重启 VSCode，检查版本 1.98.0+ |
| 权限被拒绝 | 命令执行失败 | 检查 `allowedTools` 配置 |
| OpenClaw 连接失败 | 飞书无响应 | 检查端口 18789，运行 `openclaw doctor` |
| Message ordering conflict | 飞书重复消息 | 清理会话历史：`rm -rf ~/.openclaw/agents/*/sessions/*` |
| 房产数据查询慢 | 客户画像加载慢 | 检查口袋助理 API 连接，或改用本地缓存 |
| 内容生成失败 | 抖音/小红书发布失败 | 检查平台 API 授权是否过期 |
| 贷款计算错误 | 利率计算不准确 | 确认利率数据是否最新，建议添加数据来源标注 |

### 6.2 诊断命令

```bash
# Claude Code 诊断
claude doctor

# OpenClaw 诊断
openclaw doctor --fix

# 检查端口占用
netstat -ano | findstr 18789

# 检查进程
Get-Process | Where-Object {$_.ProcessName -like "*node*"}
```

---

## 七、分时段推荐工作流

### 7.1 晨间自动化流程 (6:00-7:30)
```
1. 执行晨间启动脚本
   ./scripts/startup/start_morning_routine.ps1

2. AI 自动生成内容：
   - 昨日业务数据简报
   - 今日待办事项汇总
   - 市场动态监控报告

3. 跑步时飞书语音播放报表

4. 有想法随时语音回复，AI 记录待办
```

### 7.2 房产核心业务流程 (8:00-12:00)
```
1. 执行工作时段启动脚本
   ./scripts/startup/start_work_day.ps1

2. 查看晨间报表，了解今日重点

3. 客户准备阶段 (VSCode + Claude):
   - "分析今日预约客户背景"
   - "生成带看准备清单"
   - "准备房源对比表"

4. 带看执行阶段 (飞书 + OpenClaw):
   - 外出时飞书语音查询房源信息
   - "@Claude 查询 XX 小区最新成交价"

5. 跟进阶段 (VSCode):
   - 回到电脑前更新客户状态
   - "生成客户跟进话术"
```

### 7.3 多业务批量处理流程 (13:00-18:00)
```
1. 内容生成批量任务 (Codex):
   - "为抖音/小红书/视频号生成本周 7 条内容"
   - "生成多平台适配版本"

2. 业务数据分析 (Claude):
   - "分析本周房产成交数据"
   - "生成贷款业务周报"

3. 自动化执行 (OpenClaw + 飞书):
   - "@Claude 发布今天的房产朋友圈文案"
   - "定时发送客户跟进提醒"
```

### 7.4 学习开发流程 (19:00-23:00)
```
1. 执行学习模式启动脚本
   ./scripts/startup/start_learning_mode.ps1

2. 编程学习 (Claude Code 手把手教学):
   - "教我如何用 Python 读取 Excel"
   - "跟着 Claude 的步骤一步步操作"
   - "不懂随时打断问"

3. 项目实践：
   - 用刚学的知识解决实际业务问题
   - "帮我写一个计算房贷利率的脚本"

4. 代码审查：
   - "审查我今天写的代码"
   - "解释这段代码的优化空间"
```

### 7.5 技能调用优先级（业务版）

| 业务任务 | 首选 AI | 次选 AI | 示例指令 |
|---------|--------|--------|---------|
| **客户画像分析** | Claude | Gemini | "分析客户 XX 的背景和偏好" |
| **房源推荐** | Claude | - | "根据需求推荐 5 套房源" |
| **营销文案** | Claude | Codex | "生成小红书推广文案" |
| **数据报表** | Codex | Claude | "生成本周成交数据报表" |
| **贷款计算** | Codex | Claude | "计算月供和总利息" |
| **内容批量生成** | Codex | Claude | "生成本周 7 条视频脚本" |
| **代码学习** | Claude | - | "教我如何用 Python 做 XX" |
| **代码生成** | Codex | Claude | "生成一个房贷计算器" |
| **代码审查** | Claude | Codex | "审查这段代码的问题" |
| **市场信息查询** | Gemini | Claude | "查询最新的房贷政策" |
| **文档阅读** | Gemini | Claude | "总结这份合同的重点" |

---

## 八、业务数据安全与隐私

### 8.1 客户数据保护原则

作为房产和金融业务，客户数据安全至关重要：

| 数据类型 | 处理方式 | 说明 |
|---------|---------|------|
| 客户姓名电话 | 脱敏处理 | 使用 "客户A"、"138****8888" 代替 |
| 房产地址 | 模糊化 | 使用 "鄞州区 XX 小区" 而非具体门牌 |
| 成交价格 | 区间化 | 使用 "200-250 万区间" 而非精确数字 |
| 贷款信息 | 授权后使用 | 仅处理客户明确授权的数据 |

### 8.2 配置示例（数据脱敏）

```json
// ~/.claude/settings.json
{
  "permissions": {
    "allowDestructiveOperations": false,
    "requireApprovalFor": ["Bash", "Write", "Edit"],
    "dataHandling": {
      "maskPhoneNumbers": true,
      "maskNames": true,
      "confirmBeforeProcessing": ["客户数据", "财务数据"]
    }
  }
}
```

### 8.3 代码安全（学习阶段）

- **本地优先**: Claude Code 默认不传输代码用于训练
- **敏感数据**: 不在代码中硬编码 API Key、密码
- **环境变量**: 使用 `.env` 文件存储敏感配置
- **Git 忽略**: 确保 `.env` 已在 `.gitignore` 中

### 8.4 飞书/OpenClaw 安全

```yaml
# OpenClaw 安全配置建议
security:
  # 会话定期清理（防止数据累积）
  session_cleanup:
    enabled: true
    interval: "weekly"
    retention_days: 30

  # 敏感关键词过滤
  content_filter:
    enabled: true
    sensitive_keywords:
      - "身份证号"
      - "银行卡号"
      - "密码"
    action: "warn_and_log"

  # 访问日志
  audit_log:
    enabled: true
    log_path: "logs/openclaw/audit.log"
```

### 8.5 安全操作清单

```markdown
- [ ] 不在公共频道发送客户敏感信息
- [ ] 定期清理飞书会话历史（每月一次）
- [ ] API Key 存储在环境变量，不在代码中
- [ ] 代码提交前检查是否包含敏感数据
- [ ] 使用 Git worktree 隔离敏感项目
```

| 任务类型 | 首选工具 | 次选工具 | 原因 |
|---------|---------|---------|------|
| 架构设计 | Claude | Gemini | Claude 上下文理解更强 |
| 代码生成 | Codex | Claude | Codex 批量生成更快 |
| 代码审查 | Claude | Codex | Claude 分析更深入 |
| Bug 修复 | Claude | Gemini | 需要根因分析 |
| 文档编写 | Claude | Gemini | 结构化输出更好 |
| 快速查询 | Gemini | Claude | Gemini 响应更快 |

---

## 八、安全与隐私

### 8.1 代码安全

- **本地优先**: Claude Code 默认不传输代码用于训练
- **Git 工作区**: 使用 `--worktree` 隔离敏感任务
- **权限控制**: 配置 `allowedTools` 限制危险操作

### 8.2 配置安全

```json
// ~/.claude/settings.json
{
  "permissions": {
    "allowDestructiveOperations": false,
    "requireApprovalFor": ["Bash", "Write", "Edit"]
  }
}
```

---

## 九、参考资源

| 资源 | 链接 |
|------|------|
| Claude Code 官方文档 | https://code.claude.com/docs |
| VSCode 扩展指南 | https://code.claude.com/docs/en/vs-code |
| Windows 安装指南 | https://code.claude.com/docs/en/setup |
| GitHub 仓库 | https://github.com/anthropics/claude-code |

---

## 十、快速上手指南（新手专用）

### 第一步：安装（10分钟）
```powershell
# 1. 安装 Claude Code
irm https://claude.ai/install.ps1 | iex

# 2. VSCode 安装 Claude Code 扩展
# Ctrl+Shift+X → 搜索 "Claude Code" → 安装

# 3. 首次登录
# 点击 VSCode 底部 "✱ Claude Code" → 按提示登录
```

### 第二步：第一句指令（5分钟）
在 VSCode 的 Claude Code 面板中输入：
```
"你好，我是做房产经纪的，帮我分析一下如何用 AI 提升工作效率"
```

### 第三步：实战练习（30分钟）
```
1. 让 Claude 帮你写一个简单的 Python 脚本
   "教我写一个简单的计算器程序"

2. 学习如何引用文件
   打开任意文件 → 选中代码 → Alt+K → 提问

3. 尝试业务场景
   "帮我写一段房产朋友圈文案"
```

### 第四步：每日使用
```
每天工作时：
1. 打开 VSCode，自动启动 Claude Code
2. 遇到问题时直接问
3. 需要批量处理时尝试使用技能
4. 外出时用飞书保持连接
```

---

## 十一、进阶学习路径

### 第 1 周：熟悉界面
- [ ] 学会打开和关闭 Claude Code 面板
- [ ] 学会使用 @ 引用文件
- [ ] 学会使用快捷键

### 第 2 周：业务应用
- [ ] 用 Claude 分析一个客户案例
- [ ] 生成一份房源推广文案
- [ ] 尝试用飞书远程查询数据

### 第 3 周：技能探索
- [ ] 尝试 5 个不同的业务技能
- [ ] 学会在飞书中调用技能
- [ ] 记录最常用的技能清单

### 第 4 周：编程入门
- [ ] 学会用 Python 读取 Excel
- [ ] 学会写简单的数据处理脚本
- [ ] 学会让 Claude 帮你调试代码

---

*文档版本: 2026-03-04*
*适用 Leo AI System v2.0*
*用户场景: 房产/商业/金融/电商/内容 五大业务*
