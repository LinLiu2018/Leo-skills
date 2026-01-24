# Twitter Monitor Skill

> 监控 Twitter 上的 AI 科技博主，采集最新推文

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 Twitter API

1. 申请 Twitter Developer Account：https://developer.twitter.com/
2. 创建 App 并获取 API 凭证
3. 复制 `.env.example` 为 `.env` 并填入凭证

```bash
cp .env.example .env
# 编辑 .env 文件
```

详细申请指南：[TWITTER_API_GUIDE.md](../../../docs/TWITTER_API_GUIDE.md)

### 3. 运行

```bash
# 监控博主
python scripts/main.py --mode monitor

# 按关键词搜索
python scripts/main.py --mode search --keywords GPT Claude LangChain

# 查看统计
python scripts/main.py --mode stats
```

## 功能特性

- ✅ 监控指定 Twitter 博主
- ✅ 按关键词搜索推文
- ✅ 智能去重（URL + 哈希 + 相似度）
- ✅ 质量过滤（点赞数、转发数）
- ✅ SQLite 数据持久化
- ✅ 自动处理速率限制
- ✅ 支持定时调度

## 配置博主

编辑 `config/bloggers.yaml`：

```yaml
bloggers:
  - username: "OpenAI"
    category: "official"
    priority: 10
    enabled: true
```

## 使用示例

### Python 代码

```python
from scripts.main import TwitterMonitor

monitor = TwitterMonitor()

# 监控博主
tweets = monitor.monitor()

# 搜索关键词
tweets = monitor.search_by_keywords(['GPT-4', 'Claude'])

# 获取未处理推文
unprocessed = monitor.get_unprocessed_tweets()
```

### 定时任务

```python
from apscheduler.schedulers.blocking import BlockingScheduler

monitor = TwitterMonitor()
scheduler = BlockingScheduler()

# 每天 8:00 和 20:00 执行
scheduler.add_job(monitor.monitor, trigger='cron', hour='8,20', minute='0')
scheduler.start()
```

## 文档

- [SKILL.md](SKILL.md) - 完整技术文档
- [TWITTER_API_GUIDE.md](../../../docs/TWITTER_API_GUIDE.md) - Twitter API 申请指南

## 许可证

MIT License

---

*创建时间：2026-01-23*
