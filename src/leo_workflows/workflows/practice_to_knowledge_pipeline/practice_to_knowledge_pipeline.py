# -*- coding: utf-8 -*-
"""
Practice to Knowledge Pipeline - 实操沉淀流水线
================================================
从实践中提取技能和提示词，沉淀到知识库。

流程：提取 → 评估 → 存储 → 同步到 Obsidian
配置来源：definitions/practice_to_knowledge_pipeline.yaml（统一 YAML）
"""

import re
from typing import Any, Dict, List, Optional

from leo_workflows.pipeline_base import PipelineBase


class PracticeToKnowledgePipeline(PipelineBase):
    """
    实操沉淀流水线

    支持 3 种模式：
    - full: 完整沉淀（prompt + skill）
    - prompt_only: 只保存 prompt
    - skill_only: 只沉淀技能经验
    """

    yaml_name = "practice_to_knowledge_pipeline"

    def __init__(self):
        super().__init__()
        self._prompt_vault = None
        self._prompt_optimizer = None
        self._evolution_manager = None

    def _get_prompt_vault(self):
        if self._prompt_vault is None:
            try:
                from leo_skills.prompt_engineering.prompt_vault_skill import PromptVaultSkill
                self._prompt_vault = PromptVaultSkill()
            except ImportError:
                pass
        return self._prompt_vault

    def _get_prompt_optimizer(self):
        if self._prompt_optimizer is None:
            try:
                from leo_skills.prompt_engineering.prompt_optimizer_skill import PromptOptimizerSkill
                self._prompt_optimizer = PromptOptimizerSkill()
            except ImportError:
                pass
        return self._prompt_optimizer

    def _get_evolution_manager(self):
        if self._evolution_manager is None:
            try:
                from leo_skills.tools.skill_evolution_manager_skill import SkillEvolutionManagerSkill
                self._evolution_manager = SkillEvolutionManagerSkill()
            except ImportError:
                pass
        return self._evolution_manager

    def run(self, orchestrator=None, session_content: str = "", mode: str = "full", **kwargs) -> Dict[str, Any]:
        if not session_content:
            raise ValueError("缺少必要参数: session_content")

        results = {"mode": mode, "extracted_prompts": [], "evolved_skills": [], "obsidian_paths": []}
        extracted = self.extract_from_session(session_content)
        results["extracted_prompts"] = extracted.get("prompts", [])
        results["extracted_skills"] = extracted.get("skills", [])

        if mode in ("full", "prompt_only"):
            for prompt_data in results["extracted_prompts"]:
                save_result = self.save_prompt(
                    prompt_text=prompt_data.get("content", ""),
                    title=prompt_data.get("title", ""),
                    category=prompt_data.get("category", "custom"),
                    tags=prompt_data.get("tags", []),
                )
                if save_result.get("obsidian_path"):
                    results["obsidian_paths"].append(save_result["obsidian_path"])

        if mode in ("full", "skill_only"):
            for skill_data in results["extracted_skills"]:
                evolve_result = self.evolve_skill(
                    skill_name=skill_data.get("skill_name", ""),
                    feedback=skill_data.get("feedback", ""),
                )
                results["evolved_skills"].append(evolve_result)

        return results

    def save_prompt(self, prompt_text: str = "", title: str = "", category: str = "custom",
                    framework: str = "custom", tags: Optional[List[str]] = None,
                    use_case: str = "", **kwargs) -> Dict[str, Any]:
        """保存单个 prompt（评估 → 存储 → 同步 Obsidian）"""
        result = {"prompt_text": prompt_text[:50] + "...", "steps": []}
        optimizer = self._get_prompt_optimizer()
        score = 0
        if optimizer:
            eval_result = optimizer.evaluate_prompt(prompt_text)
            score = eval_result.get("score", 0)
            result["steps"].append({"step": "evaluate", "score": score})

        vault = self._get_prompt_vault()
        if vault:
            save_result = vault.execute(
                action="save", title=title, content=prompt_text,
                category=category, framework=framework, tags=tags or [], use_case=use_case,
            )
            prompt_id = save_result.get("result", {}).get("prompt_id", "")
            result["steps"].append({"step": "save", "prompt_id": prompt_id})
            if prompt_id:
                export_result = vault.execute(action="export_to_obsidian", prompt_id=prompt_id)
                files = export_result.get("result", {}).get("files", [])
                if files:
                    result["obsidian_path"] = files[0].get("path", "")
                    result["steps"].append({"step": "export_obsidian", "path": result["obsidian_path"]})

        result["score"] = score
        return result

    def evolve_skill(self, skill_name: str = "", feedback: str = "", **kwargs) -> Dict[str, Any]:
        """沉淀技能经验"""
        manager = self._get_evolution_manager()
        if manager:
            return manager.execute(action="evolve_from_feedback", skill_name=skill_name, feedback=feedback)
        return {"status": "skipped", "reason": "evolution_manager 不可用"}

    def extract_from_session(self, session_content: str) -> Dict[str, Any]:
        """从会话内容中提取可复用的 prompts 和技能经验"""
        prompts = []
        skills = []

        prompt_patterns = [
            r"(?:请|帮我|需要|要求)[^\n]{10,200}",
            r"(?:prompt|提示词)[：:]\s*([^\n]+)",
            r"```(?:prompt)?\n([\s\S]*?)```",
        ]
        for pattern in prompt_patterns:
            for match in re.findall(pattern, session_content, re.MULTILINE):
                content = match.strip() if isinstance(match, str) else match
                if len(content) > 10:
                    category = self._auto_categorize(content)
                    title = content[:30].replace("\n", " ").strip() + "..."
                    prompts.append({"title": title, "content": content, "category": category, "tags": ["自动提取"]})

        skill_patterns = [
            r"(?:学到|发现|总结|经验)[：:]\s*([^\n]+)",
            r"(?:步骤|流程|方法)[：:]\s*([\s\S]*?)(?:\n\n|\Z)",
        ]
        for pattern in skill_patterns:
            for match in re.findall(pattern, session_content, re.MULTILINE):
                content = match.strip()
                if len(content) > 10:
                    skills.append({"skill_name": "general", "feedback": content})

        return {"prompts": prompts, "skills": skills}

    def _auto_categorize(self, content: str) -> str:
        content_lower = content.lower()
        if any(w in content_lower for w in ["代码", "code", "函数", "api", "bug", "debug"]):
            return "coding"
        if any(w in content_lower for w in ["分析", "数据", "统计", "报告"]):
            return "analysis"
        if any(w in content_lower for w in ["写", "文章", "内容", "创作", "文案"]):
            return "writing"
        if any(w in content_lower for w in ["商业", "营销", "市场", "客户", "销售"]):
            return "business"
        return "custom"

    def get_required_skills(self) -> List[str]:
        return ["prompt_vault_skill", "prompt_optimizer_skill", "obsidian_sync_skill", "skill_evolution_manager_skill"]


def create_pipeline() -> PracticeToKnowledgePipeline:
    return PracticeToKnowledgePipeline()

practice_to_knowledge_pipeline = PracticeToKnowledgePipeline()
