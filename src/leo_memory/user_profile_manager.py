# -*- coding: utf-8 -*-
"""
用户画像自动学习系统
===================
实现 Wingman 的"察言观色"能力

自动记录用户习惯、偏好、工作模式
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ContentPreference:
    """内容偏好"""
    tone: str = "专业但亲和"  # 语气风格
    emphasis: List[str] = None  # 强调点
    avoid: List[str] = None  # 避免用词
    common_phrases: List[str] = None  # 常用话术

    def __post_init__(self):
        if self.emphasis is None:
            self.emphasis = []
        if self.avoid is None:
            self.avoid = []
        if self.common_phrases is None:
            self.common_phrases = []


@dataclass
class WorkflowPattern:
    """工作流模式"""
    pattern_name: str
    steps: List[str]
    trigger_keywords: List[str]
    frequency: int = 0  # 使用次数
    last_used: str = ""


@dataclass
class UserProfile:
    """用户画像"""
    user_id: str = "leo"
    business_domain: str = "commercial_real_estate"

    # 当前项目
    current_project: Dict[str, Any] = None

    # 内容偏好
    content_preferences: Dict[str, Any] = None

    # 工作流模式
    workflow_patterns: List[Dict] = None

    # 外部工具
    external_tools: Dict[str, Any] = None

    # 学习统计
    learning_stats: Dict[str, Any] = None

    # 创建/更新时间
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if self.current_project is None:
            self.current_project = {
                "name": "",
                "location": "",
                "target_audience": "",
                "key_selling_points": [],
                "price_range": ""
            }
        if self.content_preferences is None:
            self.content_preferences = {
                "tone": "专业但亲和",
                "emphasis": ["投资回报", "稳定收益", "实物资产"],
                "avoid": ["高风险", "投机"],
                "common_phrases": []
            }
        if self.workflow_patterns is None:
            self.workflow_patterns = []
        if self.external_tools is None:
            self.external_tools = {
                "messaging": ["飞书", "微信"],
                "ads": ["抖音", "小红书"],
                "storage": "D:/桌面/房产项目"
            }
        if self.learning_stats is None:
            self.learning_stats = {
                "total_interactions": 0,
                "skills_used": {},
                "files_edited": [],
                "feedback_given": []
            }
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()


class UserProfileManager:
    """
    用户画像自动学习系统

    功能：
    1. 观察用户行为并自动学习
    2. 构建用户画像
    3. 为任务生成个性化上下文
    4. 预测用户需求
    """

    def __init__(self, profile_path: str = None):
        """
        初始化用户画像管理器

        Args:
            profile_path: 用户画像文件路径，默认使用项目目录
        """
        if profile_path is None:
            # 默认路径
            base_path = Path(__file__).parent.parent.parent
            self.profile_path = base_path / "leo_knowledge" / "context" / "user_profile.json"
        else:
            self.profile_path = Path(profile_path)

        self.profile_path.parent.mkdir(parents=True, exist_ok=True)

        # 加载或创建用户画像
        self.profile = self._load_profile()

    def _load_profile(self) -> UserProfile:
        """加载用户画像"""
        if self.profile_path.exists():
            try:
                with open(self.profile_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return UserProfile(**data)
            except Exception as e:
                print(f"[WARNING] 加载用户画像失败: {e}，创建新的")
                return UserProfile()
        return UserProfile()

    def _save_profile(self):
        """保存用户画像"""
        self.profile.updated_at = datetime.now().isoformat()
        try:
            with open(self.profile_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.profile), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ERROR] 保存用户画像失败: {e}")

    def observe(self, event_type: str, data: Dict[str, Any]):
        """
        观察用户行为，自动学习

        Args:
            event_type: 事件类型
                - file_edited: 文件编辑
                - skill_used: 技能使用
                - content_generated: 内容生成
                - feedback: 用户反馈
                - project_switched: 切换项目
            data: 事件数据
        """
        if event_type == "file_edited":
            self._learn_from_file_edit(data)
        elif event_type == "skill_used":
            self._learn_from_skill_use(data)
        elif event_type == "content_generated":
            self._learn_from_content(data)
        elif event_type == "feedback":
            self._learn_from_feedback(data)
        elif event_type == "project_switched":
            self._learn_project_info(data)

        # 更新统计
        self.profile.learning_stats["total_interactions"] += 1

        # 保存
        self._save_profile()

    def _learn_from_file_edit(self, data: Dict):
        """从文件编辑学习"""
        file_path = data.get("file", "")
        content = data.get("content", "")

        # 记录文件类型偏好
        if file_path:
            self.profile.learning_stats["files_edited"].append({
                "file": file_path,
                "timestamp": datetime.now().isoformat()
            })

        # 从内容学习风格
        if content:
            # 提取常用词汇
            phrases = self._extract_common_phrases(content)
            for phrase in phrases:
                if phrase not in self.profile.content_preferences["common_phrases"]:
                    self.profile.content_preferences["common_phrases"].append(phrase)
                    # 只保留最近的 20 个
                    self.profile.content_preferences["common_phrases"] = \
                        self.profile.content_preferences["common_phrases"][-20:]

    def _learn_from_skill_use(self, data: Dict):
        """从技能使用学习"""
        skill_name = data.get("skill", "")
        success = data.get("success", True)

        if skill_name:
            if skill_name not in self.profile.learning_stats["skills_used"]:
                self.profile.learning_stats["skills_used"][skill_name] = {
                    "count": 0,
                    "success": 0,
                    "failed": 0
                }

            self.profile.learning_stats["skills_used"][skill_name]["count"] += 1
            if success:
                self.profile.learning_stats["skills_used"][skill_name]["success"] += 1
            else:
                self.profile.learning_stats["skills_used"][skill_name]["failed"] += 1

            # 识别工作流模式
            self._detect_workflow_pattern(skill_name)

    def _learn_from_content(self, data: Dict):
        """从生成内容学习"""
        content = data.get("content", "")
        content_type = data.get("type", "")

        if content:
            # 分析语气
            tone = self._analyze_tone(content)
            if tone:
                self.profile.content_preferences["tone"] = tone

            # 分析强调点
            emphasis = self._analyze_emphasis(content)
            for item in emphasis:
                if item not in self.profile.content_preferences["emphasis"]:
                    self.profile.content_preferences["emphasis"].append(item)
                    # 只保留 10 个
                    self.profile.content_preferences["emphasis"] = \
                        self.profile.content_preferences["emphasis"][-10:]

    def _learn_from_feedback(self, data: Dict):
        """从用户反馈学习"""
        feedback = data.get("feedback", "")
        task = data.get("task", "")

        self.profile.learning_stats["feedback_given"].append({
            "task": task,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat()
        })

        # 分析反馈中的偏好调整
        if "字体" in feedback or "大小" in feedback:
            # 记录格式偏好
            pass

    def _learn_project_info(self, data: Dict):
        """学习项目信息"""
        project = data.get("project", {})
        self.profile.current_project.update(project)

    def _extract_common_phrases(self, content: str) -> List[str]:
        """提取常用短语"""
        # 简单的短语提取：找出 2-4 字的高频词汇组合
        phrases = []

        # 常见房地产话术
        real_estate_phrases = [
            "投资回报", "年回报", "稳定收益", "满租现铺",
            "包租", "投资客", "资产配置", "现金流"
        ]

        for phrase in real_estate_phrases:
            if phrase in content:
                phrases.append(phrase)

        return phrases

    def _analyze_tone(self, content: str) -> str:
        """分析语气"""
        # 简单的语气分析
        if any(word in content for word in ["亲", "哈", "哦"]):
            return "亲和"
        elif any(word in content for word in ["必须", "一定", "绝对"]):
            return "强势"
        else:
            return "专业但亲和"

    def _analyze_emphasis(self, content: str) -> List[str]:
        """分析强调点"""
        emphasis = []

        # 检查内容中强调的是什么
        if any(word in content for word in ["回报", "收益", "赚钱"]):
            emphasis.append("投资回报")
        if any(word in content for word in ["稳定", "安全", "保障"]):
            emphasis.append("稳定收益")
        if any(word in content for word in ["位置", "地段", "交通"]):
            emphasis.append("地段优势")

        return emphasis

    def _detect_workflow_pattern(self, skill_name: str):
        """检测工作流模式"""
        # 检查最近的技能使用序列
        recent_skills = list(self.profile.learning_stats["skills_used"].keys())[-5:]

        # 常见模式
        patterns = {
            "调研 → 生成": ["research_assistant_skill", "content_layout_leo_skill"],
            "分析 → 报告": ["data_analyzer_skill", "project_marketing_doc_generator_skill"],
        }

        for pattern_name, pattern_skills in patterns.items():
            if all(s in recent_skills for s in pattern_skills):
                # 检查是否已记录此模式
                existing = [p for p in self.profile.workflow_patterns
                           if p["pattern_name"] == pattern_name]
                if existing:
                    existing[0]["frequency"] += 1
                    existing[0]["last_used"] = datetime.now().isoformat()
                else:
                    self.profile.workflow_patterns.append({
                        "pattern_name": pattern_name,
                        "steps": pattern_skills,
                        "trigger_keywords": [],
                        "frequency": 1,
                        "last_used": datetime.now().isoformat()
                    })

    def get_context_for_task(self, task: str) -> str:
        """
        为任务生成个性化上下文

        Args:
            task: 任务描述

        Returns:
            个性化上下文字符串（用于 Prompt）
        """
        context_parts = []

        # 项目上下文
        if self.profile.current_project.get("name"):
            project = self.profile.current_project
            context_parts.append(f"""当前项目：{project.get('name', '')}
- 位置：{project.get('location', '')}
- 目标客群：{project.get('target_audience', '')}
- 核心卖点：{', '.join(project.get('key_selling_points', []))}
- 价格区间：{project.get('price_range', '')}""")

        # 内容偏好
        prefs = self.profile.content_preferences
        context_parts.append(f"""内容风格：
- 语气：{prefs.get('tone', '')}
- 强调点：{', '.join(prefs.get('emphasis', []))}
- 避免用词：{', '.join(prefs.get('avoid', []))}""")

        # 相关工作流模式
        relevant_patterns = self._find_relevant_patterns(task)
        if relevant_patterns:
            context_parts.append(f"相关经验：你经常使用 '{relevant_patterns[0]}' 工作流")

        return "\n\n".join(context_parts)

    def _find_relevant_patterns(self, task: str) -> List[str]:
        """找到与任务相关的模式"""
        relevant = []

        for pattern in self.profile.workflow_patterns:
            if pattern["frequency"] > 2:  # 使用超过 2 次的模式
                relevant.append(pattern["pattern_name"])

        return relevant[:3]  # 返回最相关的 3 个

    def get_profile_summary(self) -> str:
        """获取用户画像摘要"""
        stats = self.profile.learning_stats

        return f"""用户画像摘要：
- 总交互次数：{stats['total_interactions']}
- 使用技能数：{len(stats['skills_used'])}
- 常用技能：{', '.join(list(stats['skills_used'].keys())[:5])}
- 工作流模式：{len(self.profile.workflow_patterns)}
- 最后更新：{self.profile.updated_at[:10]}
"""

    def reset_profile(self):
        """重置用户画像（谨慎使用）"""
        self.profile = UserProfile()
        self._save_profile()


# ==================== 便捷函数 ====================

def get_profile_manager() -> UserProfileManager:
    """获取用户画像管理器实例"""
    return UserProfileManager()


def observe_user_action(event_type: str, **data):
    """便捷函数：观察用户行为"""
    manager = get_profile_manager()
    manager.observe(event_type, data)


def get_personalized_context(task: str) -> str:
    """便捷函数：获取个性化上下文"""
    manager = get_profile_manager()
    return manager.get_context_for_task(task)


# ==================== 测试入口 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("用户画像自动学习系统 - 测试")
    print("=" * 60)

    manager = UserProfileManager()

    # 模拟学习
    print("\n1. 模拟技能使用...")
    manager.observe("skill_used", {
        "skill": "research_assistant_skill",
        "success": True
    })

    print("2. 模拟内容生成...")
    manager.observe("content_generated", {
        "content": "乐橙荟商铺投资回报稳定，年回报6%，满租现铺，10年包租。",
        "type": "marketing"
    })

    print("3. 模拟项目切换...")
    manager.observe("project_switched", {
        "project": {
            "name": "乐橙荟商铺",
            "location": "宁波鄞州",
            "target_audience": "投资客",
            "key_selling_points": ["满租现铺", "10年包租", "年回报6%"],
            "price_range": "100-150万"
        }
    })

    print("\n4. 用户画像摘要：")
    print(manager.get_profile_summary())

    print("\n5. 为任务生成个性化上下文：")
    context = manager.get_context_for_task("生成营销文案")
    print(context)

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
