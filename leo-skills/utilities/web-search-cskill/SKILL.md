# Web Search Skill

**网络搜索技能** - 提供网络搜索和信息收集能力

## 快速激活

```
搜索关于[主题]的信息
```
```
帮我搜索[关键词]
```
```
查找[主题]的最新资料
```

## 功能

1. **网络搜索** - 关键词搜索，支持时间范围和网站限定
2. **内容抓取** - 抓取网页内容并提取文本
3. **信息提取** - 自动提取关键信息和摘要

## 使用场景

- 房地产政策搜索
- 市场调研
- 竞品分析
- 技术资料收集

## 配置

```yaml
search_engine: google
max_results: 10
timeout: 30
language: zh-CN
```

## API

### search(query, max_results=10)
执行网络搜索

### fetch_content(url)
抓取网页内容

### extract_info(content, keywords=None)
提取关键信息

---

**版本**: 1.0.0
**作者**: Leo Liu
