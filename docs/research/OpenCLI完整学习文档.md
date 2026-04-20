# OpenCLI 完整学习文档

> **版本**: v1.7.3 | **更新时间**: 2026-04-15
> **官方仓库**: https://github.com/jackwener/opencli
> **npm**: @jackwener/opencli
> **文档来源**: 官方仓库完整文档（README、SKILL.md、docs/）

---

## 一、项目概述

**OpenCLI** 是一个将网站、浏览器会话、Electron 应用和本地工具统一转换为 CLI 的工具。

### 核心定位

- **把网站变成 CLI**：87+ 内置适配器，开箱即用
- **直接驱动浏览器**：AI Agent 实时点击、输入、提取、截图
- **把新网站生成 CLI**：通过 explore/synthesize/generate 自动生成

### 六大亮点

| 亮点 | 说明 |
|------|------|
| 🖥️ **桌面应用控制** | 通过 CDP 直接控制 Electron 应用（Cursor、Codex、ChatGPT、Notion 等） |
| 🌐 **浏览器自动化** | AI Agent 直接控制浏览器：点击、输入、提取、截图，完全可编程 |
| 🔐 **账号安全** | 复用 Chrome 登录态，凭证永不离开浏览器 |
| 🤖 **AI Agent 就绪** | explore 发现 API、synthesize 生成适配器、cascade 探测认证策略 |
| 💰 **零 LLM 成本** | 运行时不消耗 token，10000 次也不花一分钱 |
| 🔁 **确定性输出** | 相同命令、相同输出结构，每次一致，可管道化 |

---

## 二、系统架构

### 双引擎架构

```
┌─────────────────────────────────────────────────────────────┐
│                    opencli CLI (Commander.js)               │
├─────────────────────────────────────────────────────────────┤
│                      引擎层                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐          │
│  │   Registry   │  │   Dynamic    │  │   Output   │          │
│  │  (命令注册)   │  │   Loader    │  │ Formatter  │          │
│  └──────────────┘  └──────────────┘  └────────────┘          │
├─────────────────────────────────────────────────────────────┤
│                      适配器层                                │
│  ┌─────────────────┐  ┌──────────────────────────┐         │
│  │    Pipeline     │  │  TypeScript Adapters     │         │
│  │  (声明式)       │  │  (browser/desktop/AI)    │         │
│  └─────────────────┘  └──────────────────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                      连接层                                  │
│  ┌─────────────────┐  ┌──────────────────────────┐         │
│  │ Browser Bridge  │  │  CDP (Chrome DevTools)   │         │
│  │ (Extension+WS)  │  │  (Electron apps)         │         │
│  └─────────────────┘  └──────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 通信流程

```
┌─────────────┐     WebSocket      ┌──────────────┐     Chrome API     ┌─────────┐
│   opencli   │ ◄──────────────► │  micro-daemon │ ◄──────────────► │  Chrome  │
│  (Node.js)  │   localhost:19825 │  (auto-start) │    Extension       │ Browser  │
└─────────────┘                   └──────────────┘                   └─────────┘
```

---

## 三、认证策略（5 级体系）

OpenCLI 使用 5 级认证策略，按优先级自动探测：

| Tier | 策略 | 原理 | 速度 | 场景 |
|------|------|------|------|------|
| **1** | `public` | 直接 fetch，无认证 | ⚡ ~1s | HackerNews, V2EX |
| **2** | `cookie` | 复用 Chrome Cookie | 🔄 ~7s | Bilibili, Zhihu, Reddit |
| **2.5** | `localStorage Bearer` | JWT 存 localStorage | 🔄 ~7s | 现代 SaaS（Linear, Notion） |
| **3** | `header` | CSRF token + Bearer | 🔄 ~7s | Twitter GraphQL |
| **4** | `intercept` | Store Action + XHR 拦截 | 🔄 ~10s | 小红书（Pinia + XHR） |
| **5** | `ui` | DOM 解析（最后手段） | 🐌 ~15s+ | 遗留网站 |

### 策略决策树

```
fetch(url) 直接能拿到？
  → ✅ Tier 1: public
  → ❌ fetch(url, {credentials:'include'}) 带 Cookie 能拿到？
       → ✅ Tier 2: cookie
       → ❌ localStorage 有 token，Bearer header 能拿到？
              → ✅ Tier 2.5: localStorage Bearer
              → ❌ 加 CSRF header 后能拿到？
                     → ✅ Tier 3: header
                     → ❌ 网站有 Pinia/Vuex Store？
                            → ✅ Tier 4: intercept
                            → ❌ Tier 5: ui（UI 自动化）
```

---

## 四、命令分类总览

### 4.1 内置命令（87+ 适配器）

| 类别 | 平台数 | 代表平台 | 命令示例 |
|------|--------|----------|----------|
| **社交媒体** | 15 | Twitter/X、小红书、知乎、B站、微博、YouTube、Reddit | `twitter search`, `xiaohongshu search`, `bilibili hot` |
| **AI 工具** | 10 | Cursor、Codex、ChatGPT、Notion、Grok | `cursor send`, `notion write`, `grok ask` |
| **新闻资讯** | 12 | HackerNews、36kr、路透社、彭博社 | `hackernews top`, `36kr hot` |
| **视频/播客** | 5 | B站、YouTube、小宇宙、豆瓣 | `youtube transcript`, `bilibili download` |
| **电商/购物** | 4 | Amazon、1688、京东、什么值得买 | `amazon bestsellers`, `1688 search` |
| **财经/股票** | 4 | Yahoo Finance、雪球、Barchart | `yahoo-finance quote`, `xueqiu stock` |
| **阅读/知识** | 8 | 微信读书、Wikipedia、Arxiv、Stack Overflow | `weread shelf`, `arxiv search` |
| **招聘/职场** | 3 | BOSS直聘、LinkedIn、Steam | `boss search`, `linkedin timeline` |
| **社区/论坛** | 4 | V2EX、豆瓣、微博 | `v2ex hot`, `douban top250` |
| **工具/其他** | 5 | 飞书、Google、Web | `feishu new`, `google search` |

### 4.2 桌面应用适配器（8 个）

| 应用 | 说明 | 命令数 |
|------|------|--------|
| **Cursor** | 控制 Cursor IDE | 13 |
| **Codex** | 驱动 OpenAI Codex CLI Agent | 11 |
| **Antigravity** | 控制 Antigravity Ultra | 7 |
| **ChatGPT App** | 自动化 ChatGPT macOS 客户端 | 6 |
| **ChatWise** | 多 LLM 客户端 | 9 |
| **Notion** | 搜索、读取、写入 Notion 页面 | 7 |
| **Discord** | Discord 桌面版消息/频道 | 7 |
| **Doubao App** | 控制豆包桌面应用 | 7 |

### 4.3 核心系统命令

```bash
# 诊断
opencli doctor              # 检查扩展 + daemon 连接状态
opencli daemon stop         # 停止 daemon

# 发现
opencli list                # 列出所有命令（支持 -f json/yaml）
opencli explore <url>       # 深度探索网站 API
opencli synthesize <site>   # 从探索产物生成适配器
opencli generate <url>     # 一键：explore → synthesize → register
opencli cascade <url>       # 认证策略级联探测

# 浏览器控制
opencli browser open <url>  # 打开 URL
opencli browser state       # 获取页面元素状态（带 [N] 索引）
opencli browser click <N>   # 点击元素
opencli browser type <N> "text"  # 输入文本
opencli browser wait        # 等待（time/selector/text）
opencli browser eval       # 执行 JS（只读）
opencli browser network     # 捕获 API 请求
opencli browser screenshot  # 截图

# 适配器开发
opencli browser init <site>/<cmd>   # 生成适配器脚手架
opencli browser verify <site>/<cmd>  # 验证适配器
```

---

## 五、AI Agent 工作流（完整流程）

### 5.1 快速模式（一键生成）

```bash
# 4 步完成：explore → synthesize → register → test
opencli generate https://example.com --goal "hot"
```

### 5.2 完整模式（深度探索）

```bash
# Step 1: 深度探索
opencli explore https://example.com --site mysite

# Step 2: 合成适配器
opencli synthesize mysite

# Step 3: 认证策略探测
opencli cascade https://api.example.com/data

# Step 4: 验证
opencli mysite hot --limit 3 -v
```

### 5.3 浏览器探索工作流

```bash
# 0. 打开页面
opencli browser open https://example.com

# 1. 观察元素
opencli browser state                    # 返回带 [N] 索引的元素列表

# 2. 首次抓包
opencli browser network                  # 列出捕获的 JSON API 请求

# 3. 模拟交互（触发懒加载 API）
opencli browser click <N>               # 点击按钮触发深层 API

# 4. 二次抓包
opencli browser network                  # 找出新触发的 API

# 5. 查看响应
opencli browser network --detail <N>     # 查看完整响应体

# 6. 验证 API 可复现
opencli browser eval "fetch(...).then(r=>r.json())"
```

---

## 六、适配器开发指南

### 6.1 适配器模板（Tier 2 Cookie 模式）

```typescript
// clis/<site>/<name>.js
import { cli, Strategy } from '@jackwener/opencli/registry';

cli({
  site: 'mysite',
  name: 'mycommand',
  description: '一句话描述',
  domain: 'www.example.com',
  strategy: Strategy.COOKIE,
  browser: true,
  args: [
    { name: 'limit', type: 'int', default: 20 },
  ],
  columns: ['rank', 'title', 'value'],
  func: async (page, kwargs) => {
    await page.goto('https://www.example.com/target-page');
    const data = await page.evaluate(`(async () => {
      const res = await fetch('/api/target', { credentials: 'include' });
      const d = await res.json();
      return (d.data?.items || []).map(item => ({
        title: item.title,
        value: item.value,
      }));
    })()`);
    return (data as any[]).slice(0, kwargs.limit).map((item, i) => ({
      rank: i + 1,
      title: item.title || '',
      value: item.value || '',
    }));
  },
});
```

### 6.2 Tier 1 Public 模式（无浏览器）

```typescript
import { cli, Strategy } from '@jackwener/opencli/registry';

cli({
  site: 'hn',
  name: 'top',
  description: 'Top Hacker News stories',
  domain: 'news.ycombinator.com',
  strategy: Strategy.PUBLIC,
  browser: false,           // 无需浏览器
  args: [{ name: 'limit', type: 'int', default: 5 }],
  columns: ['rank', 'title', 'score', 'url'],
  func: async (_page, kwargs) => {
    const resp = await fetch('https://hacker-news.firebaseio.com/v0/topstories.json');
    const ids = await resp.json();
    return Promise.all(
      ids.slice(0, kwargs.limit).map(async (id: number, i: number) => {
        const item = await (await fetch(`https://hacker-news.firebaseio.com/v0/item/${id}.json`)).json();
        return { rank: i + 1, title: item.title, score: item.score, url: item.url ?? '' };
      })
    );
  },
});
```

### 6.3 Tier 3 Header 模式（如 Twitter）

```typescript
import { cli, Strategy } from '@jackwener/opencli/registry';
import { AuthRequiredError } from '@jackwener/opencli/errors';

cli({
  site: 'twitter',
  name: 'mycommand',
  description: '一句话描述',
  domain: 'x.com',
  strategy: Strategy.HEADER,
  browser: true,
  args: [{ name: 'limit', type: 'int', default: 20 }],
  columns: ['rank', 'name', 'value'],
  func: async (page, kwargs) => {
    await page.goto('https://x.com');
    const data = await page.evaluate(`(async () => {
      const ct0 = document.cookie.match(/ct0=([^;]+)/)?.[1];
      if (!ct0) return { error: 'Not logged in' };
      const bearer = 'YOUR_BEARER_TOKEN';
      const res = await fetch('/i/api/graphql/QUERY_ID/Endpoint', {
        headers: {
          'Authorization': 'Bearer ' + bearer,
          'X-Csrf-Token': ct0,
          'X-Twitter-Auth-Type': 'OAuth2Session',
        },
        credentials: 'include',
      });
      return res.json();
    })()`);
    if ((data as any).error) throw new AuthRequiredError('x.com');
    return [];
  },
});
```

---

## 七、输出格式

```bash
# 支持的格式
-f table    # 富文本表格（默认）
-f json     # JSON（管道化、传给 AI）
-f yaml     # YAML（人类可读）
-f md       # Markdown
-f csv      # CSV
-v          # 详细模式：展示调试步骤
```

---

## 八、退出码规范

| 退出码 | 含义 | 触发场景 |
|--------|------|----------|
| `0` | 成功 | 命令正常完成 |
| `1` | 通用错误 | 未分类的意外错误 |
| `2` | 用法错误 | 参数错误或未知命令 |
| `66` | 无数据 | 命令返回空结果 |
| `69` | 服务不可用 | Browser Bridge 未连接 |
| `75` | 临时失败 | 命令超时，可重试 |
| `77` | 需要认证 | 未登录目标网站 |
| `78` | 配置错误 | 凭证缺失或配置有误 |
| `130` | 中断 | Ctrl-C / SIGINT |

---

## 九、环境变量配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `OPENCLI_DAEMON_PORT` | `19825` | daemon-extension 通信端口 |
| `OPENCLI_WINDOW_FOCUSED` | `false` | 设为 `1` 时 automation 窗口在前台打开 |
| `OPENCLI_BROWSER_CONNECT_TIMEOUT` | `30` | 浏览器连接超时（秒） |
| `OPENCLI_BROWSER_COMMAND_TIMEOUT` | `60` | 单个浏览器命令超时（秒） |
| `OPENCLI_BROWSER_EXPLORE_TIMEOUT` | `120` | explore/record 操作超时（秒） |
| `OPENCLI_CDP_ENDPOINT` | — | Chrome DevTools Protocol 端点 |
| `OPENCLI_CDP_TARGET` | — | 按 URL 子串过滤 CDP target |
| `OPENCLI_VERBOSE` | `false` | 启用详细日志 |

---

## 十、常见问题与解决方案

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| "Extension not connected" | 扩展未启用 | 检查 `chrome://extensions` 中扩展已启用 |
| attach failed: chrome-extension:// | 其他扩展冲突 | 禁用 1Password 等扩展 |
| 空数据 / Unauthorized | 登录态过期 | 在 Chrome 中重新登录目标网站 |
| Node API 错误 | Node.js < 21 | 升级到 Node.js >= 21 |
| daemon 问题 | 守护进程异常 | `curl localhost:19825/status` 检查 |

---

## 十一、与 LEO 系统的集成建议

### 11.1 集成架构

```
┌─────────────────────────────────────────────────────────────┐
│                   LEO System                                │
├─────────────────────────────────────────────────────────────┤
│  技能层                                                        │
│  ├─ opencli-* skills (已安装)                              │
│  └─ 自定义技能                                                │
│                                                              │
│  执行层                                                        │
│  ├─ subprocess 调用 opencli                                  │
│  └─ 输出解析 (JSON/YAML)                                     │
│                                                              │
│  数据层                                                        │
│  ├─ 社交媒体监控 → opencli twitter/xiaohongshu/bilibili    │
│  ├─ 电商数据   → opencli amazon/1688/jd                     │
│  ├─ 财经数据   → opencli yahoo-finance/xueqiu               │
│  └─ AI 工具   → opencli cursor/notion/codex                 │
└─────────────────────────────────────────────────────────────┘
```

### 11.2 LEO 场景应用

| LEO 模块 | OpenCLI 命令 | 说明 |
|----------|-------------|------|
| **竞品监控** | `opencli amazon search "智能手表"` | 电商搜索 |
| **社交监控** | `opencli xiaohongshu search "关键词"` | 小红书监控 |
| **热点追踪** | `opencli bilibili hot` | B站热门 |
| **财经数据** | `opencli yahoo-finance quote AAPL` | 股票行情 |
| **内容获取** | `opencli zhihu download <url>` | 导出文章 |
| **媒体下载** | `opencli twitter download <user>` | 社交媒体下载 |
| **AI 自动化** | `opencli cursor send "解释代码"` | 桌面应用控制 |

### 11.3 快速调用示例

```python
# LEO 技能中调用 OpenCLI
import subprocess
import json

def get_bilibili_hot(limit=10):
    result = subprocess.run(
        ["opencli", "bilibili", "hot", "-f", "json"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0:
        return json.loads(result.stdout)
    return None

def search_xiaohongshu(keyword, limit=20):
    result = subprocess.run(
        ["opencli", "xiaohongshu", "search", keyword, "-f", "json", "--limit", str(limit)],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0:
        return json.loads(result.stdout)
    return None
```

---

## 十二、最佳实践

### 12.1 工具选择优先级

```
OpenCLI 有内置适配器？ → 直接用（零成本、无需配置）
OpenCLI 没有？         → web-access CDP 浏览器
复杂多步 Agent 任务？  → browser-use
高频批量操作？         → Playwright MCP
```

### 12.2 浏览器控制最佳实践

| 规则 | 说明 |
|------|------|
| **优先 state** | 用 `state` 获取元素索引，不用 screenshot |
| **优先 API** | 发现 JSON API 后用 fetch，不用 DOM 解析 |
| **链式调用** | 用 `&&` 合并多个操作，减少开销 |
| **wait 等待** | SPA 页面操作后加 wait，避免竞态 |
| **eval 只读** | eval 只用于数据提取，不用它点击/输入 |

### 12.3 适配器开发最佳实践

| 规范 | 说明 |
|------|------|
| **位置参数优先** | 主语用位置参数（search "query"），可选参数用 flag（--limit） |
| **错误分类** | 使用 CliError 子类（AuthRequiredError、EmptyResultError） |
| **避免 any** | TypeScript strict 模式，尽量避免 any |
| **IIFE 包装** | evaluate 内嵌大段 JS 时用 IIFE 避免变量冲突 |

---

## 十三、参考链接

| 资源 | URL |
|------|-----|
| GitHub 仓库 | https://github.com/jackwener/opencli |
| npm 包 | https://www.npmjs.com/package/@jackwener/opencli |
| 中文 README | https://github.com/jackwener/opencli/blob/main/README.zh-CN.md |
| 完整适配器列表 | https://github.com/jackwener/opencli/blob/main/docs/adapters/index.md |
| 对比指南 | https://github.com/jackwener/opencli/blob/main/docs/comparison.md |
| 开发者贡献指南 | https://github.com/jackwener/opencli/blob/main/docs/developer/contributing.md |
| 架构文档 | https://github.com/jackwener/opencli/blob/main/docs/developer/architecture.md |
| AI 工作流 | https://github.com/jackwener/opencli/blob/main/docs/developer/ai-workflow.md |

---

## 十四、OpenCLI vs 其他方案对比

| 维度 | **OpenCLI** | browser-use | Playwright MCP | web-access |
|------|------------|-------------|----------------|------------|
| **Token 消耗** | **零** | 中等 | 最低 | 中等 |
| **平台覆盖** | **87+ 内置** | 无内置 | 无内置 | 通用 |
| **桌面应用** | **8 个适配器** | ❌ | ❌ | ❌ |
| **学习成本** | 低 | 中 | 中 | 中 |
| **AI 集成** | 内置 explore | 内置 Agent | 需配合 LLM | 无 |
| **反爬虫** | 部分内置 | 云服务 | 无 | 无 |

**结论**：OpenCLI 是**首选**工具（零成本、高覆盖），其他工具作为补充。

---

*文档整理时间：2026-04-15*
*基于官方仓库完整文档整理*
