"""
Web Search Skill
================
网络搜索技能 - 提供网络搜索和信息收集能力

功能:
1. 网络搜索
2. 内容抓取
3. 信息提取
"""

from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup
import re



from core.evolution import EvolvableSkill
class WebSearchSkill:
    """
    Web Search Skill
    ================
    提供网络搜索和信息收集能力
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):

        super().__init__(
            skill_name="web-search-cskill",
            config_path=str(Path(__file__).parent.parent / "config" / "config.yaml")
        )
        """
        初始化WebSearch Skill

        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.search_engine = self.config.get("search_engine", "duckduckgo")
        self.max_results = self.config.get("max_results", 10)
        self.timeout = self.config.get("timeout", 30)
        self.user_agent = self.config.get(
            "user_agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )

    def search(self,
              query: str,
              max_results: Optional[int] = None,
              **kwargs) -> Dict[str, Any]:
        """
        执行网络搜索

        Args:
            query: 搜索关键词
            max_results: 最大结果数
            **kwargs: 其他参数

        Returns:
            搜索结果字典
        """
        max_results = max_results or self.max_results

        # 简化实现：返回模拟结果
        # 实际实现需要集成搜索API
        results = self._mock_search(query, max_results)

        return {
            "query": query,
            "results": results,
            "total": len(results),
            "engine": self.search_engine
        }

    def fetch_content(self,
                     url: str,
                     **kwargs) -> Dict[str, Any]:
        """
        抓取网页内容

        Args:
            url: 网页URL
            **kwargs: 其他参数

        Returns:
            网页内容字典
        """
        try:
            headers = {"User-Agent": self.user_agent}
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            # 解析HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # 提取文本
            title = soup.title.string if soup.title else ""
            text = soup.get_text(separator='\n', strip=True)

            return {
                "url": url,
                "title": title,
                "content": text,
                "html": response.text,
                "status_code": response.status_code,
                "success": True
            }

        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "success": False
            }

    def extract_info(self,
                    content: str,
                    keywords: Optional[List[str]] = None,
                    **kwargs) -> Dict[str, Any]:
        """
        提取关键信息

        Args:
            content: 文本内容
            keywords: 关键词列表
            **kwargs: 其他参数

        Returns:
            提取的信息字典
        """
        # 生成摘要（简化实现：取前500字）
        summary = content[:500] + "..." if len(content) > 500 else content

        # 提取关键词（如果提供）
        found_keywords = []
        if keywords:
            for keyword in keywords:
                if keyword in content:
                    found_keywords.append(keyword)

        # 提取句子（简化实现）
        sentences = [s.strip() for s in content.split('。') if len(s.strip()) > 10]
        key_sentences = sentences[:5]  # 取前5句

        return {
            "summary": summary,
            "keywords": found_keywords,
            "key_sentences": key_sentences,
            "content_length": len(content),
            "success": True
        }

    def _mock_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        模拟搜索结果（用于测试）

        实际实现应该调用真实的搜索API
        """
        results = []

        for i in range(min(max_results, 5)):
            results.append({
                "title": f"{query} - 搜索结果 {i+1}",
                "url": f"https://example.com/result{i+1}",
                "snippet": f"这是关于 {query} 的搜索结果摘要 {i+1}。包含相关信息和详细内容。",
                "source": "示例网站",
                "rank": i + 1
            })

        return results

    def batch_search(self,
                    queries: List[str],
                    **kwargs) -> Dict[str, Any]:
        """
        批量搜索

        Args:
            queries: 搜索关键词列表
            **kwargs: 其他参数

        Returns:
            批量搜索结果
        """
        all_results = {}

        for query in queries:
            results = self.search(query, **kwargs)
            all_results[query] = results

        return {
            "queries": queries,
            "results": all_results,
            "total_queries": len(queries)
        }

    def get_help(self) -> str:
        """获取帮助信息"""
        return """
Web Search Skill 帮助
====================

功能:
1. search(query, max_results=10) - 执行网络搜索
2. fetch_content(url) - 抓取网页内容
3. extract_info(content, keywords=None) - 提取关键信息
4. batch_search(queries) - 批量搜索

使用示例:
- skill.search("人工智能发展趋势")
- skill.fetch_content("https://example.com")
- skill.extract_info(content, keywords=["AI", "机器学习"])

注意:
- 当前使用模拟搜索结果
- 实际部署需要配置搜索API
- 遵守网站robots.txt规则
"""


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 创建Skill实例
    skill = WebSearchSkill()

    # 测试搜索
    print("测试搜索功能:")
    results = skill.search("人工智能发展趋势", max_results=5)
    print(f"找到 {results['total']} 个结果")
    for result in results['results']:
        print(f"- {result['title']}")

    # 测试内容抓取
    print("\n测试内容抓取:")
    content = skill.fetch_content("https://www.example.com")
    if content['success']:
        print(f"成功抓取: {content['title']}")
    else:
        print(f"抓取失败: {content['error']}")

    # 测试信息提取
    print("\n测试信息提取:")
    test_content = "人工智能是计算机科学的一个分支。机器学习是人工智能的核心技术。深度学习推动了AI的快速发展。"
    info = skill.extract_info(test_content, keywords=["人工智能", "机器学习"])
    print(f"摘要: {info['summary']}")
    print(f"找到关键词: {info['keywords']}")

    # 获取帮助
    print("\n" + skill.get_help())
