# Web Search Skill

**网络搜索技能** - 为Research Agent提供网络搜索和信息收集能力

---

## 🎯 技能概述

这个技能为Leo AI Agent System提供网络搜索能力，支持：
- 关键词搜索
- 网页内容抓取
- 信息提取和摘要
- 多来源整合

## 📋 功能列表

### 1. 搜索功能
- 关键词搜索
- 高级搜索（时间范围、网站限定等）
- 搜索结果排序和过滤

### 2. 内容抓取
- 网页HTML抓取
- 文本内容提取
- 结构化数据提取

### 3. 信息处理
- 内容摘要生成
- 关键信息提取
- 多来源信息整合

## 🔧 使用方式

### 基础搜索
```python
from web_search_skill import WebSearchSkill

skill = WebSearchSkill()
results = skill.search(query="人工智能发展趋势", max_results=10)
```

### 内容抓取
```python
content = skill.fetch_content(url="https://example.com")
```

### 信息提取
```python
summary = skill.extract_info(content, keywords=["AI", "机器学习"])
```

## 📊 配置选项

```yaml
web_search:
  search_engine: "google"  # google, bing, duckduckgo
  max_results: 10
  timeout: 30
  user_agent: "Mozilla/5.0..."
  language: "zh-CN"
```

## 🔌 集成方式

### 与Research Agent集成
```python
class ResearchAgent(BaseAgent):
    def execute(self, task, **kwargs):
        # 使用WebSearch Skill
        results = self.use_skill("web_search_skill", "search", query=task)
        return results
```

## 📝 API说明

### search(query, max_results=10, **kwargs)
执行网络搜索

**参数**:
- `query` (str): 搜索关键词
- `max_results` (int): 最大结果数
- `time_range` (str): 时间范围（可选）
- `site` (str): 限定网站（可选）

**返回**:
```python
{
    "query": "搜索关键词",
    "results": [
        {
            "title": "标题",
            "url": "链接",
            "snippet": "摘要",
            "source": "来源"
        }
    ],
    "total": 10
}
```

### fetch_content(url, **kwargs)
抓取网页内容

**参数**:
- `url` (str): 网页URL
- `timeout` (int): 超时时间

**返回**:
```python
{
    "url": "网页URL",
    "title": "页面标题",
    "content": "文本内容",
    "html": "HTML内容",
    "metadata": {...}
}
```

### extract_info(content, keywords=None, **kwargs)
提取关键信息

**参数**:
- `content` (str): 文本内容
- `keywords` (list): 关键词列表

**返回**:
```python
{
    "summary": "内容摘要",
    "keywords": ["关键词1", "关键词2"],
    "entities": ["实体1", "实体2"],
    "facts": ["事实1", "事实2"]
}
```

## 🎓 使用示例

### 示例1：房地产政策搜索
```python
# 搜索最新房地产政策
results = skill.search(
    query="宁波房地产政策 2026",
    time_range="past_month",
    max_results=20
)

# 抓取详细内容
for result in results["results"]:
    content = skill.fetch_content(result["url"])
    info = skill.extract_info(content, keywords=["政策", "调控", "限购"])
```

### 示例2：市场调研
```python
# 搜索AI眼镜市场信息
results = skill.search(
    query="AI眼镜市场规模 趋势",
    max_results=15
)

# 整合信息
all_info = []
for result in results["results"]:
    content = skill.fetch_content(result["url"])
    info = skill.extract_info(content)
    all_info.append(info)
```

## 🔒 注意事项

1. **API限制**: 某些搜索引擎有API调用限制
2. **网站robots.txt**: 遵守网站的爬虫规则
3. **请求频率**: 避免过于频繁的请求
4. **内容版权**: 注意内容使用的版权问题

## 🚀 未来计划

- [ ] 支持更多搜索引擎
- [ ] 添加图片搜索
- [ ] 支持PDF文档抓取
- [ ] 添加缓存机制
- [ ] 实现智能去重

---

**创建时间**: 2026-01-09
**维护者**: Leo Liu
**版本**: 1.0.0
