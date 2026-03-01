# Twitter API 申请指南

## 概述

Twitter API v2 需要申请 Developer Account 才能使用。本指南将帮助您完成申请流程。

## 申请步骤

### 1. 访问 Twitter Developer Portal

访问：https://developer.twitter.com/

### 2. 注册 Developer Account

1. 点击 "Sign up" 或 "Apply for a developer account"
2. 选择账号类型：
   - **Hobbyist**（爱好者）- 免费，适合个人项目
   - **Academic**（学术）- 免费，需要学术机构邮箱
   - **Business**（商业）- 付费，适合商业用途

**推荐选择**：Hobbyist → Exploring the API

### 3. 填写申请表

需要回答以下问题（英文）：

**问题 1：What country do you live in?**
- 回答：China

**问题 2：What's your use case?**
- 回答示例：
```
I'm building an AI technology intelligence system that monitors AI-related
tweets from tech bloggers and researchers. The system will:

1. Monitor tweets from AI technology accounts (OpenAI, Anthropic, etc.)
2. Extract AI technology information from tweets
3. Generate daily reports for personal learning and research

This is a personal project for educational purposes to stay updated with
the latest AI technologies and trends.
```

**问题 3：Will you make Twitter content or derived information available to a government entity?**
- 回答：No

**问题 4：Will your product, service, or analysis make Twitter content or derived information available to a government entity?**
- 回答：No

### 4. 同意条款

- 阅读并同意 Developer Agreement
- 阅读并同意 Developer Policy

### 5. 验证邮箱

- 检查邮箱，点击验证链接

### 6. 创建 App

申请通过后：

1. 进入 Developer Portal
2. 点击 "Create App"
3. 填写 App 信息：
   - **App name**：ai-tech-intelligence（或其他名称）
   - **Description**：AI Technology Intelligence System
   - **Website URL**：可以填写 GitHub 仓库地址或个人网站
   - **Callback URLs**：留空（不需要）

### 7. 获取 API 密钥

创建 App 后：

1. 进入 App 设置页面
2. 点击 "Keys and tokens" 标签
3. 生成以下密钥：
   - **API Key** (Consumer Key)
   - **API Secret** (Consumer Secret)
   - **Bearer Token**
   - **Access Token**
   - **Access Token Secret**

**重要**：立即保存这些密钥，它们只会显示一次！

### 8. 配置 API 权限

1. 进入 "Settings" 标签
2. 设置 App permissions：
   - **Read**（只读）- 足够用于监控推文
   - **Read and Write**（读写）- 如果需要发推文
   - **Read, Write, and Direct Messages**（读写和私信）- 不需要

**推荐**：选择 **Read** 权限即可

## API 访问级别

### Free Tier（免费）

- **推文数量**：500,000 条/月
- **请求速率**：
  - User lookup: 300 requests/15 min
  - Tweet lookup: 300 requests/15 min
  - Search tweets: 180 requests/15 min
- **适用场景**：个人项目、测试

### Basic（基础版）

- **价格**：$100/月
- **推文数量**：2,000,000 条/月
- **请求速率**：更高的速率限制
- **适用场景**：生产环境

### Pro（专业版）

- **价格**：$5,000/月
- **推文数量**：10,000,000 条/月
- **更多功能**：完整的历史数据访问

## 预估使用量

根据我们的系统设计：

- 监控 20 个博主
- 每人每天 10 条推文
- 每天 2 次采集
- **每天**：20 × 10 × 2 = 400 条推文
- **每月**：400 × 30 = 12,000 条推文

**结论**：**Free Tier 完全足够**（500,000 条/月 >> 12,000 条/月）

## 配置到系统

获取密钥后，将它们填入 `.env` 文件：

```bash
# 复制模板文件
cp .env.example .env

# 编辑 .env 文件，填入实际密钥
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAABcdefg...
TWITTER_API_KEY=abcdefghijklmnopqrstuvwx
TWITTER_API_SECRET=abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGH
TWITTER_ACCESS_TOKEN=1234567890-ABCDEFGHIJKLMNOPQRSTUVWXYZabcde
TWITTER_ACCESS_TOKEN_SECRET=abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGH
```

## 测试 API 连接

创建测试脚本 `test_twitter_api.py`：

```python
import tweepy
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化客户端
client = tweepy.Client(
    bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
    consumer_key=os.getenv('TWITTER_API_KEY'),
    consumer_secret=os.getenv('TWITTER_API_SECRET'),
    access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
    access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
)

# 测试：获取自己的用户信息
try:
    me = client.get_me()
    print(f"✅ API 连接成功！")
    print(f"用户名：{me.data.username}")
    print(f"用户 ID：{me.data.id}")
except Exception as e:
    print(f"❌ API 连接失败：{e}")

# 测试：搜索推文
try:
    tweets = client.search_recent_tweets(
        query="AI OR Claude OR GPT",
        max_results=10
    )
    print(f"\n✅ 搜索测试成功！")
    print(f"找到 {len(tweets.data)} 条推文")
    for tweet in tweets.data[:3]:
        print(f"- {tweet.text[:50]}...")
except Exception as e:
    print(f"❌ 搜索测试失败：{e}")
```

运行测试：

```bash
python test_twitter_api.py
```

## 常见问题

### Q1: 申请被拒绝怎么办？

**A**: 重新申请，提供更详细的使用说明：
- 说明是个人学习项目
- 强调不会用于商业用途
- 说明不会分享数据给第三方

### Q2: 如何避免超出速率限制？

**A**: 系统已内置速率限制器：
- 请求间隔：2 秒
- 自动重试机制
- 错误处理和日志记录

### Q3: Free Tier 够用吗？

**A**: 完全够用！我们的系统每月只需要约 12,000 条推文，远低于 500,000 的限制。

### Q4: 需要信用卡吗？

**A**: Free Tier 不需要信用卡。只有升级到 Basic 或 Pro 才需要。

## 下一步

完成 Twitter API 申请后：

1. ✅ 填写 `.env` 文件
2. ✅ 运行测试脚本验证连接
3. ✅ 开始实现 twitter_monitor_skill

## 参考资料

- [Twitter Developer Portal](https://developer.twitter.com/)
- [Twitter API v2 文档](https://developer.twitter.com/en/docs/twitter-api)
- [Tweepy 文档](https://docs.tweepy.org/)
- [API 定价](https://developer.twitter.com/en/products/twitter-api/pricing)

---

*创建时间：2026-01-23*
