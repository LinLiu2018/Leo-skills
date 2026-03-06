# -*- coding: utf-8 -*-
"""
技能推荐引擎 (Skill Recommender)

基于用户意图和上下文，推荐或自动生成 Skills。
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


@dataclass
class SkillRecommendation:
    """技能推荐"""
    skill_name: str
    skill_path: str
    confidence: float
    reason: str
    category: str
    estimated_effort: str  # "low", "medium", "high"
    required_tools: List[str]


@dataclass
class SkillGenerationRequest:
    """技能生成请求"""
    intent_category: str
    trigger_keywords: List[str]
    description: str
    example_inputs: List[str]
    priority: str  # "high", "medium", "low"
    context: Dict[str, Any]


class SkillRecommender:
    """
    技能推荐引擎

    基于分析结果，推荐现有技能或建议生成新技能。
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent.parent
        self.registry_file = self.project_root / ".claude" / "skill_registry.json"
        self.templates_dir = self.project_root / "src" / "leo_skills" / "_templates"

    def recommend_for_intent(
        self,
        intent_category: str,
        keywords: List[str],
        top_n: int = 5
    ) -> List[SkillRecommendation]:
        """
        为意图推荐技能

        Args:
            intent_category: 意图类别
            keywords: 关键词
            top_n: 返回数量

        Returns:
            推荐列表
        """
        recommendations = []

        # 1. 从注册表搜索匹配技能
        registry_matches = self._search_registry(intent_category, keywords)
        recommendations.extend(registry_matches)

        # 2. 如果没有足够匹配，建议生成新技能
        if len(recommendations) < top_n:
            generated = self._suggest_new_skill(intent_category, keywords)
            if generated:
                recommendations.append(generated)

        # 按置信度排序
        recommendations.sort(key=lambda x: x.confidence, reverse=True)
        return recommendations[:top_n]

    def _search_registry(
        self,
        category: str,
        keywords: List[str]
    ) -> List[SkillRecommendation]:
        """从注册表搜索匹配技能"""
        matches = []

        if not self.registry_file.exists():
            return matches

        try:
            with open(self.registry_file, "r", encoding="utf-8") as f:
                registry = json.load(f)

            for skill_name, skill_info in registry.get("skills", {}).items():
                score = 0
                reasons = []

                # 分类匹配
                if skill_info.get("category") == category:
                    score += 30
                    reasons.append(f"分类匹配: {category}")

                # 触发词匹配
                triggers = skill_info.get("triggers", [])
                for kw in keywords:
                    if any(kw.lower() in t.lower() for t in triggers):
                        score += 20
                        reasons.append(f"触发词匹配: {kw}")

                # 描述匹配
                description = skill_info.get("description", "").lower()
                for kw in keywords:
                    if kw.lower() in description:
                        score += 10

                if score > 0:
                    confidence = min(0.95, score / 100)
                    matches.append(SkillRecommendation(
                        skill_name=skill_name,
                        skill_path=skill_info.get("path", ""),
                        confidence=confidence,
                        reason="; ".join(reasons),
                        category=skill_info.get("category", "unknown"),
                        estimated_effort="low",  # 已存在，直接调用
                        required_tools=self._extract_tools(skill_info)
                    ))

        except Exception as e:
            logger.error(f"Failed to search registry: {e}")

        return matches

    def _suggest_new_skill(
        self,
        category: str,
        keywords: List[str]
    ) -> Optional[SkillRecommendation]:
        """建议生成新技能"""
        # 基于模板推荐
        template = self._find_template(category)

        if template:
            skill_name = f"{category}_auto_skill"
            return SkillRecommendation(
                skill_name=skill_name,
                skill_path=f"src/leo_skills/{category}/{skill_name}",
                confidence=0.6,
                reason=f"基于高频意图 '{category}' 建议自动生成",
                category=category,
                estimated_effort="medium",
                required_tools=template.get("tools", [])
            )

        return None

    def _find_template(self, category: str) -> Optional[Dict[str, Any]]:
        """查找技能模板"""
        templates = {
            "development": {
                "tools": ["Read", "Write", "Bash", "Grep"],
                "template_file": "code_generator_skill.md"
            },
            "content": {
                "tools": ["Read", "Write", "WebFetch"],
                "template_file": "content_writer_skill.md"
            },
            "realestate": {
                "tools": ["Read", "Write", "Grep"],
                "template_file": "realestate_skill.md"
            },
            "loan": {
                "tools": ["Read", "Write", "Bash"],
                "template_file": "calculator_skill.md"
            },
            "ecommerce": {
                "tools": ["Read", "Write", "WebFetch", "Bash"],
                "template_file": "ecommerce_skill.md"
            },
            "analysis": {
                "tools": ["Read", "Grep", "Glob", "Bash"],
                "template_file": "analyzer_skill.md"
            },
        }

        return templates.get(category)

    def _extract_tools(self, skill_info: Dict[str, Any]) -> List[str]:
        """从技能信息中提取所需工具"""
        tools = []

        # 从元数据中提取
        metadata = skill_info.get("metadata", {})
        if "allowed-tools" in metadata:
            tools.extend(metadata["allowed-tools"])

        # 从技能名称推断
        name = skill_info.get("name", "")
        if "code" in name or "script" in name:
            tools.extend(["Read", "Write", "Bash"])
        if "content" in name or "write" in name:
            tools.extend(["Read", "Write", "WebFetch"])

        return list(set(tools))

    def generate_skill_code(self, request: SkillGenerationRequest) -> Dict[str, Any]:
        """
        生成技能代码框架

        Args:
            request: 生成请求

        Returns:
            生成的代码和元数据
        """
        template = self._find_template(request.intent_category)

        if not template:
            return {"error": f"No template found for category: {request.intent_category}"}

        skill_name = f"{request.intent_category}_auto_{self._generate_suffix()}"

        # 生成 SKILL.md
        skill_md = self._generate_skill_md(skill_name, request, template)

        # 生成 main.py
        main_py = self._generate_main_py(skill_name, request, template)

        # 生成 evolution.json
        evolution_json = {
            "version": "1.0.0",
            "evolution_history": [{
                "version": "1.0.0",
                "date": str(__import__('datetime').date.today()),
                "changes": f"Auto-generated based on intent: {request.intent_category}"
            }],
            "learned_tips": [],
            "learned_errors": []
        }

        return {
            "skill_name": skill_name,
            "category": request.intent_category,
            "files": {
                "SKILL.md": skill_md,
                "scripts/main.py": main_py,
                "evolution.json": json.dumps(evolution_json, indent=2)
            },
            "triggers": request.trigger_keywords
        }

    def _generate_skill_md(
        self,
        skill_name: str,
        request: SkillGenerationRequest,
        template: Dict[str, Any]
    ) -> str:
        """生成 SKILL.md"""
        tools_str = "\n  - ".join(template.get("tools", ["Read", "Write"]))

        return f"""---
name: {skill_name}
description: {request.description}
version: 1.0.0
category: {request.intent_category}
triggers:
  - {request.trigger_keywords[0] if request.trigger_keywords else skill_name}
compatibility:
  - claude-code
  - openclaw
tools:
  - {tools_str}
---

# {skill_name}

{request.description}

## 使用场景

{chr(10).join(f"- {ex}" for ex in request.example_inputs[:3])}

## 触发词

{chr(10).join(f"- `{kw}`" for kw in request.trigger_keywords)}

## 实现说明

自动生成的技能，基于高频意图分析。

## 版本历史

- 1.0.0: 初始版本 (自动生成)
"""

    def _generate_main_py(
        self,
        skill_name: str,
        request: SkillGenerationRequest,
        template: Dict[str, Any]
    ) -> str:
        """生成 main.py"""
        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{skill_name}

{request.description}
"""

import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(**kwargs) -> Dict[str, Any]:
    """
    主执行函数

    Args:
        **kwargs: 执行参数

    Returns:
        执行结果
    """
    logger.info(f"Executing {skill_name} with params: {{kwargs}}")

    # TODO: 实现具体逻辑
    result = {{
        "skill": "{skill_name}",
        "status": "success",
        "message": "Skill executed successfully",
        "data": {{}}
    }}

    return result


if __name__ == "__main__":
    # 测试运行
    print(main())
'''

    def _generate_suffix(self) -> str:
        """生成技能名称后缀"""
        import random
        import string
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

    def apply_recommendation(
        self,
        recommendation: SkillRecommendation,
        auto_create: bool = False
    ) -> Dict[str, Any]:
        """
        应用推荐

        Args:
            recommendation: 推荐项
            auto_create: 是否自动创建新技能

        Returns:
            应用结果
        """
        if recommendation.confidence >= 0.8:
            # 高置信度：直接使用现有技能
            return {
                "action": "use_existing",
                "skill": recommendation.skill_name,
                "path": recommendation.skill_path
            }

        elif recommendation.confidence >= 0.5:
            # 中等置信度：建议生成新技能
            if auto_create:
                request = SkillGenerationRequest(
                    intent_category=recommendation.category,
                    trigger_keywords=[recommendation.skill_name],
                    description=recommendation.reason,
                    example_inputs=[],
                    priority="medium",
                    context={}
                )
                generated = self.generate_skill_code(request)

                return {
                    "action": "auto_created",
                    "skill": generated["skill_name"],
                    "files": list(generated["files"].keys())
                }
            else:
                return {
                    "action": "suggest_create",
                    "skill": recommendation.skill_name,
                    "reason": recommendation.reason,
                    "effort": recommendation.estimated_effort
                }

        else:
            return {
                "action": "review_needed",
                "skill": recommendation.skill_name,
                "reason": "Confidence too low"
            }


# 便捷函数
def recommend_skill(intent: str, keywords: List[str]) -> List[SkillRecommendation]:
    """快速推荐入口"""
    recommender = SkillRecommender()
    return recommender.recommend_for_intent(intent, keywords)


if __name__ == "__main__":
    # 测试
    recs = recommend_skill("development", ["代码", "python", "脚本"])
    for r in recs:
        print(f"{r.skill_name}: {r.confidence:.2f} - {r.reason}")
