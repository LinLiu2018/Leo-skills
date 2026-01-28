# Real Estate News Publisher - CSkill

**房产资讯自动化发布代理**

一个智能化的房地产政策资讯采集、内容生成和自动发布系统，专注于宁波及周边区域（余姚、镇海、奉化）的度假别墅市场。

## 功能特性

### 第一部分：信息搜索与采集
- ✅ 多渠道信息源监控（政府官网、新闻网站、行业平台、社交媒体）
- ✅ 智能关键词搜索（政策、市场、区域、产品类）
- ✅ 内容筛选与去重（按时间、去重、优先级、可信度）

### 第二部分：内容智能整合
- ✅ 内容分析与提炼（政策要点、市场影响、趋势判断）
- ✅ 文章智能创作（标题生成、正文结构、项目融入、SEO优化）
- ✅ 内容优化（公众号适配、合规检查）

### 第三部分：公众号自动发布
- ✅ 微信公众号集成（API连接、自动排版、定时发布）
- 🔧 多平台分发（视频号、小红书、抖音）

### 第四部分：效果追踪与优化
- ✅ 数据统计（阅读量、点赞数、分享数）
- ✅ 自动优化（分析高阅读量特征、调整策略）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API 密钥：

```bash
# 智谱 AI (或 OpenAI)
ZHIPUAI_API_KEY=your_zhipuai_api_key

# 微信公众号
WECHAT_APPID=your_wechat_appid
WECHAT_SECRET=your_wechat_secret
WECHAT_ACCOUNT_ID=your_account_id
```

### 3. 运行

```bash
# 完整流程（采集 -> 分析 -> 生成 -> 发布）
python scripts/main.py

# 仅生成文章，不发布
python scripts/main.py --no-publish

# 指定关键词
python scripts/main.py --keywords 限购 公积金

# 测试模式
python scripts/main.py --test
```

## 配置说明

### 主配置文件 (`config/config.yaml`)

```yaml
# AI 配置
ai:
  provider: "zhipuai"  # 或 "openai"
  model: "glm-4"
  api_key: "${ZHIPUAI_API_KEY}"

# 采集调度
schedule:
  collection_frequency: "0 8,20 * * *"  # 每天 8 点和 20 点
  publishing_time: "0 8,19 * * 1-5"     # 工作日 8 点和 19 点

# 内容设置
content:
  articles_per_run: 3          # 每次生成文章数量
  min_relevance_score: 0.6     # 最低相关性得分
  days_to_lookback: 7          # 回溯天数
```

### 数据源配置 (`config/sources.yaml`)

配置要监控的政府网站、新闻门户和行业平台。

### 关键词配置 (`config/keywords.yaml`)

配置政策、市场、区域、产品类关键词。

## 目录结构

```
realestate_news_publisher_skill/
├── .claude-plugin/
│   └── marketplace.json      # 插件清单
├── scripts/
│   ├── collectors/           # 数据采集模块
│   ├── analyzers/            # 内容分析模块
│   ├── generators/           # 内容生成模块
│   ├── publishers/           # 发布模块
│   ├── trackers/             # 数据追踪模块
│   ├── utils/                # 工具模块
│   └── main.py               # 主程序
├── config/
│   ├── config.yaml           # 主配置
│   ├── sources.yaml          # 数据源配置
│   └── keywords.yaml         # 关键词配置
├── assets/
│   └── templates/            # 文章模板
├── SKILL.md                  # 技能文档
├── README.md                 # 本文件
└── requirements.txt          # 依赖列表
```

## 作为 Claude Code 技能使用

此技能可以安装到 Claude Code 中使用：

1. 将技能目录添加到 Claude Code 技能路径
2. 使用激活词触发：
   - "创建新闻发布代理"
   - "自动化房产资讯发布"
   - "监控房产政策并生成文章"

## 定时任务

使用 cron 或 Windows 任务计划程序定时运行：

```bash
# 每天早上 8 点运行
0 8 * * * cd /path/to/skill && python scripts/main.py
```

## 注意事项

1. **微信公众号 API**：需要认证的服务号才能使用自动发布功能
2. **AI 配额**：智谱 AI 和 OpenAI 都有 API 调用限制
3. **爬虫合规**：遵守 robots.txt 和相关法律法规
4. **内容审核**：建议使用草稿模式，人工审核后再发布

## 项目信息

- **版本**: 1.0.0
- **创建者**: Agent-Skill-Creator
- **类型**: Simple Skill
- **目标区域**: 宁波、余姚、镇海、奉化

## 许可证

MIT License

---

**Created with Agent-Skill-Creator v2.1**
