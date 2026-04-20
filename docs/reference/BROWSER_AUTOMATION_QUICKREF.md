# 浏览器自动化快速参考

> 无订阅最佳实践：OpenCLI + CDP Proxy

## 工具状态

| 工具 | 状态 | 位置 |
|------|------|------|
| OpenCLI | ✅ | `opencli.cmd` (Windows) |
| CDP Proxy | ✅ | `http://localhost:3456` |

---

## OpenCLI 常用命令

### 社交媒体

```bash
# B站
opencli bilibili hot --limit 10 -f json
opencli bilibili search "关键词" -f json

# 小红书
opencli xiaohongshu search "关键词" -f json
opencli xiaohongshu download <url> --output ./downloads

# Twitter/X
opencli twitter trending -f json
opencli twitter search "query" -f json

# Reddit
opencli reddit hot -f json
```

### 电商

```bash
# Amazon
opencli amazon bestsellers electronics -f json
opencli amazon search "商品" -f json

# 1688
opencli 1688 search "商品" -f json
```

### 新闻/社区

```bash
# HackerNews
opencli hackernews top -f json

# V2EX
opencli v2ex hot -f json

# 知乎
opencli zhihu hot -f json
```

### 诊断

```bash
opencli doctor                              # 检查状态
opencli list -f json | grep <平台>          # 查看命令
```

---

## CDP Proxy API

```bash
CDP="http://localhost:3456"

# 基础
curl -s $CDP/targets                         # 列出标签页
curl -s "$CDP/info?target=ID"              # 页面信息
curl -s "$CDP/eval?target=ID" -d 'document.title'  # 执行JS

# 控制
curl -s "$CDP/navigate?target=ID&url=https://example.com"
curl -s -X POST "$CDP/click?target=ID" -d '.button'
curl -s "$CDP/screenshot?target=ID&file=/tmp/shot.png"
curl -s "$CDP/scroll?target=ID&direction=down"
```

---

## Python 封装使用

```python
from scripts.browser import OpenCLIClient, CDPClient

# OpenCLI
client = OpenCLIClient()
data = client.bilibili_hot(limit=10)
data = client.xiaohongshu_search("AI")

# CDP
cdp = CDPClient()
tabs = cdp.list_tabs()
cdp.screenshot(tabs[0]['targetId'], "/tmp/shot.png")
```

---

## 文件位置

- 封装工具：`scripts/browser/browser_tools.py`
- 学习文档：`docs/research/OpenCLI完整学习文档.md`
