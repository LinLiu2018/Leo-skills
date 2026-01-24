---
name: twitter_monitor_skill
description: 监控 Twitter 上的 AI 科技博主，采集最新推文并存储到数据库
version: 1.0.0
author: Leo Liu
created: 2026-01-23
category: intelligence
tags: [twitter, monitoring, ai, intelligence, data-collection]
---

# Twitter Monitor Skill - Technical Specification

**Version:** 1.0.0
**Type:** Simple Skill
**Created:** 2026-01-23
**Category:** Intelligence / Data Collection

## Overview

Twitter Monitor Skill 是一个专业的 Twitter 监控工具，用于采集 AI 科技博主的最新推文。它支持定时监控、关键词搜索、智能去重和数据持久化。

### Purpose（目的）

- 监控 Twitter 上的 AI 科技博主（OpenAI, Anthropic, AI 研究者等）
- 自动采集最新推文并存储到数据库
- 为技术情报系统提供数据源

### Problem Statement（问题陈述）

AI 技术发展迅速，重要的技术信息往往首先在 Twitter 上发布。手动监控多个博主效率低下，容易遗漏重要信息。

### Solution Approach（解决方案）

使用 Twitter API v2 自动采集推文，通过三层去重机制（URL → 哈希 → 相似度）确保数据质量，存储到 SQLite 数据库供后续分析使用。

## Core Capabilities（核心能力）

1. **博主监控**：监控指定的 Twitter 博主，采集最新推文
2. **关键词搜索**：按关键词搜索相关推文
3. **智能去重**：三层去重机制（URL、哈希、TF-IDF 相似度）
4. **质量过滤**：根据点赞数、转发数、内容长度过滤低质量推文
5. **数据持久化**：存储到 SQLite 数据库，支持查询和统计
6. **速率限制**：自动处理 Twitter API 速率限制
7. **定时调度**：支持 Cron 表达式定时执行

## When To Use（使用场景）

### 适用场景

- ✅ 监控 AI 科技博主的最新动态
- ✅ 采集特定主题的推文（如 GPT, Claude, LangChain）
- ✅ 为技术情报系统提供数据源
- ✅ 研究 AI 技术趋势和热点
- ✅ 构建 AI 技术知识库

### 激活词示例

```
"监控 Twitter 上的 AI 博主"
"采集 OpenAI 的最新推文"
"搜索关于 Claude 的推文"
"获取未处理的推文"
```

## When NOT To Use（不适用场景）

- ❌ 需要实时监控（本技能为定时采集）
- ❌ 需要采集历史推文（Twitter API 限制为最近 7 天）
- ❌ 需要采集大量推文（受 API 配额限制）
- ❌ 需要分析推文内容（请使用 tech_extractor_skill）

## Architecture & Design（架构设计）

### 目录结构

```
twitter_monitor_skill/
├── .claude-plugin/
│   └── marketplace.json          # 插件清单
├── scripts/
│   ├── __init__.py
│   ├── main.py                   # 主入口
│   ├── collectors/
│   │   ├── __init__.py
│   │   └── twitter_collector.py  # Twitter 采集器
│   ├── analyzers/
│   │   ├── __init__.py
│   │   └── deduplicator.py       # 去重器
│   ├── models/
│   │   ├── __init__.py
│   │   └── database.py           # 数据库模型
│   └── utils/
│       ├── __init__.py
│       ├── http_client.py
│       └── logger.py
├── config/
│   ├── config.yaml               # 主配置
│   ├── bloggers.yaml             # 博主列表
│   └── evolution_config.yaml     # 进化配置
├── data/
│   └── twitter_monitor.db        # SQLite 数据库
├── SKILL.md                      # 本文档
├── README.md                     # 使用说明
└── requirements.txt              # Python 依赖
```

### 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| Twitter API | tweepy 4.14+ | 官方推荐的 Python Twitter API 库 |
| 数据库 | SQLite + SQLAlchemy | 轻量级数据库，支持 ORM |
| 去重 | scikit-learn | TF-IDF + 余弦相似度 |
| 配置 | PyYAML + python-dotenv | YAML 配置 + 环境变量 |
| 定时 | APScheduler | Cron 表达式支持 |

### 核心组件

#### 1. TwitterCollector（采集器）

```python
class TwitterCollector:
    def collect_user_tweets(username, max_results) -> List[Dict]
    def search_tweets(query, max_results) -> List[Dict]
    def get_user_info(username) -> Dict
```

**功能**：
- 采集指定用户的推文
- 按关键词搜索推文
- 获取用户信息
- 自动处理速率限制

#### 2. Deduplicator（去重器）

```python
class Deduplicator:
    def deduplicate(tweets) -> List[Dict]
    def _deduplicate_by_url(tweets) -> List[Dict]
    def _deduplicate_by_hash(tweets) -> List[Dict]
    def _deduplicate_by_similarity(tweets) -> List[Dict]
```

**三层去重策略**：
1. **URL 去重**：移除重复的推文链接
2. **哈希去重**：基于内容 MD5 哈希去重
3. **相似度去重**：使用 TF-IDF + 余弦相似度去重

#### 3. Database（数据库）

```python
class Database:
    def save_tweet(tweet_data) -> Tweet
    def get_tweets(author_username, limit, processed) -> List[Tweet]
    def mark_as_processed(tweet_ids)
    def cleanup_old_tweets(days)
```

**数据模型**：
```python
class Tweet:
    id: int
    tweet_id: str
    author_username: str
    content: str
    created_at: datetime
    likes: int
    retweets: int
    # ... 更多字段
```

## Usage Examples（使用示例）

### 1. 命令行使用

```bash
# 监控配置的博主
python scripts/main.py --mode monitor

# 按关键词搜索
python scripts/main.py --mode search --keywords GPT Claude LangChain

# 查看统计信息
python scripts/main.py --mode stats

# 清理旧推文
python scripts/main.py --cleanup
```

### 2. Python 代码使用

```python
from twitter_monitor_cskill.scripts.main import TwitterMonitor

# 初始化监控器
monitor = TwitterMonitor()

# 监控博主
tweets = monitor.monitor()
print(f"采集到 {len(tweets)} 条推文")

# 按关键词搜索
tweets = monitor.search_by_keywords(['GPT-4', 'Claude', 'LangChain'])

# 获取未处理的推文
unprocessed = monitor.get_unprocessed_tweets(limit=100)

# 标记为已处理
tweet_ids = [tweet['tweet_id'] for tweet in unprocessed]
monitor.mark_as_processed(tweet_ids)

# 获取统计信息
stats = monitor.get_stats()
print(f"总推文数：{stats['total_tweets']}")
```

### 3. 定时任务

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from twitter_monitor_cskill.scripts.main import TwitterMonitor

monitor = TwitterMonitor()
scheduler = BlockingScheduler()

# 每天 8:00 和 20:00 执行
scheduler.add_job(
    monitor.monitor,
    trigger='cron',
    hour='8,20',
    minute='0'
)

scheduler.start()
```

## Configuration（配置说明）

### 环境变量（.env）

```bash
# Twitter API 凭证
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_secret
```

### 博主配置（config/bloggers.yaml）

```yaml
bloggers:
  - username: "OpenAI"
    category: "official"
    priority: 10
    enabled: true

  - username: "karpathy"
    category: "researcher"
    priority: 9
    enabled: true
```

### 主配置（config/config.yaml）

```yaml
monitoring:
  schedule: "0 8,20 * * *"
  max_tweets_per_user: 100
  lookback_days: 7
  filters:
    min_likes: 5
    min_retweets: 2

rate_limiting:
  request_interval: 2
  max_requests_per_hour: 300

deduplication:
  similarity_threshold: 0.85
```

## Dependencies（依赖项）

```
tweepy>=4.14.0
sqlalchemy>=2.0.0
pyyaml>=6.0
python-dotenv>=1.0.0
apscheduler>=3.10.0
scikit-learn>=1.3.0
jieba>=0.42.1
```

## Installation（安装）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 Twitter API 凭证

# 3. 测试运行
python scripts/main.py --mode stats
```

## API Reference（API 参考）

### TwitterMonitor

#### `monitor(bloggers=None) -> List[Dict]`

监控指定博主

**参数**：
- `bloggers`: 博主列表（可选）

**返回**：
- 采集到的推文列表

#### `search_by_keywords(keywords, max_results=100) -> List[Dict]`

按关键词搜索推文

**参数**：
- `keywords`: 关键词列表
- `max_results`: 最大结果数

**返回**：
- 搜索到的推文列表

#### `get_unprocessed_tweets(limit=100) -> List[Dict]`

获取未处理的推文

**参数**：
- `limit`: 返回数量限制

**返回**：
- 未处理的推文列表

#### `mark_as_processed(tweet_ids)`

标记推文为已处理

**参数**：
- `tweet_ids`: 推文 ID 列表

## Performance（性能）

- **采集速度**：约 2 秒/博主（受速率限制影响）
- **去重效率**：1000 条推文约 1-2 秒
- **数据库性能**：SQLite，适合中小规模数据（< 100万条）
- **内存占用**：约 50-100 MB

## Limitations（限制）

1. **Twitter API 限制**：
   - Free Tier: 500,000 推文/月
   - 只能获取最近 7 天的推文
   - 速率限制：300 请求/15 分钟

2. **去重限制**：
   - 相似度去重对短文本效果较差
   - 需要足够的文本长度（建议 > 50 字符）

3. **数据库限制**：
   - SQLite 不适合高并发场景
   - 建议定期清理旧数据

## Troubleshooting（故障排除）

### 问题 1：API 认证失败

**错误**：`401 Unauthorized`

**解决**：
- 检查 `.env` 文件中的 API 凭证是否正确
- 确认 Twitter Developer Account 状态正常
- 重新生成 API 密钥

### 问题 2：速率限制

**错误**：`429 Too Many Requests`

**解决**：
- 增加 `request_interval` 配置
- 减少 `max_tweets_per_user` 配置
- 等待 15 分钟后重试

### 问题 3：数据库锁定

**错误**：`database is locked`

**解决**：
- 确保没有多个进程同时访问数据库
- 使用 `with` 语句正确关闭数据库连接

## Version History（版本历史）

### v1.0.0 (2026-01-23)

- ✅ 初始版本发布
- ✅ 支持博主监控和关键词搜索
- ✅ 三层去重机制
- ✅ SQLite 数据持久化
- ✅ 速率限制和错误处理

## Future Enhancements（未来增强）

- [ ] 支持更多社交媒体平台（微博、知乎）
- [ ] 实时监控（WebSocket）
- [ ] 情感分析
- [ ] 自动分类和标签
- [ ] Web 管理界面

## Related Skills（相关技能）

- **tech_extractor_skill**: 从推文中提取 AI 技术信息
- **skill_code_generator_skill**: 基于技术信息生成代码
- **obsidian_sync_skill**: 同步到 Obsidian 知识库

## Support（支持）

- **作者**：Leo Liu (@LinLiu2018)
- **文档**：[TWITTER_API_GUIDE.md](../../../docs/TWITTER_API_GUIDE.md)
- **问题反馈**：GitHub Issues

---

*最后更新：2026-01-23*
