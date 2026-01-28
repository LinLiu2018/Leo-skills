"""
Web Search Skill
================
网络搜索技能 - 提供真实网络搜索和深度研究能力

功能:
1. 真实网络搜索（Bing/SerpAPI/DuckDuckGo）
2. 网页内容抓取
3. 关键信息提取
4. Deep Research 深度研究

作者: Claude Code
版本: 2.0.0
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
    支持多种搜索后端: Bing, DuckDuckGo, SerpAPI
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            skill_name="web_search_skill",
            config_path=str(Path(__file__).parent.parent / "config" / "config.yaml")
        )
        self.config = config or {}
        self.search_engine = self.config.get("search_engine", "duckduckgo")
        self.max_results = self.config.get("max_results", 10)
        self.timeout = self.config.get("timeout", 30)
        self.bing_api_key = self.config.get("bing_api_key") or self._get_env("BING_API_KEY")
        self.serpapi_key = self.config.get("serpapi_key") or self._get_env("SERPAPI_KEY")

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
            results = self._duckduckgo_search(query, max_results, time_range, language)

        return {"query": query, "results": results, "total": len(results), "engine": self.search_engine}

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
            market = f"{language}-{language.split('-')[0]}"
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
            return self._duckduckgo_search(query, max_results, time_range, language)

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
            self.logger.error(f"SerpAPI search failed: {e}")
            return self._duckduckgo_search(query, max_results, "", language)

    def _duckduckgo_search(self, query: str, max_results: int, time_range: str, language: str) -> List[Dict]:
        """DuckDuckGo 免费搜索（无需API Key）"""
        import requests
        from bs4 import BeautifulSoup

        try:
            url = "https://html.duckduckgo.com/html/"
            params = {"q": query, "kl": language}
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []

            for result in soup.find_all('div', class_='result')[:max_results]:
                link_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')
                if link_elem:
                    results.append({
                        "title": link_elem.get_text(strip=True),
                        "url": link_elem.get('href', ''),
                        "snippet": snippet_elem.get_text(strip=True) if snippet_elem else "",
                        "source": "DuckDuckGo"
                    })

            return results[:max_results]
        except Exception as e:
            self.logger.error(f"DuckDuckGo search failed: {e}")
            return []

    def fetch_content(self, url: str, extract_images: bool = False, **kwargs) -> Dict[str, Any]:
        """抓取网页内容"""
        import requests
        from bs4 import BeautifulSoup

        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # 清理脚本和样式
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            # 提取标题
            title = soup.title.string if soup.title else ""
            if not title and soup.find('h1'):
                title = soup.find('h1').get_text(strip=True)

            # 提取段落文本
            paragraphs = soup.find_all('p')
            text = '\n'.join([p.get_text(strip=True) for p in paragraphs])

            return {
                "url": url, "title": title, "content": text[:10000],
                "html": response.text[:50000], "word_count": len(text.split()),
                "status_code": response.status_code, "success": True
            }
        except Exception as e:
            return {"url": url, "error": str(e), "success": False}

    def extract_info(self, content: str, keywords: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """提取关键信息"""
        import jieba

        summary = content[:500] + "..." if len(content) > 500 else content
        found_keywords = [k for k in keywords if k in content] if keywords else []

        try:
            auto_keywords = jieba.analyse.extract_tags(content, topK=10)
        except:
            auto_keywords = []

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

        Args:
            query: 研究主题
            max_iterations: 最大迭代次数（默认3）
            max_sources: 每轮最大来源数（默认5）

        Returns:
            深度研究报告
        """
        research_log = []
        all_findings = []
        all_sources = []

        # 7个研究角度
        research_angles = [
            "概述 定义 概念",
            "现状 发展趋势 数据",
            "案例 成功 经验",
            "政策 法规 支持",
            "挑战 问题 风险",
            "投资 成本 回报",
            "未来 前景 预测"
        ]

        for iteration, angle in enumerate(research_angles[:max_iterations]):
            self.logger.info(f"Iteration {iteration + 1}: {angle}")

            search_results = self.search(f"{query} {angle}", max_results=max_sources, **kwargs)

            for result in search_results["results"]:
                if result.get("url"):
                    content = self.fetch_content(result["url"])
                    if content["success"]:
                        extracted = self.extract_info(content.get("content", ""), keywords=[query] + angle.split())
                        finding = {
                            "angle": angle, "title": result["title"], "source": result["url"],
                            "snippet": result.get("snippet", ""), "extracted_info": extracted, "iteration": iteration + 1
                        }
                        all_findings.append(finding)
                        all_sources.append({"url": result["url"], "title": result["title"], "source_engine": result.get("source")})

            research_log.append({
                "iteration": iteration + 1, "angle": angle,
                "sources_found": len(search_results["results"]),
                "sources_analyzed": len([f for f in all_findings if f["iteration"] == iteration + 1])
            })
            time.sleep(1)  # 避免请求过快

        report = self._synthesize_report(query, all_findings, research_log)

        return {
            "query": query, "report": report, "findings": all_findings,
            "sources": all_sources, "research_log": research_log,
            "total_sources": len(all_sources), "total_iterations": len(research_log), "success": True
        }

    def _generate_research_angles(self, query: str) -> List[str]:
        """生成研究角度"""
        return ["概述 定义 概念", "现状 发展趋势 数据", "案例 成功 经验",
                "政策 法规 支持", "挑战 问题 风险", "投资 成本 回报", "未来 前景 预测"]

    def _synthesize_report(self, query: str, findings: List[Dict], research_log: List[Dict]) -> str:
        """综合研究报告"""
        report = [f"# {query} 深度研究报告\n",
                  f"## 研究概述\n- 研究主题: {query}\n- 迭代次数: {len(research_log)}\n- 分析来源: {len(findings)}个\n\n## 主要发现\n"]

        angles_seen = set()
        for finding in findings:
            angle = finding["angle"]
            if angle not in angles_seen:
                report.append(f"\n### {angle}\n")
                angles_seen.add(angle)

            keywords = finding.get("extracted_info", {}).get("auto_keywords", [])
            report.append(f"#### {finding['title']}\n来源: {finding['source']}")
            if keywords:
                report.append(f"关键词: {', '.join(keywords[:5])}")
            report.append("")

        return "\n".join(report)

    def batch_search(self, queries: List[str], **kwargs) -> Dict[str, Any]:
        """批量搜索"""
        all_results = {}
        for i, query in enumerate(queries):
            self.logger.info(f"Batch search {i+1}/{len(queries)}: {query}")
            all_results[query] = self.search(query, **kwargs)
            if i < len(queries) - 1:
                time.sleep(1)
        return {"queries": queries, "results": all_results, "total_queries": len(queries), "success": True}

    def get_help(self) -> str:
        """获取帮助信息"""
        return """
Web Search Skill 帮助 (v2.0)
===========================

功能:
1. search(query, max_results=10) - 执行网络搜索
2. fetch_content(url) - 抓取网页内容
3. extract_info(content, keywords) - 提取关键信息
4. deep_research(query) - 深度研究 ⭐核心功能
5. batch_search(queries) - 批量搜索

使用示例:
--------
# 深度研究（推荐用于商业调研）
result = skill.deep_research("宁波智慧农贸市场 投资分析", max_iterations=5)

# 简单搜索
skill.search("菜市场 投资回报")

# 批量搜索
skill.batch_search(["宁波 农贸市场 政策", "菜市场 改造 成本"])

配置环境变量:
-----------
- BING_API_KEY: Bing搜索API密钥
- SERPAPI_KEY: SerpAPI密钥（用于Google搜索）
"""


if __name__ == "__main__":
    skill = WebSearchSkill()
    print("Testing Deep Research...")
    result = skill.deep_research("宁波智慧农贸市场 投资", max_iterations=2)
    print(f"Success: {result['success']}")
    print(f"Sources found: {result['total_sources']}")
    print(f"Report preview: {result['report'][:500]}")
