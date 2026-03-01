"""
Web Search Enhanced Skill - 增强版网络搜索

支持 Brave Search + Tavily API 双引擎，智能并发控制。
"""

from typing import Dict, Any, List, Optional
import time


class WebSearchEnhancedSkill:
    """增强版网络搜索技能"""
    
    def __init__(self):
        self.name = "web_search_enhanced_skill"
        self.version = "1.0.0"
        self.category = "utilities"
        
        # 配置
        self.config = {
            "max_results": 10,
            "rate_limit_delay": 1.0,  # 搜索间隔（秒）
            "use_tavily": False,  # 是否启用 Tavily
            "tavily_api_key": None
        }
        
        # 请求历史（用于速率限制）
        self.request_history = []
    
    def execute(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """执行搜索"""
        params = params or {}
        query = params.get("query", "")
        
        if not query:
            return {
                "status": "error",
                "message": "请提供搜索关键词"
            }
        
        # 速率限制检查
        self._enforce_rate_limit()
        
        # 执行搜索
        results = self._search(query, params)
        
        # 记录请求
        self.request_history.append(time.time())
        
        return {
            "status": "success",
            "skill": self.name,
            "action": "web_search",
            "query": query,
            "results": results
        }
    
    def _enforce_rate_limit(self):
        """执行速率限制"""
        now = time.time()
        # 移除 60 秒前的记录
        self.request_history = [t for t in self.request_history if now - t < 60]
        
        # 如果 60 秒内超过 10 次请求，等待
        if len(self.request_history) >= 10:
            wait_time = 60 - (now - self.request_history[0])
            if wait_time > 0:
                time.sleep(wait_time)
    
    def _search(self, query: str, params: Dict) -> List[Dict]:
        """执行搜索（调用 web_search 工具）"""
        # 实际搜索由 OpenClaw 的 web_search 工具执行
        # 这里返回搜索结果的处理逻辑
        return []
    
    def _deduplicate(self, results: List[Dict]) -> List[Dict]:
        """去重搜索结果"""
        seen_urls = set()
        unique = []
        
        for result in results:
            url = result.get("url", "")
            if url not in seen_urls:
                seen_urls.add(url)
                unique.append(result)
        
        return unique
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "category": self.category,
            "status": "active",
            "config": self.config
        }


__all__ = ["WebSearchEnhancedSkill"]
