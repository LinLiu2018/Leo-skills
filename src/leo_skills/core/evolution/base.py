import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


class EvolvableSkill:
    """
    EvolvableSkill
    ==============
    支持自我进化的技能基类。
    
    核心功能：
    1. 自动加载 `evolution.json` 存档。
    2. 提供 `learn()` 方法记录经验。
    3. 提供 `get_experience()` 方法获取当前经验摘要。
    
    使用方法：
    class MySkill(EvolvableSkill):
        def __init__(self):
            super().__init__("my_skill", Path(__file__).parent / "evolution.json")
            
        def execute(self, task):
            # 1. 获取经验
            tips = self.get_experience_context()
            print(f"Applying experience: {tips}")
            
            # 2. 执行任务...
            
            # 3. 记录新经验 (如果失败或有改进)
            self.learn("Ensure input format is strict JSON")
    """

    def __init__(self, skill_name: str, evolution_path: Optional[Path] = None, config_path: Optional[str] = None, **kwargs):
        self.skill_name = skill_name
        self.evolution_path = evolution_path or Path(f"./{skill_name}_evolution.json")
        self.config_path = config_path
        self.experience_data = self._load_experience()

    def _load_experience(self) -> Dict[str, Any]:
        """加载经验存档"""
        if self.evolution_path.exists():
            try:
                with open(self.evolution_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[Warning] Failed to load evolution data: {e}")
                return {"version": 1, "tips": [], "history": []}
        return {"version": 1, "tips": [], "history": []}

    def _save_experience(self):
        """保存经验存档"""
        try:
            with open(self.evolution_path, "w", encoding="utf-8") as f:
                json.dump(self.experience_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Error] Failed to save evolution data: {e}")

    def learn(self, tip: str, context: str = ""):
        """
        学习新经验 (Learn new experience)
        
        Args:
            tip: 经验总结 (e.g., "Use fetch_wechat_article for WeChat URLs")
            context: 上下文详情 (可选)
        """
        entry = {
            "tip": tip,
            "context": context,
            "timestamp": "auto-generated" # 省略具体时间实现简化
        }
        
        # 避免重复
        if not any(t["tip"] == tip for t in self.experience_data["tips"]):
            self.experience_data["tips"].append(entry)
            self.experience_data["history"].append(entry)
            self._save_experience()
            print(f"[Evolution] Skill '{self.skill_name}' learned: {tip}")

    def get_experience_context(self) -> str:
        """获取用于Prompt的经验上下文"""
        tips = [t["tip"] for t in self.experience_data.get("tips", [])]
        if not tips:
            return ""
        
        return "\n".join([f"- {tip}" for tip in tips])

    def get_tips(self) -> List[str]:
        return [t["tip"] for t in self.experience_data.get("tips", [])]
