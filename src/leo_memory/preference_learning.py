# -*- coding: utf-8 -*-
"""
用户偏好学习模块 - 让系统越用越懂你

功能：
1. 记录用户反馈（显式和隐式）
2. 分析使用模式
3. 自动调整系统行为
4. 生成个性化建议
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class PreferenceLearner:
    """用户偏好学习器"""

    def __init__(self, profile_path: Optional[str] = None):
        self.profile_path = Path(profile_path) if profile_path else Path(
            "leo_knowledge/context/user_profile.json"
        )
        self.profile = self._load_profile()

    def _load_profile(self) -> Dict[str, Any]:
        """加载用户画像"""
        if self.profile_path.exists():
            with open(self.profile_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"user_id": "leo", "learning_system": {"enabled": True}}

    def _save_profile(self):
        """保存用户画像"""
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.profile_path, "w", encoding="utf-8") as f:
            json.dump(self.profile, f, ensure_ascii=False, indent=2)

    def record_feedback(
        self, action: str, feedback: str, context: Optional[Dict] = None
    ) -> bool:
        """
        记录用户反馈

        Args:
            action: 用户操作
            feedback: "positive" | "negative" | "corrected"
            context: 上下文信息
        """
        learning = self.profile.setdefault("learning_system", {})
        tracking = learning.setdefault("feedback_tracking", {})

        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "feedback": feedback,
            "context": context or {},
        }

        if feedback == "positive":
            tracking.setdefault("positive_signals", []).append(entry)
        elif feedback == "negative":
            tracking.setdefault("negative_signals", []).append(entry)
        elif feedback == "corrected":
            tracking.setdefault("corrections_made", []).append(entry)

        self._save_profile()
        return True

    def learn_from_interaction(
        self, agent_used: str, task_type: str, satisfaction: float
    ):
        """从交互中学习"""
        interaction = self.profile.setdefault("interaction_history", {})

        # 更新使用统计
        interaction["total_sessions"] = interaction.get("total_sessions", 0) + 1
        interaction["last_interaction"] = datetime.now().isoformat()

        # 记录常用 Agent
        frequent_agents = interaction.setdefault("frequently_used_agents", [])
        if agent_used not in frequent_agents:
            frequent_agents.append(agent_used)

        # 高满意度任务加入偏好
        if satisfaction > 0.8:
            preferred = interaction.setdefault("preferred_workflows", [])
            if task_type not in preferred:
                preferred.append(task_type)

        self._save_profile()

    def adapt_parameter(self, parameter: str, new_value: Any, reason: str):
        """自适应调整参数"""
        learned = (
            self.profile.setdefault("learning_system", {})
            .setdefault("learned_patterns", {})
        )

        # 根据参数类型更新
        if "font" in parameter or "pdf" in parameter:
            doc_prefs = learned.setdefault("document_formatting", {})
            doc_prefs[parameter] = {"value": new_value, "reason": reason, "updated_at": datetime.now().isoformat()}
        elif "style" in parameter or "tone" in parameter:
            content_prefs = learned.setdefault("content_style", {})
            content_prefs[parameter] = {"value": new_value, "reason": reason, "updated_at": datetime.now().isoformat()}

        self._save_profile()

    def get_personalized_suggestions(self, task_type: str) -> List[str]:
        """基于学习生成个性化建议"""
        suggestions = []
        learned = self.profile.get("learning_system", {}).get("learned_patterns", {})

        # 文档相关建议
        if task_type in ["pdf_generation", "document_creation"]:
            doc_prefs = learned.get("document_formatting", {})
            if "pdf_font_size" in doc_prefs:
                suggestions.append(f"PDF字体已根据您的偏好设置为{doc_prefs['pdf_font_size']}")

        # 内容相关建议
        if task_type in ["content_creation", "copywriting"]:
            content_prefs = learned.get("content_style", {})
            if "opening_style" in content_prefs:
                suggestions.append(f"内容开场风格：{content_prefs['opening_style']}")

        return suggestions

    def export_learning_report(self) -> Dict[str, Any]:
        """导出学习报告"""
        learning = self.profile.get("learning_system", {})
        interaction = self.profile.get("interaction_history", {})

        return {
            "summary": {
                "total_interactions": interaction.get("total_sessions", 0),
                "positive_feedback_count": len(
                    learning.get("feedback_tracking", {}).get("positive_signals", [])
                ),
                "negative_feedback_count": len(
                    learning.get("feedback_tracking", {}).get("negative_signals", [])
                ),
                "corrections_made": len(
                    learning.get("feedback_tracking", {}).get("corrections_made", [])
                ),
            },
            "learned_patterns": learning.get("learned_patterns", {}),
            "preferences": {
                "frequently_used_agents": interaction.get("frequently_used_agents", []),
                "preferred_workflows": interaction.get("preferred_workflows", []),
            },
            "recommendations": self._generate_recommendations(),
        }

    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        interaction = self.profile.get("interaction_history", {})

        # 基于使用频率的建议
        frequent = interaction.get("frequently_used_agents", [])
        if len(frequent) > 3:
            recommendations.append("考虑创建常用Agent组合快捷方式")

        # 基于反馈的建议
        learning = self.profile.get("learning_system", {})
        tracking = learning.get("feedback_tracking", {})
        negative = len(tracking.get("negative_signals", []))
        if negative > 5:
            recommendations.append("检测到多次负面反馈，建议检查相关功能配置")

        return recommendations


# 全局学习器实例
_preference_learner: Optional[PreferenceLearner] = None


def get_preference_learner() -> PreferenceLearner:
    """获取全局偏好学习器"""
    global _preference_learner
    if _preference_learner is None:
        _preference_learner = PreferenceLearner()
    return _preference_learner


# 便捷函数
def record_positive_feedback(action: str, context: Optional[Dict] = None):
    """记录正面反馈"""
    return get_preference_learner().record_feedback(action, "positive", context)


def record_negative_feedback(action: str, context: Optional[Dict] = None):
    """记录负面反馈"""
    return get_preference_learner().record_feedback(action, "negative", context)


def record_correction(action: str, correction_details: Dict):
    """记录用户修正"""
    return get_preference_learner().record_feedback(
        action, "corrected", correction_details
    )


__all__ = [
    "PreferenceLearner",
    "get_preference_learner",
    "record_positive_feedback",
    "record_negative_feedback",
    "record_correction",
]
