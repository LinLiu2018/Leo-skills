"""
Memory Enhanced Skill - 增强记忆技能
"""

from typing import Dict, Any, Optional, List
from datetime import datetime


class MemoryEnhancedSkill:
    """增强记忆技能"""
    
    def __init__(self):
        self.name = "memory_enhanced_skill"
        self.version = "1.0.0"
        self.category = "core"
        self.memories = []
    
    def execute(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = params or {}
        action = params.get("action", "store")
        
        if action == "store":
            return self._store_memory(params)
        elif action == "retrieve":
            return self._retrieve_memory(params)
        elif action == "update":
            return self._update_memory(params)
        elif action == "delete":
            return self._delete_memory(params)
        else:
            return {"status": "error", "message": f"未知操作：{action}"}
    
    def _store_memory(self, params: Dict) -> Dict[str, Any]:
        content = params.get("content", "")
        category = params.get("category", "general")
        tags = params.get("tags", [])
        
        memory = {
            "id": len(self.memories) + 1,
            "content": content,
            "category": category,
            "tags": tags,
            "created_at": datetime.now().isoformat(),
            "access_count": 0
        }
        
        self.memories.append(memory)
        
        return {
            "status": "success",
            "skill": self.name,
            "action": "store",
            "memory_id": memory["id"],
            "message": f"已记住：{content[:50]}..."
        }
    
    def _retrieve_memory(self, params: Dict) -> Dict[str, Any]:
        query = params.get("query", "")
        category = params.get("category", None)
        
        results = []
        for memory in self.memories:
            if query.lower() in memory["content"].lower():
                memory["access_count"] += 1
                results.append(memory)
        
        return {
            "status": "success",
            "skill": self.name,
            "action": "retrieve",
            "query": query,
            "count": len(results),
            "memories": results[:10]
        }
    
    def _update_memory(self, params: Dict) -> Dict[str, Any]:
        memory_id = params.get("id", 0)
        new_content = params.get("content", "")
        
        for memory in self.memories:
            if memory["id"] == memory_id:
                memory["content"] = new_content
                memory["updated_at"] = datetime.now().isoformat()
                return {
                    "status": "success",
                    "skill": self.name,
                    "action": "update",
                    "memory_id": memory_id
                }
        
        return {"status": "error", "message": f"未找到记忆 ID: {memory_id}"}
    
    def _delete_memory(self, params: Dict) -> Dict[str, Any]:
        memory_id = params.get("id", 0)
        
        for i, memory in enumerate(self.memories):
            if memory["id"] == memory_id:
                del self.memories[i]
                return {
                    "status": "success",
                    "skill": self.name,
                    "action": "delete",
                    "memory_id": memory_id
                }
        
        return {"status": "error", "message": f"未找到记忆 ID: {memory_id}"}
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "category": self.category,
            "status": "active",
            "memory_count": len(self.memories)
        }


__all__ = ["MemoryEnhancedSkill"]
