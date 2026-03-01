"""
Web Search Skill
================
网络搜索技能 - 提供真实网络搜索和深度研究能力

功能:
1. 真实网络搜索（Bing/SerpAPI/SearX）
2. 网页内容抓取
3. 关键信息提取
4. Deep Research 深度研究

作者: Claude Code
版本: 2.1.0
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import sys
import time
import re

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.evolution import EvolvableSkill


class WebSearchSkill(EvolvableSkill):
    """
    Web Search Skill - 提供真实网络搜索能力
    ===========================================
    支持多种搜索后端: Bing, SerpAPI, SearX
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            skill_name="web_search_skill",
            config_path=str(Path(__file__).parent.parent / "config" / "config.yaml")
        )
        self.config = config or {}
        self.search_engine = self.config.get("search_engine", "searx")
        self.max_results = self.config.get("max_results", 10)
        self.timeout = self.config.get("timeout", 30)
        self.bing_api_key = self.config.get("bing_api_key") or self._get_env("BING_API_KEY")
        self.serpapi_key = self.config.get("serpapi_key") or self._get_env("SERPAPI_KEY")

        # SearX 实例列表（公开实例）
        self.searx_instances = [
            "https://search.sapti.me",
            "https://search.bus-hit.me",
            "https://searx.be",
            "https://search.mdosch.de",
        ]

        # 简单的日志记录器
        import logging
        self.logger = logging.getLogger(__name__)

    def _get_env(self, key: str) -> Optional[str]:
        import os
        return os.environ.get(key)

    def search(self, query: str, max_results: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """执行网络搜索"""
        max_results = max_results or self.max_results
        time_range = kwargs.get("time_range", "")
        site = kwargs.get("site", "")
        language = kwargs.get("language", "zh-CN")

        if self.bing_api_key and self.search_engine == "bing":
            results = self._bing_search(query, max_results, time_range, language)
        elif self.serpapi_key:
            results = self._serpapi_search(query, max_results, site, language)
        else:
            results = self._searx_search(query, max_results, time_range, language)

        return {"query": query, "results": results, "total": len(results), "engine": self.search_engine}

    def _searx_search(self, query: str, max_results: int, time_range: str, language: str) -> List[Dict]:
        """SearX 搜索引擎（免费开源）"""
        import requests
        import random

        # 随机选择一个 SearX 实例
        instances = self.searx_instances.copy()
        random.shuffle(instances)

        for instance in instances:
            try:
                url = f"{instance}/search"
                params = {
                    "q": query,
                    "format": "json",
                    "language": language.split('-')[0],
                    "safesearch": "0"
                }
                if time_range:
                    params["time_range"] = time_range

                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }

                response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()

                results = []
                if "results" in data:
                    for item in data["results"][:max_results]:
                        results.append({
                            "title": item.get("title", ""),
                            "url": item.get("url", ""),
                            "snippet": item.get("content", ""),
                            "source": item.get("engine", "SearX"),
                            "score": item.get("score", 0)
                        })

                if results:
                    self.logger.info(f"SearX search successful using {instance}")
                    return results

            except Exception as e:
                self.logger.warning(f"SearX instance {instance} failed: {e}")
                continue

        # 如果所有 SearX 实例都失败，返回空列表
        self.logger.error("All SearX instances failed")
        return self._bing_public_search(query, max_results, language)

    def _bing_public_search(self, query: str, max_results: int, language: str) -> List[Dict]:
        """Public Bing HTML fallback without API key."""
        import requests
        from bs4 import BeautifulSoup

        try:
            market = "zh-CN" if language.lower().startswith("zh") else "en-US"
            response = requests.get(
                "https://cn.bing.com/search",
                params={"q": query, "setlang": market},
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept-Language": f"{market},zh;q=0.9,en;q=0.8",
                },
                timeout=self.timeout,
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            items = soup.select("ol#b_results > li.b_algo")
            results: List[Dict] = []
            for item in items[:max_results]:
                a = item.select_one("h2 a")
                if not a:
                    continue
                snippet_node = item.select_one(".b_caption p") or item.select_one("p")
                results.append(
                    {
                        "title": a.get_text(" ", strip=True),
                        "url": a.get("href", ""),
                        "snippet": snippet_node.get_text(" ", strip=True) if snippet_node else "",
                        "source": "Bing (public)",
                        "score": 0,
                    }
                )
            return results
        except Exception as e:
            self.logger.error(f"Bing public fallback failed: {e}")
            return []

    def _bing_search(self, query: str, max_results: int, time_range: str, language: str) -> List[Dict]:
        """Bing Search API 搜索"""
        try:
            from azure.cognitiveservices.search.websearch import WebSearchClient
            from azure.cognitiveservices.search.websearch.models import SafeSearch
            from msrest.authentication import CognitiveServicesCredentials

            endpoint = "https://api.bing.microsoft.com/v7.0/search"
            client = WebSearchClient(
                endpoint=endpoint,
                credentials=CognitiveServicesCredentials(self.bing_api_key)
            )
            market = f"{language}-{language.split('-')[0].upper()}"
            response = client.search(query=query, count=max_results, mkt=market, safe_search=SafeSearch.MODERATE)

            results = []
            if response.web_pages and response.web_pages.value:
                for item in response.web_pages.value[:max_results]:
                    results.append({
                        "title": item.name, "url": item.url, "snippet": item.snippet,
                        "display_url": item.display_url, "source": "Bing"
                    })
            return results
        except Exception as e:
            self.logger.error(f"Bing search failed: {e}")
            return self._searx_search(query, max_results, time_range, language)

    def _serpapi_search(self, query: str, max_results: int, site: str, language: str) -> List[Dict]:
        """SerpAPI (Google搜索) 搜索"""
        try:
            import requests
            params = {"api_key": self.serpapi_key, "q": query, "num": min(max_results, 10), "hl": language.split('-')[0]}
            if site:
                params["as_sitesearch"] = site

            response = requests.get("https://serpapi.com/search", params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            results = []
            if "organic_results" in data:
                for item in data["organic_results"][:max_results]:
                    results.append({
                        "title": item.get("title", ""), "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""), "position": item.get("position"), "source": "Google (SerpAPI)"
                    })
            return results
        except Exception as e:
            self.logger.error(f"SerpAPI failed: {e}")
            return self._searx_search(query, max_results, "", language)

    def fetch_content(self, url: str, extract_images: bool = False, **kwargs) -> Dict[str, Any]:
        """抓取网页内容"""
        import requests
        from bs4 import BeautifulSoup
        import trafilatura

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            }
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            # 使用 trafilatura 提取正文内容
            content = trafilatura.extract(response.text, include_comments=False, include_tables=True)

            # 备用：使用 BeautifulSoup
            if not content:
                soup = BeautifulSoup(response.content, 'html.parser')
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                title = soup.title.string if soup.title else ""
                paragraphs = soup.find_all('p')
                content = '\n'.join([p.get_text(strip=True) for p in paragraphs])
            else:
                soup = BeautifulSoup(response.content, 'html.parser')
                title = soup.title.string if soup.title else ""

            return {
                "url": url, "title": title, "content": content[:15000] if content else "",
                "word_count": len(content.split()) if content else 0,
                "status_code": response.status_code, "success": bool(content)
            }
        except Exception as e:
            return {"url": url, "error": str(e), "success": False}

    def extract_info(self, content: str, keywords: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """提取关键信息"""
        summary = content[:500] + "..." if len(content) > 500 else content
        found_keywords = [k for k in keywords if k in content] if keywords else []

        # 使用 jieba 提取关键词（如果可用）
        auto_keywords = []
        try:
            import jieba.analyse
            auto_keywords = jieba.analyse.extract_tags(content, topK=10)
        except:
            pass

        sentences = [s.strip() for s in content.replace('。', '\n').split('\n') if len(s.strip()) > 20]
        key_sentences = sentences[:5]
        key_numbers = list(set(re.findall(r'[\d,.]+%?', content)))[:10]

        return {
            "summary": summary, "keywords": found_keywords, "auto_keywords": auto_keywords,
            "key_sentences": key_sentences, "key_numbers": key_numbers,
            "content_length": len(content), "word_count": len(content.split()), "success": True
        }

    def deep_research(self, query: str, max_iterations: int = 3, max_sources: int = 5, **kwargs) -> Dict[str, Any]:
        """
        Deep Research - 深度研究（核心功能）
        迭代式搜索和分析，从多个角度深入研究主题
        """
        research_log = []
        all_findings = []
        all_sources = []

        # 研究角度
        research_angles = kwargs.get("angles", [
            "最新新闻 最新动态",
            "发展趋势 预测",
            "重要事件 突破",
        ])

        for iteration, angle in enumerate(research_angles[:max_iterations]):
            self.logger.info(f"Iteration {iteration + 1}: {angle}")

            search_results = self.search(f"{query} {angle}", max_results=max_sources, **kwargs)

            for result in search_results.get("results", []):
                if result.get("url"):
                    # 只获取部分内容，避免请求过多
                    content = self.fetch_content(result["url"])
                    if content.get("success"):
                        extracted = self.extract_info(content.get("content", ""), keywords=query.split())
                        finding = {
                            "angle": angle, "title": result["title"], "source": result["url"],
                            "snippet": result.get("snippet", ""), "extracted_info": extracted,
                            "iteration": iteration + 1
                        }
                        all_findings.append(finding)
                        all_sources.append({"url": result["url"], "title": result["title"], "source_engine": result.get("source")})

            research_log.append({
                "iteration": iteration + 1, "angle": angle,
                "sources_found": len(search_results.get("results", [])),
                "sources_analyzed": len([f for f in all_findings if f["iteration"] == iteration + 1])
            })
            time.sleep(0.5)  # 避免请求过快

        report = self._synthesize_report(query, all_findings, research_log)

        return {
            "query": query, "report": report, "findings": all_findings,
            "sources": all_sources, "research_log": research_log,
            "total_sources": len(all_sources), "total_iterations": len(research_log), "success": True
        }

    def _synthesize_report(self, query: str, findings: List[Dict], research_log: List[Dict]) -> str:
        """综合研究报告"""
        report = [f"# {query} 研究报告\n",
                  f"## 研究概述\n- 研究主题: {query}\n- 分析角度: {len(research_log)}个\n- 数据来源: {len(findings)}个网页\n\n## 主要发现\n"]

        for i, finding in enumerate(findings[:10], 1):  # 限制显示前10个发现
            report.append(f"\n### {i}. {finding['title']}\n")
            report.append(f"**来源**: {finding['source']}\n")
            if finding.get('snippet'):
                report.append(f"**摘要**: {finding['snippet'][:200]}...\n")

        report.append(f"\n## 数据来源\n")
        for source in list({s['url']: s for s in [f for f in findings]}.values())[:5]:
            report.append(f"- [{source.get('title', 'Unknown')[:50]}]({source.get('source', '#')})\n")

        return "\n".join(report)

    def get_help(self) -> str:
        """获取帮助信息"""
        return """
Web Search Skill 帮助 (v2.1)
===========================

功能:
1. search(query, max_results=10) - 执行网络搜索
2. fetch_content(url) - 抓取网页内容
3. extract_info(content, keywords) - 提取关键信息
4. deep_research(query) - 深度研究 ⭐核心功能

使用示例:
--------
# 深度研究（推荐用于获取最新信息）
result = skill.deep_research("2025年2月 AI人工智能最新新闻", max_iterations=3)

# 简单搜索
skill.search("菜市场 投资回报")

配置环境变量:
-----------
- BING_API_KEY: Bing搜索API密钥（更稳定）
- SERPAPI_KEY: SerpAPI密钥（Google搜索）
- 默认使用 SearX（免费，无需API Key）
"""


if __name__ == "__main__":
    skill = WebSearchSkill()
    print("Testing Search...")
    result = skill.search("2025年 AI最新新闻", max_results=5)
    print(f"Found {result['total']} results")
    for item in result['results'][:3]:
        print(f"- {item['title'][:50]}...")
