# Real Estate News Publisher - CSkill

**Version:** 1.0.0
**Type:** Simple Skill
**Architecture:** Simple Skill (Single focused objective)
**Created by:** Agent-Skill-Creator v2.1

---

## Table of Contents

1. [Overview](#overview)
2. [Core Capabilities](#core-capabilities)
3. [Architecture & Design](#architecture--design)
4. [Module Specifications](#module-specifications)
5. [Data Sources & Configuration](#data-sources--configuration)
6. [Content Generation Strategy](#content-generation-strategy)
7. [Platform Integration](#platform-integration)
8. [Usage Examples](#usage-examples)
9. [Quality Standards](#quality-standards)
10. [Performance & Optimization](#performance--optimization)
11. [Error Handling & Recovery](#error-handling--recovery)
12. [Deployment & Installation](#deployment--installation)

---

## Overview

### Purpose

The **Real Estate News Publisher** is an autonomous agent designed to automate the entire workflow of real estate policy news collection, intelligent content generation, and multi-platform publishing. It monitors multiple sources for policy updates, analyzes market trends, generates engaging articles using AI, and publishes them to WeChat Official Accounts and other social media platforms.

This skill addresses the critical need for real estate professionals to maintain an active online presence with timely, relevant content without the manual effort of daily research, writing, and publishing.

### Problem Statement

Real estate agencies and professionals face several challenges:

1. **Time-Consuming Research**: Monitoring multiple government websites, news portals, and industry platforms daily
2. **Content Creation Burden**: Writing engaging, professional articles consistently
3. **Manual Publishing**: Logging into platforms to format and publish content
4. **Lack of Analytics**: Difficulty tracking which content performs best
5. **Inconsistent Scheduling**: Missing optimal publishing times

### Solution Approach

This skill implements a comprehensive 4-phase pipeline:

```
PHASE 1: COLLECTION
├─ Multi-source monitoring (government, news, industry, social)
├─ Intelligent keyword-based search
├─ Content deduplication and filtering
└─ Priority scoring

PHASE 2: ANALYSIS
├─ Policy point extraction
├─ Market impact analysis
├─ Trend identification
└─ Opportunity detection

PHASE 3: GENERATION
├─ AI-powered article writing
├─ SEO optimization
├─ Image suggestion
└─ Compliance checking

PHASE 4: PUBLICATION
├─ WeChat Official Account API integration
├─ Automatic formatting and scheduling
├─ Multi-platform synchronization
└─ Performance tracking
```

### Key Differentiators

- **Ningbo-Focused**: Specialized for Ningbo real estate market (Yuyao, Zhenhai, Fenghua)
- **Intelligent Filtering**: Prioritizes policy > market > regional > product news
- **AI-Enhanced**: Uses GLM-4/ZhipuAI for intelligent content generation
- **Multi-Platform**: WeChat, WeChat Channel, Xiaohongshu, Douyin support
- **Performance-Driven**: Built-in analytics and automatic optimization

---

## Core Capabilities

### 1. Multi-Source Information Collection

#### Government Websites Monitoring
- **Ninghousing Bureau** (宁波市住建局)
- **Yuyao Government** (余姚市政府)
- **Zhenhai Government** (镇海区政府)
- **Fenghua Government** (奉化区政府)

#### News Portals Scraping
- Xinhua Real Estate (新华网房产)
- People's Real Estate (人民网房产)
- Zhejiang Online (浙江在线)
- Ningbo Daily (宁波日报)

#### Industry Platforms
- Beike Research Institute (贝壳研究院)
- Lianjia Market Reports (链家)
- Anjuke Market Data (安居客)

#### Social Media Monitoring
- Weibo real estate topics
- Zhihu Q&A

### 2. Intelligent Keyword Search

**Policy Keywords:**
- 限购 (Purchase restrictions)
- 限贷 (Lending restrictions)
- 公积金 (Provident fund)
- 房贷利率 (Mortgage rates)
- 税收优惠 (Tax incentives)

**Market Keywords:**
- 成交量 (Transaction volume)
- 房价走势 (Price trends)
- 供应量 (Supply)
- 去化率 (Absorption rate)

**Regional Keywords:**
- 余姚 (Yuyao)
- 镇海 (Zhenhai)
- 奉化 (Fenghua)
- 牟山 (Moushan)
- 九龙湖 (Jiulonghu)
- 溪口 (Xikou)

**Product Keywords:**
- 别墅 (Villa)
- 度假房产 (Vacation property)
- 养老地产 (Senior housing)
- 低密度住宅 (Low-density housing)

### 3. Content Analysis & Filtering

- **Time Filtering**: Last 7 days content
- **Deduplication**: Remove duplicate articles
- **Priority Scoring**: Policy > Market > Regional > Product
- **Source Credibility**: Government > News > Industry > Social
- **Relevance Detection**: NINGBO-focused relevance scoring

### 4. AI-Powered Content Generation

#### Article Structure
1. **Engaging Title**: Keyword-rich, attention-grabbing
2. **Introduction**: Hook reader, state article purpose
3. **Policy Analysis**: Core policy points explained simply
4. **Market Impact**: How it affects Ningbo vacation villa market
5. **Buying Advice**: Actionable recommendations
6. **Project Integration**: Natural mention of relevant projects
7. **Closing**: Call-to-action

#### SEO Optimization
- Keyword density optimization (2-3%)
- Meta descriptions
- Tag generation
- Readable formatting

### 5. WeChat Official Account Publishing

- **API Integration**: Direct WeChat platform connection
- **Automatic Formatting**: Rich text with images
- **Scheduled Publishing**: Optimal times (8 AM or 7 PM weekdays)
- **Tag Management**: Topic tags for discoverability

### 6. Multi-Platform Distribution

- **WeChat Channel**: Text-to-speech + image slideshow
- **Xiaohongshu**: Key points + beautiful formatting
- **Douyin**: Short video script generation

### 7. Performance Tracking & Optimization

- **Metrics**: Reads, likes, shares, comments
- **Conversion**: Consultations, site visits
- **Auto-Optimization**: Learn from high-performing articles
- **A/B Testing**: Title and content strategies

---

## Architecture & Design

### Directory Structure

```
realestate-news-publisher-cskill/
├── .claude-plugin/
│   └── marketplace.json          # Plugin manifest
├── scripts/
│   ├── __init__.py
│   ├── main.py                   # Main entry point
│   ├── collectors/               # Data collection modules
│   │   ├── __init__.py
│   │   ├── government_collector.py
│   │   ├── news_collector.py
│   │   ├── industry_collector.py
│   │   └── social_collector.py
│   ├── analyzers/                # Content analysis modules
│   │   ├── __init__.py
│   │   ├── content_analyzer.py
│   │   ├── relevance_scorer.py
│   │   └── deduplicator.py
│   ├── generators/               # Content generation modules
│   │   ├── __init__.py
│   │   ├── article_generator.py
│   │   ├── title_generator.py
│   │   └── seo_optimizer.py
│   ├── publishers/               # Publishing modules
│   │   ├── __init__.py
│   │   ├── wechat_publisher.py
│   │   ├── wechat_channel_publisher.py
│   │   ├── xiaohongshu_publisher.py
│   │   └── douyin_publisher.py
│   ├── trackers/                 # Analytics modules
│   │   ├── __init__.py
│   │   ├── analytics_collector.py
│   │   └── optimizer.py
│   └── utils/                    # Utility modules
│       ├── __init__.py
│       ├── http_client.py
│       ├── logger.py
│       └── config_loader.py
├── config/
│   ├── config.yaml               # Main configuration
│   ├── sources.yaml              # Data source definitions
│   └── keywords.yaml             # Keyword definitions
├── assets/
│   └── templates/                # Article templates
│       ├── policy_article.md
│       ├── market_article.md
│       └── regional_article.md
├── SKILL.md                      # This file
├── README.md                     # User documentation
└── requirements.txt              # Python dependencies
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| HTTP Client | requests, aiohttp | Web scraping |
| HTML Parsing | BeautifulSoup4, lxml | Content extraction |
| Scheduling | APScheduler | Task scheduling |
| AI Generation | zhipuai (GLM-4) | Content generation |
| WeChat API | wechatpy | Platform integration |
| Database | SQLAlchemy | Data storage |
| Config | PyYAML | Configuration management |
| Logging | logging | Log management |

---

## Module Specifications

### Collectors Module

#### `government_collector.py`
Monitors official government websites for policy updates.

**Key Methods:**
- `collect_ninghousing_bureau()`: Scrape Ningbo housing authority
- `collect_yuyao_gov()`: Scrape Yuyao government portal
- `collect_zhenhai_gov()`: Scrape Zhenhai district portal
- `collect_fenghua_gov()`: Scrape Fenghua district portal

**Data Returned:**
```python
{
    "title": "Policy title",
    "url": "Source URL",
    "publish_date": "2024-01-15",
    "source": "ninghousing_bureau",
    "content": "Full content text",
    "category": "policy",
    "priority": 10
}
```

#### `news_collector.py`
Scrapes major news portals for real estate news.

**Key Methods:**
- `collect_xinhua_property()`: Xinhua Real Estate
- `collect_people_property()`: People's Real Estate
- `collect_zhejiang_online()`: Zhejiang Online
- `collect_ningbo_daily()`: Ningbo Daily

#### `industry_collector.py`
Monitors industry platforms for market data and analysis.

**Key Methods:**
- `collect_beike_research()`: Beike Research Institute
- `collect_lianjia_data()`: Lianjia market reports
- `collect_anjuke_data()`: Anjuke market data

#### `social_collector.py`
Monitors social media for trending topics.

**Key Methods:**
- `collect_weibo_topics()`: Weibo real estate topics
- `collect_zhihu_qa()`: Zhihu Q&A

### Analyzers Module

#### `content_analyzer.py`
Analyzes collected content for key information.

**Key Methods:**
- `extract_policy_points()`: Extract core policy changes
- `analyze_market_impact()`: Analyze market implications
- `identify_trends()`: Identify emerging trends
- `assess_sentiment()`: Positive/negative/neutral assessment

**Analysis Output:**
```python
{
    "policy_points": ["Point 1", "Point 2"],
    "market_impact": "positive/negative/neutral",
    "trends": ["Trend 1"],
    "sentiment": "bullish/bearish/neutral",
    "relevance_score": 0.85
}
```

#### `relevance_scorer.py`
Scores content relevance to Ningbo vacation villa market.

**Scoring Factors:**
- Geographic relevance (Ningbo/Yuyao/Zhenhai/Fenghua)
- Product relevance (villa/vacation/senior housing)
- Policy impact level
- Market timing relevance

#### `deduplicator.py`
Removes duplicate and similar content.

**Methods:**
- Content hashing
- Similarity detection (TF-IDF + cosine similarity)
- URL canonicalization

### Generators Module

#### `article_generator.py`
Generates full articles using AI.

**Key Methods:**
- `generate_policy_article()`: Policy-focused article
- `generate_market_article()`: Market analysis article
- `generate_regional_article()`: Regional spotlight article

**Article Template:**
```markdown
# [Engaging Title with Keywords]

## 引言
[Hook opening that captures attention]

## 政策解读
[Core policy points explained simply]

## 市场影响
[Analysis of impact on Ningbo vacation villa market]

## 购房建议
[Actionable recommendations for buyers]

## 推荐项目
[Natural mention of relevant projects like 余姚牟山玫瑰园]

## 结语
[Call-to-action]

---
#宁波房产 #政策解读 #度假别墅
```

#### `title_generator.py`
Generates engaging, click-worthy titles.

**Strategies:**
- Question format: "房贷利率再降，现在是买房的好时机吗？"
- Number format: "2024年宁波购房5大红利政策解读"
- Urgency format: "紧急！余姚最新购房政策出台，买房人必看"
- Benefit format: "宁波公积金新政解读：最高可省XX万元"

#### `seo_optimizer.py`
Optimizes content for search engines.

**Optimizations:**
- Keyword density (2-3%)
- Meta description generation
- Heading structure (H1, H2, H3)
- Internal/external linking
- Image alt text

### Publishers Module

#### `wechat_publisher.py`
Publishes articles to WeChat Official Account.

**Key Methods:**
- `create_article()`: Create article draft
- `upload_media()`: Upload images
- `publish_article()`: Publish immediately
- `schedule_article()`: Schedule for later

**Integration:**
```python
# Requires WeChat Official Account credentials
WECHAT_APPID = "your_appid"
WECHAT_SECRET = "your_secret"
```

#### `wechat_channel_publisher.py`
Publishes to WeChat Channel (视频号).

**Format:** Text-to-speech + image slideshow

#### `xiaohongshu_publisher.py`
Publishes to Xiaohongshu.

**Format:** Key points + emoji-rich formatting

#### `douyin_publisher.py`
Generates video scripts for Douyin.

**Format:** 15-60 second video script

### Trackers Module

#### `analytics_collector.py`
Collects performance metrics.

**Metrics:**
- Read count (阅读量)
- Like count (点赞数)
- Share count (分享数)
- Comment count (评论数)
- Follow count (关注数)

#### `optimizer.py`
Analyzes performance and suggests optimizations.

**Optimizations:**
- Best performing topics
- Optimal publish times
- Title effectiveness
- Content length analysis

---

## Data Sources & Configuration

### Source Configuration (`config/sources.yaml`)

```yaml
government_sources:
  - name: "宁波市住建局"
    url: "http://zjj.ningbo.gov.cn"
    type: "government"
    update_frequency: "daily"
    priority: 10

  - name: "余姚市政府"
    url: "http://www.yuyao.gov.cn"
    type: "government"
    update_frequency: "daily"
    priority: 9

news_sources:
  - name: "新华网房产"
    url: "http://www.xinhuanet.com/house/index.htm"
    type: "news"
    update_frequency: "hourly"
    priority: 7

industry_sources:
  - name: "贝壳研究院"
    url: "https://research.ke.com"
    type: "industry"
    update_frequency: "daily"
    priority: 6
```

### Keyword Configuration (`config/keywords.yaml`)

```yaml
policy_keywords:
  - 限购
  - 限贷
  - 公积金
  - 房贷利率
  - 税收优惠
  - 购房补贴
  - 落户政策

market_keywords:
  - 成交量
  - 房价走势
  - 供应量
  - 去化率
  - 库存
  - 土拍

regional_keywords:
  - 余姚
  - 镇海
  - 奉化
  - 牟山
  - 九龙湖
  - 溪口

product_keywords:
  - 别墅
  - 度假房产
  - 养老地产
  - 低密度住宅
  - 排屋
  - 合院
```

### Main Configuration (`config/config.yaml`)

```yaml
# AI Configuration
ai:
  provider: "zhipuai"  # or "openai"
  model: "glm-4"
  api_key: "${ZHIPUAI_API_KEY}"
  temperature: 0.7
  max_tokens: 2000

# Collection Schedule
schedule:
  collection_frequency: "0 8,20 * * *"  # 8 AM and 8 PM
  publishing_time: "0 8,19 * * 1-5"    # 8 AM and 7 PM weekdays
  timezone: "Asia/Shanghai"

# Content Settings
content:
  articles_per_run: 3
  min_relevance_score: 0.6
  article_length:
    min: 800
    max: 1500
  days_to_lookback: 7

# WeChat Configuration
wechat:
  app_id: "${WECHAT_APPID}"
  app_secret: "${WECHAT_SECRET}"
  account_id: "${WECHAT_ACCOUNT_ID}"
  auto_publish: false  # Set to true for automatic publishing
  create_as_draft: true

# Database
database:
  type: "sqlite"
  path: "./data/realestate_publisher.db"

# Logging
logging:
  level: "INFO"
  file: "./logs/publisher.log"
  rotation: "10 MB"
```

---

## Content Generation Strategy

### AI Prompt Engineering

The system uses carefully crafted prompts to generate high-quality content:

#### Policy Article Prompt

```
你是一位专业的房地产内容创作者。请基于以下信息撰写一篇微信公众号文章：

【政策信息】
{policy_content}

【分析要点】
{analysis}

【要求】
1. 标题要吸引人，包含关键词
2. 正文结构：引言 + 政策解读 + 市场影响 + 购房建议 + 结语
3. 自然融入项目信息（余姚牟山玫瑰园、九龙湖利时玖珑湾等）
4. 段落简短，适合手机阅读
5. 专业但不晦涩，贴近购房者
6. 字数800-1200字

请生成文章内容。
```

### Project Integration

The system naturally integrates project mentions:

- **余姚牟山玫瑰园** (Yuyao Moushan Rose Garden)
- **九龙湖利时玖珑湾** (Jiulonghu Lishi Jiulongwan)
- **溪口度假项目** (Xikou Vacation Projects)

Integration strategy:
1. Only mention when relevant to article topic
2. Position as examples, not advertisements
3. Include value propositions (location, amenities, price)

---

## Platform Integration

### WeChat Official Account API

#### Authentication
```python
from wechatpy import WeChatClient

client = WeChatClient(
    appid=config.wechat.app_id,
    appsecret=config.wechat.app_secret
)
```

#### Create Article
```python
def create_article(title, content, images):
    """Create article as draft or publish directly"""
    articles = [{
        "title": title,
        "author": "房产资讯",
        "digest": content[:100],
        "content": content,
        "content_source_url": "",
        "thumb_media_id": upload_cover(images[0]),
        "show_cover_pic": 1,
        "need_open_comment": 1,
        "only_fans_can_comment": 0
    }]

    return client.draft.add_articles(articles)
```

#### Schedule Publishing
```python
def schedule_article(media_id, publish_time):
    """Schedule article for specific time"""
    return client.draft.auto_post_id_to_media_id(
        media_id=media_id,
        publish_time=publish_time
    )
```

---

## Usage Examples

### Basic Usage

```python
from scripts.main import RealEstateNewsPublisher

# Initialize publisher
publisher = RealEstateNewsPublisher(config_path="config/config.yaml")

# Run full pipeline
publisher.run()
```

### Custom Collection

```python
# Collect only from specific sources
news = publisher.collect_from_sources(
    sources=["government", "news"],
    keywords=["限购", "公积金"]
)
```

### Generate Single Article

```python
from scripts.generators.article_generator import ArticleGenerator

generator = ArticleGenerator(config)
article = generator.generate_policy_article(
    policy_data=policy_item,
    analysis=analysis_result
)
```

### Schedule Daily Run

```python
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

# Run at 8 AM and 8 PM daily
scheduler.add_job(
    publisher.run,
    trigger='cron',
    hour='8,20',
    minute='0'
)

scheduler.start()
```

---

## Quality Standards

### Content Quality

- **Originality**: All content generated from collected sources
- **Accuracy**: Fact-checking against official sources
- **Readability**: Short paragraphs, clear headings
- **Engagement**: Compelling titles and hooks
- **Compliance**: No sensitive content, verified claims

### Technical Quality

- **Error Handling**: Comprehensive try-catch blocks
- **Logging**: Detailed logs for debugging
- **Testing**: Unit tests for all modules
- **Documentation**: Clear docstrings and comments
- **Security**: API keys in environment variables

---

## Performance & Optimization

### Caching Strategy

- Source content cached for 1 hour
- Generated articles cached for 24 hours
- API responses cached per WeChat limits

### Rate Limiting

- Respect robots.txt
- Implement request delays
- Use connection pooling

### Database Optimization

- Index on publish_date and source
- Archive old content monthly
- Clean up duplicates weekly

---

## Error Handling & Recovery

### Common Errors

| Error | Handling |
|-------|----------|
| Source unavailable | Skip, log warning, retry next cycle |
| API rate limit | Exponential backoff |
| AI generation fail | Retry with fallback template |
| WeChat API error | Save as draft, notify admin |
| Database locked | Retry with backoff |

### Recovery Strategy

1. **Checkpoint system**: Save progress after each phase
2. **Retry logic**: 3 retries with exponential backoff
3. **Fallback templates**: Use templates if AI fails
4. **Notifications**: Alert on critical failures

---

## Deployment & Installation

### Installation

```bash
# Clone the skill
cd ~/ai-agents-workspace/skills/realestate-news-publisher-cskill

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python scripts/init_db.py

# Test run
python scripts/main.py --test
```

### Environment Variables

```bash
# .env file
ZHIPUAI_API_KEY=your_zhipuai_api_key
WECHAT_APPID=your_wechat_appid
WECHAT_SECRET=your_wechat_secret
WECHAT_ACCOUNT_ID=your_account_id
DATABASE_URL=sqlite:///./data/publisher.db
LOG_LEVEL=INFO
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "scripts/main.py"]
```

### Systemd Service

```ini
[Unit]
Description=Real Estate News Publisher
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/skill
ExecStart=/usr/bin/python3 scripts/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please open a GitHub issue or contact the development team.
