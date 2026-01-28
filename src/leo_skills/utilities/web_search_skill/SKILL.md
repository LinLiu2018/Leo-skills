# Web Search Skill

**网络搜索技能 v2.0** - 提供真实网络搜索和深度研究能力

## 快速激活

```
深度研究[主题]
搜索[关键词]
批量搜索[多个关键词]
```

## 功能 (v2.0 新增 Deep Research)

1. **真实网络搜索** - 支持 Bing/Google/DuckDuckGo
2. **Deep Research** - 深度研究 ⭐核心功能
3. **内容抓取** - 抓取网页内容并提取文本
4. **信息提取** - 自动提取关键信息和摘要
5. **批量搜索** - 一次处理多个查询

## Deep Research 深度研究

```
深度研究 "宁波智慧农贸市场 投资分析"
```

自动执行7个维度研究：
- 概述 定义 概念
- 现状 发展趋势 数据
- 案例 成功 经验
- 政策 法规 支持
- 挑战 问题 风险
- 投资 成本 回报
- 未来 前景 预测

## 使用场景

- 商业项目调研 ⭐推荐
- 市场可行性分析
- 竞品分析
- 政策研究
- 投资回报分析

## 配置

```yaml
# config.yaml 或环境变量
search_engine: duckduckgo  # bing/serpapi/duckduckgo
bing_api_key: YOUR_BING_KEY  # 环境变量: BING_API_KEY
serpapi_key: YOUR_SERP_KEY   # 环境变量: SERPAPI_KEY
max_results: 10
timeout: 30
language: zh-CN
```

## API

### search(query, max_results=10, time_range="", site="")
执行网络搜索

### deep_research(query, max_iterations=3, max_sources=5)
深度研究（核心功能）

### fetch_content(url, extract_images=False)
抓取网页内容

### extract_info(content, keywords=None)
提取关键信息

### batch_search(queries)
批量搜索

---

**版本**: 2.0.0
**作者**: Claude Code
