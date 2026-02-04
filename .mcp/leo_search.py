#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Leo Search - 网络搜索工具
使用 Bing RSS 源，无需 API Key
"""

import sys
import os
import json
import re
import urllib.request
import urllib.parse
import ssl

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

os.environ['PYTHONIOENCODING'] = 'utf-8'


class LeoSearch:
    """网络搜索工具"""
    
    def __init__(self):
        self.timeout = 30
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    def search_with_bing_rss(self, query: str, max_results: int = 10) -> list:
        """使用 Bing RSS 搜索"""
        try:
            # Bing News RSS
            url = f"https://www.bing.com/news/search?q={urllib.parse.quote(query)}&format=rss"
            req = urllib.request.Request(
                url,
                headers={'User-Agent': self.user_agent}
            )
            
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as response:
                xml = response.read().decode('utf-8', errors='replace')
            
            results = []
            # 解析 RSS
            items = re.findall(r'<item>(.*?)</item>', xml, re.DOTALL)
            
            for item in items[:max_results]:
                title = re.search(r'<title[^>]*>([^<]*)</title>', item)
                url = re.search(r'<link[^>]*>([^<]*)</link>', item)
                desc = re.search(r'<description[^>]*>([^<]*)</description>', item)
                date = re.search(r'<pubDate[^>]*>([^<]*)</pubDate>', item)
                
                if title and url:
                    results.append({
                        "title": title.group(1).strip(),
                        "url": url.group(1).strip(),
                        "snippet": desc.group(1).strip()[:300] if desc else "",
                        "date": date.group(1).strip() if date else "",
                        "source": "Bing News"
                    })
            
            return results
        except Exception as e:
            print(f"[ERROR] Bing RSS failed: {e}")
            return []
    
    def search_with_baidu(self, query: str, max_results: int = 10) -> list:
        """使用百度搜索（简单爬取）"""
        try:
            url = f"https://www.baidu.com/s?wd={urllib.parse.quote(query)}"
            req = urllib.request.Request(
                url,
                headers={'User-Agent': self.user_agent}
            )
            
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as response:
                html = response.read().decode('utf-8', errors='replace')
            
            results = []
            # 解析百度结果
            patterns = [
                r'<a[^>]*class="[^"]*c-showurl[^"]*"[^>]*>([^<]*)</a>',
                r'<a[^>]*href="(http[^"]*)"[^>]*>([^<]*<em>[^<]*</em>[^<]*)</a>',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html)
                for match in matches[:max_results]:
                    if len(match) == 2:
                        url, title = match
                        title = re.sub(r'<[^>]+>', '', title)  # 移除 em 标签
                        results.append({
                            "title": title.strip(),
                            "url": url.strip()[:200],
                            "snippet": "",
                            "source": "Baidu"
                        })
            
            # 去重
            seen = set()
            unique_results = []
            for r in results:
                if r['url'] not in seen:
                    seen.add(r['url'])
                    unique_results.append(r)
            
            return unique_results[:max_results]
        except Exception as e:
            print(f"[ERROR] Baidu search failed: {e}")
            return []
    
    def search(self, query: str, max_results: int = 10) -> dict:
        """综合搜索"""
        # 先尝试 Bing
        results = self.search_with_bing_rss(query, max_results)
        
        # 如果 Bing 没结果，尝试百度
        if not results:
            results = self.search_with_baidu(query, max_results)
        
        # 查找官方数据源
        official_sources = []
        for r in results:
            url = r.get('url', '').lower()
            if any(domain in url for domain in ['ningbo.gov.cn', 'tjj', 'nbjs', 'gov.cn', 'nbfcjs.com']):
                official_sources.append(r)
        
        return {
            "query": query,
            "total": len(results),
            "results": results,
            "official_sources": official_sources
        }
    
    def generate_research_report(self, topic: str) -> str:
        """生成调研报告"""
        data = self.search(topic)
        
        report = f"""# {topic} 调研报告

**生成时间**: 2026-02-03 13:15
**搜索关键词**: {data['query']}
**找到结果**: {data['total']} 条

---

## 一、搜索结果摘要

### 官方数据源

"""

        if data['official_sources']:
            for i, source in enumerate(data['official_sources'], 1):
                report += f"{i}. **{source['title']}**\n   URL: {source['url']}\n"
                if source.get('snippet'):
                    report += f"   摘要: {source['snippet'][:100]}...\n"
                report += "\n"
        else:
            report += "未在搜索结果中发现明显的官方数据源。\n\n"

        report += "### 其他相关结果\n\n"
        
        other_results = [r for r in data['results'] if r not in data['official_sources']]
        for i, r in enumerate(other_results[:5], 1):
            report += f"{i}. **{r['title']}**\n   URL: {r['url'][:80]}...\n\n"

        report += """---

## 二、数据获取建议

### 推荐官方数据源

| 数据类型 | 数据源 | 网址 |
|---------|--------|------|
| 统计数据 | 宁波市统计局 | tjj.ningbo.gov.cn |
| 房产数据 | 宁波住建局 | nbjs.ningbo.gov.cn |
| 成交数据 | 透明售房网 | www.nbfcjs.com |

### 下一步行动

1. 访问上述官方数据源获取准确数据
2. 复制数据后发送给我
3. 我将使用 Leo 的 `data_analyzer_skill` 做深度分析

---

*报告由 Leo Search 自动生成*
"""
        
        return report


def main():
    if len(sys.argv) < 2:
        print("Leo Search - 网络搜索工具")
        print()
        print("Usage:")
        print("  python leo_search.py search <query>")
        print("  python leo_search.py report <topic>")
        print()
        print("Examples:")
        print("  python leo_search.py search 宁波房价")
        print("  python leo_search.py report 宁波商业租赁市场分析")
        sys.exit(0)
    
    command = sys.argv[1]
    searcher = LeoSearch()
    
    if command == "search":
        query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "宁波"
        data = searcher.search(query)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    
    elif command == "report":
        topic = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "未指定主题"
        report = searcher.generate_research_report(topic)
        print(report)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
