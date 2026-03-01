# -*- coding: utf-8 -*-
"""
prompt_vault_skill - 提示词库管理技能

保存、版本控制、标签分类、搜索和Obsidian同步。
将实操中积累的提示词沉淀为可复用的知识资产。
"""

import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class PromptVaultSkill:
    """
    提示词库管理技能

    功能：
    - 保存提示词（自动评分、版本控制）
    - 搜索和浏览提示词库
    - 更新提示词（版本自增）
    - 导出到 Obsidian 知识库
    - 导入 GitHub 精选预置提示词
    """

    def __init__(self):
        self.name = "prompt_vault_skill"
        self.version = "1.0.0"
        self.description = "提示词库管理 - 沉淀可复用的提示词资产"

        # 路径配置
        self.skill_dir = Path(__file__).parent
        self.vault_file = self.skill_dir / "data" / "prompt_vault.json"
        self.presets_file = self.skill_dir / "data" / "presets.json"
        self.config = self._load_config()

        # 延迟加载依赖技能
        self._optimizer = None

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        config_path = self.skill_dir / "config" / "config.yaml"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {
            "obsidian_vault_path": "d:/桌面/Leo-Outputs",
            "obsidian_prompt_folder": "30-Resources/Prompts",
            "auto_score": True,
            "auto_export_to_obsidian": False,
        }

    def _load_vault(self) -> Dict[str, Any]:
        """加载提示词库"""
        if self.vault_file.exists():
            with open(self.vault_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"version": "1.0.0", "prompts": [], "stats": {"total": 0, "last_updated": None}}

    def _save_vault(self, vault: Dict[str, Any]):
        """保存提示词库"""
        vault["stats"]["total"] = len(vault["prompts"])
        vault["stats"]["last_updated"] = datetime.now().isoformat()
        self.vault_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.vault_file, "w", encoding="utf-8") as f:
            json.dump(vault, f, ensure_ascii=False, indent=2)

    def _get_optimizer(self):
        """延迟加载 prompt_optimizer_skill"""
        if self._optimizer is None:
            try:
                from leo_skills.prompt_engineering.prompt_optimizer_skill import PromptOptimizerSkill
                self._optimizer = PromptOptimizerSkill()
            except ImportError:
                self._optimizer = None
        return self._optimizer

    # ==================== 主入口 ====================

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行技能主入口

        Args:
            action: 动作类型 (save/search/list/get/update/use_prompt/auto_dispatch/export_to_obsidian/import_presets/record_feedback/evolve_prompt/evolution_history)
        """
        action = kwargs.get("action", "list")
        try:
            actions = {
                "save": self.save_prompt,
                "search": self.search_prompts,
                "list": self.list_prompts,
                "get": self.get_prompt,
                "update": self.update_prompt,
                "use_prompt": self.use_prompt,
                "auto_dispatch": self.auto_dispatch,
                "export_to_obsidian": self.export_to_obsidian,
                "import_presets": self.import_presets,
                "record_feedback": self.record_feedback,
                "evolve_prompt": self.evolve_prompt,
                "evolution_history": self.get_evolution_history,
            }
            handler = actions.get(action)
            if not handler:
                return {"status": "error", "skill": self.name, "error": f"未知动作: {action}"}

            result = handler(**{k: v for k, v in kwargs.items() if k != "action"})
            return {"status": "success", "skill": self.name, "action": action, "result": result}
        except Exception as e:
            return {"status": "error", "skill": self.name, "action": action, "error": str(e)}

    # ==================== 核心操作 ====================

    def save_prompt(
        self,
        title: str = "",
        content: str = "",
        category: str = "custom",
        framework: str = "custom",
        tags: Optional[List[str]] = None,
        use_case: str = "",
        **kwargs,
    ) -> Dict[str, Any]:
        """保存提示词到库中，自动评分"""
        if not content:
            return {"error": "提示词内容不能为空"}

        vault = self._load_vault()

        # 自动评分
        score = 0
        if self.config.get("auto_score", True):
            optimizer = self._get_optimizer()
            if optimizer:
                eval_result = optimizer.evaluate_prompt(content)
                score = eval_result.get("score", 0)

        # 自动生成标题
        if not title:
            title = content[:30].replace("\n", " ").strip() + "..."

        prompt_entry = {
            "id": str(uuid.uuid4())[:8],
            "title": title,
            "content": content,
            "category": category,
            "framework": framework,
            "version": 1,
            "score": score,
            "tags": tags or [],
            "use_case": use_case,
            "usage_count": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        vault["prompts"].append(prompt_entry)
        self._save_vault(vault)

        # 自动导出到 Obsidian
        if self.config.get("auto_export_to_obsidian", False):
            self._export_single_to_obsidian(prompt_entry)

        return {"prompt_id": prompt_entry["id"], "title": title, "score": score, "message": f"已保存提示词: {title}"}

    def search_prompts(
        self, query: str = "", category: Optional[str] = None, tags: Optional[List[str]] = None, **kwargs
    ) -> Dict[str, Any]:
        """搜索提示词"""
        vault = self._load_vault()
        results = vault["prompts"]

        if query:
            query_lower = query.lower()
            results = [
                p for p in results
                if query_lower in p["title"].lower()
                or query_lower in p["content"].lower()
                or query_lower in " ".join(p.get("tags", [])).lower()
            ]

        if category:
            results = [p for p in results if p["category"] == category]

        if tags:
            results = [p for p in results if any(t in p.get("tags", []) for t in tags)]

        return {"count": len(results), "prompts": results}

    def list_prompts(self, category: Optional[str] = None, sort_by: str = "updated_at", **kwargs) -> Dict[str, Any]:
        """列出所有提示词"""
        vault = self._load_vault()
        prompts = vault["prompts"]

        if category:
            prompts = [p for p in prompts if p["category"] == category]

        # 排序
        reverse = sort_by in ("updated_at", "created_at", "score", "usage_count")
        prompts.sort(key=lambda p: p.get(sort_by, ""), reverse=reverse)

        # 返回摘要（不含完整 content）
        summaries = [
            {
                "id": p["id"],
                "title": p["title"],
                "category": p["category"],
                "framework": p["framework"],
                "score": p["score"],
                "version": p["version"],
                "tags": p["tags"],
                "usage_count": p["usage_count"],
                "updated_at": p["updated_at"],
            }
            for p in prompts
        ]

        return {"total": len(summaries), "prompts": summaries}

    def get_prompt(self, prompt_id: str = "", **kwargs) -> Dict[str, Any]:
        """获取单个提示词，使用次数 +1"""
        vault = self._load_vault()
        for p in vault["prompts"]:
            if p["id"] == prompt_id:
                p["usage_count"] = p.get("usage_count", 0) + 1
                self._save_vault(vault)
                return {"prompt": p}
        return {"error": f"未找到提示词: {prompt_id}"}

    def update_prompt(self, prompt_id: str = "", **kwargs) -> Dict[str, Any]:
        """更新提示词，版本自增"""
        vault = self._load_vault()
        for p in vault["prompts"]:
            if p["id"] == prompt_id:
                # 更新字段
                for key in ("title", "content", "category", "framework", "tags", "use_case"):
                    if key in kwargs and kwargs[key] is not None:
                        p[key] = kwargs[key]

                # 如果内容变了，重新评分
                if "content" in kwargs:
                    optimizer = self._get_optimizer()
                    if optimizer:
                        p["score"] = optimizer.evaluate_prompt(kwargs["content"]).get("score", p["score"])

                p["version"] = p.get("version", 1) + 1
                p["updated_at"] = datetime.now().isoformat()
                self._save_vault(vault)
                return {"prompt_id": prompt_id, "version": p["version"], "message": "已更新"}
        return {"error": f"未找到提示词: {prompt_id}"}

    # ==================== 使用提示词 ====================

    def use_prompt(
        self,
        prompt_id: str = "",
        query: str = "",
        variables: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        使用提示词 - 自动匹配、填充变量、追踪使用次数

        三种匹配方式（按优先级）：
        1. prompt_id 精确匹配
        2. query 模糊匹配（框架名 > 标题 > 标签 > 内容）
        3. 返回错误

        Args:
            prompt_id: 直接指定 prompt ID
            query: 模糊匹配关键词（如 "CRISPE"、"代码审查"）
            variables: 变量填充字典，如 {"code": "...", "topic": "..."}
        """
        vault = self._load_vault()
        prompt = None

        # 按 ID 查找
        if prompt_id:
            for p in vault["prompts"]:
                if p["id"] == prompt_id:
                    prompt = p
                    break

        # 按 query 模糊匹配
        if not prompt and query:
            prompt = self._fuzzy_match_prompt(vault["prompts"], query)

        if not prompt:
            # 返回可用的提示词列表帮助用户选择
            available = [{"id": p["id"], "title": p["title"], "framework": p["framework"]} for p in vault["prompts"][:10]]
            return {"error": f"未找到匹配的提示词: {prompt_id or query}", "available": available}

        # 填充变量
        content = prompt["content"]
        filled_vars = []
        if variables:
            for key, value in variables.items():
                placeholder = f"{{{key}}}"
                if placeholder in content:
                    content = content.replace(placeholder, str(value))
                    filled_vars.append(key)

        # 追踪使用
        prompt["usage_count"] = prompt.get("usage_count", 0) + 1
        prompt["last_used"] = datetime.now().isoformat()
        self._save_vault(vault)

        # 提取未填充的变量占位符
        unfilled = re.findall(r"\{(\w+)\}", content)

        return {
            "prompt_id": prompt["id"],
            "title": prompt["title"],
            "framework": prompt["framework"],
            "content": content,
            "filled_variables": filled_vars,
            "unfilled_variables": unfilled,
            "usage_count": prompt["usage_count"],
            "score": prompt.get("score", 0),
            "message": f"已加载提示词: {prompt['title']} (v{prompt.get('version', 1)})",
        }

    def _fuzzy_match_prompt(self, prompts: List[Dict], query: str) -> Optional[Dict]:
        """模糊匹配提示词（框架名 > 标题 > 标签 > 内容）"""
        q = query.lower().strip()

        # 1. 精确匹配框架名（如 "CRISPE"、"CO-STAR"）
        for p in prompts:
            if p.get("framework", "").lower() == q:
                return p

        # 2. 标题包含关键词
        for p in prompts:
            if q in p["title"].lower():
                return p

        # 3. 标签匹配
        for p in prompts:
            if any(q in t.lower() for t in p.get("tags", [])):
                return p

        # 4. 内容包含
        for p in prompts:
            if q in p.get("content", "").lower():
                return p

        return None

    def auto_dispatch(self, user_input: str = "", variables: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """
        自然语言自动调度 - 从用户描述中识别意图、匹配提示词、组装可执行任务

        流程：
        1. 解析用户输入，提取关键词
        2. 在提示词库中模糊匹配最佳 prompt
        3. 从用户输入中提取可填充的变量
        4. 返回组装好的任务（prompt 内容 + 填充后的变量 + 执行建议）

        Args:
            user_input: 用户的自然语言描述，如 "帮我审查这段Python代码" 或 "用CRISPE框架写一篇产品介绍"
            variables: 额外的变量填充字典
        """
        if not user_input:
            return {"error": "请输入任务描述"}

        vault = self._load_vault()
        prompts = vault["prompts"]

        # 1. 尝试从输入中提取框架名或关键词
        matched_prompt = None
        match_reason = ""

        # 检查是否明确指定了框架（如 "用CRISPE框架..."）
        framework_match = re.search(
            r"(?:用|使用|套用|应用)\s*([A-Za-z][A-Za-z0-9\-.]*[A-Za-z0-9]|[A-Za-z0-9]+)",
            user_input
        )
        if framework_match:
            query = framework_match.group(1)
            matched_prompt = self._fuzzy_match_prompt(prompts, query)
            if matched_prompt:
                match_reason = f"匹配框架: {query}"

        # 如果没有明确框架，按任务类型智能匹配
        if not matched_prompt:
            matched_prompt, match_reason = self._smart_match_by_task(prompts, user_input)

        if not matched_prompt:
            return {
                "matched": False,
                "message": "未找到匹配的提示词，将使用通用对话模式",
                "original_input": user_input,
                "suggestion": "可以先用 list 查看所有可用提示词",
            }

        # 2. 从用户输入中提取可能的变量值
        auto_vars = self._extract_variables_from_input(user_input, matched_prompt["content"])
        if variables:
            auto_vars.update(variables)

        # 3. 填充变量
        content = matched_prompt["content"]
        filled_vars = []
        for key, value in auto_vars.items():
            placeholder = f"{{{key}}}"
            if placeholder in content:
                content = content.replace(placeholder, str(value))
                filled_vars.append(key)

        # 4. 追踪使用
        matched_prompt["usage_count"] = matched_prompt.get("usage_count", 0) + 1
        matched_prompt["last_used"] = datetime.now().isoformat()
        self._save_vault(vault)

        # 5. 提取未填充的变量
        unfilled = re.findall(r"\{(\w+)\}", content)

        return {
            "matched": True,
            "prompt_id": matched_prompt["id"],
            "title": matched_prompt["title"],
            "framework": matched_prompt["framework"],
            "content": content,
            "match_reason": match_reason,
            "filled_variables": filled_vars,
            "unfilled_variables": unfilled,
            "usage_count": matched_prompt["usage_count"],
            "score": matched_prompt.get("score", 0),
            "original_input": user_input,
            "message": f"已自动匹配提示词: {matched_prompt['title']} ({match_reason})",
        }

    def _smart_match_by_task(self, prompts: List[Dict], user_input: str):
        """根据任务描述智能匹配最佳提示词"""
        input_lower = user_input.lower()

        # 任务类型关键词 → 分类/标签映射
        task_signals = [
            (["审查", "review", "代码审查", "code review", "检查代码"], "代码审查"),
            (["架构", "设计方案", "技术方案", "技术选型", "系统设计"], "架构"),
            (["分析", "商业分析", "市场分析", "竞品", "swot"], "商业分析"),
            (["写作", "创作", "文章", "内容", "公众号", "文案"], "内容创作"),
            (["推理", "思考", "分析问题", "逻辑"], "推理"),
            (["调研", "研究", "research"], "研究"),
            (["产品", "需求", "prd", "用户故事"], "产品"),
        ]

        for keywords, search_term in task_signals:
            if any(kw in input_lower for kw in keywords):
                matched = self._fuzzy_match_prompt(prompts, search_term)
                if matched:
                    trigger = next(kw for kw in keywords if kw in input_lower)
                    return matched, f"任务关键词: {trigger}"

        # 兜底：全文模糊搜索
        for p in prompts:
            title_lower = p["title"].lower()
            tags_lower = " ".join(p.get("tags", [])).lower()
            if any(word in title_lower or word in tags_lower for word in input_lower.split() if len(word) > 1):
                return p, "关键词模糊匹配"

        return None, ""

    def _extract_variables_from_input(self, user_input: str, prompt_content: str) -> Dict[str, str]:
        """从用户输入中自动提取可填充的变量值"""
        variables = {}

        # 提取 prompt 中的变量占位符
        placeholders = re.findall(r"\{(\w+)\}", prompt_content)
        if not placeholders:
            return variables

        # 常见变量的提取规则
        extraction_rules = {
            "code": (r"```[\s\S]*?```|`[^`]+`", lambda m: m.group(0).strip("`").strip()),
            "topic": (r"(?:关于|主题|topic)[：:\s]*(.+?)(?:[，。,.]|$)", lambda m: m.group(1).strip()),
            "question": (r"(?:问题|question)[：:\s]*(.+?)(?:[？?]|$)", lambda m: m.group(1).strip()),
            "requirement": (r"(?:需求|requirement)[：:\s]*(.+?)(?:[，。,.]|$)", lambda m: m.group(1).strip()),
            "industry": (r"(?:行业|industry)[：:\s]*(.+?)(?:[，。,.]|$)", lambda m: m.group(1).strip()),
        }

        for var_name in placeholders:
            if var_name in extraction_rules:
                pattern, extractor = extraction_rules[var_name]
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    variables[var_name] = extractor(match)

        return variables

    # ==================== Obsidian 导出 ====================

    def export_to_obsidian(self, prompt_id: Optional[str] = None, export_all: bool = False, **kwargs) -> Dict[str, Any]:
        """导出提示词到 Obsidian"""
        vault = self._load_vault()
        exported = []

        if export_all:
            prompts_to_export = vault["prompts"]
        elif prompt_id:
            prompts_to_export = [p for p in vault["prompts"] if p["id"] == prompt_id]
        else:
            return {"error": "请指定 prompt_id 或 export_all=True"}

        for p in prompts_to_export:
            path = self._export_single_to_obsidian(p)
            if path:
                exported.append({"id": p["id"], "title": p["title"], "path": str(path)})

        return {"exported_count": len(exported), "files": exported}

    def _export_single_to_obsidian(self, prompt: Dict[str, Any]) -> Optional[Path]:
        """导出单个提示词到 Obsidian"""
        obsidian_path = Path(self.config.get("obsidian_vault_path", "d:/桌面/Leo-Outputs"))
        prompt_folder = obsidian_path / self.config.get("obsidian_prompt_folder", "30-Resources/Prompts")
        prompt_folder.mkdir(parents=True, exist_ok=True)

        # 按分类创建子目录
        category_folder = prompt_folder / prompt.get("category", "custom")
        category_folder.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        safe_title = prompt["title"].replace("/", "-").replace("\\", "-").replace(":", "-")[:50]
        file_path = category_folder / f"{safe_title}.md"

        # 生成 Obsidian 笔记内容
        tags_str = ", ".join(prompt.get("tags", []))
        avg_rating = prompt.get("avg_rating", 0)
        feedback_count = len(prompt.get("feedback_history", []))
        evolution_count = len(prompt.get("evolution_history", []))
        last_evolved = prompt.get("last_evolved", "")
        note_content = f"""---
created: {prompt.get("created_at", datetime.now().isoformat())}
prompt_id: {prompt["id"]}
category: {prompt.get("category", "custom")}
framework: {prompt.get("framework", "custom")}
version: {prompt.get("version", 1)}
score: {prompt.get("score", 0)}
tags: [提示词, {prompt.get("category", "custom")}, {tags_str}]
usage_count: {prompt.get("usage_count", 0)}
avg_rating: {avg_rating}
feedback_count: {feedback_count}
evolution_count: {evolution_count}
last_evolved: "{last_evolved}"
---

# {prompt["title"]}

## 提示词内容

```
{prompt["content"]}
```

## 元信息

- 分类: {prompt.get("category", "custom")}
- 框架: {prompt.get("framework", "custom")}
- 评分: {prompt.get("score", 0)}/100
- 版本: v{prompt.get("version", 1)}
- 使用次数: {prompt.get("usage_count", 0)}
- 平均评价: {avg_rating}/5（{feedback_count}次反馈）
- 进化次数: {evolution_count}

## 使用场景

{prompt.get("use_case", "待补充")}

---
*由 Leo System prompt_vault_skill 自动生成*
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(note_content)

        return file_path

    # ==================== 预置导入 ====================

    def import_presets(self, source: str = "builtin", **kwargs) -> Dict[str, Any]:
        """导入预置提示词"""
        if self.presets_file.exists():
            with open(self.presets_file, "r", encoding="utf-8") as f:
                presets = json.load(f)
        else:
            presets = self._get_builtin_presets()

        vault = self._load_vault()
        existing_titles = {p["title"] for p in vault["prompts"]}
        imported = 0

        for preset in presets.get("prompts", []):
            if preset["title"] not in existing_titles:
                preset["id"] = str(uuid.uuid4())[:8]
                preset["created_at"] = datetime.now().isoformat()
                preset["updated_at"] = datetime.now().isoformat()
                preset.setdefault("usage_count", 0)
                preset.setdefault("version", 1)
                vault["prompts"].append(preset)
                imported += 1

        self._save_vault(vault)
        return {"imported": imported, "total": len(vault["prompts"])}

    def _get_builtin_presets(self) -> Dict[str, Any]:
        """内置精选预置提示词（来自 GitHub 最佳实践）"""
        return {"prompts": []}  # 预置已迁移到 data/presets.json

    # ==================== 进化能力 ====================

    def record_feedback(
        self,
        prompt_id: str = "",
        rating: int = 3,
        success: bool = True,
        context: str = "",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        记录使用反馈，达到阈值时自动触发进化

        Args:
            prompt_id: 提示词 ID
            rating: 评分 1-5（1=很差, 5=很好）
            success: 是否达到预期效果
            context: 使用场景和备注
        """
        if not prompt_id:
            return {"error": "请指定 prompt_id"}

        vault = self._load_vault()
        for p in vault["prompts"]:
            if p["id"] == prompt_id:
                # 初始化反馈历史
                p.setdefault("feedback_history", [])
                p.setdefault("evolution_history", [])

                # 追加反馈
                feedback_entry = {
                    "rating": max(1, min(5, rating)),
                    "success": success,
                    "context": context,
                    "timestamp": datetime.now().isoformat(),
                }
                p["feedback_history"].append(feedback_entry)

                # 更新平均评分
                ratings = [f["rating"] for f in p["feedback_history"]]
                p["avg_rating"] = round(sum(ratings) / len(ratings), 2)

                self._save_vault(vault)

                # 检查是否触发自动进化
                evolved = False
                evo_config = self.config.get("evolution", {})
                if evo_config.get("auto_evolve", True):
                    evolved = self._check_and_trigger_evolution(p, vault)

                return {
                    "prompt_id": prompt_id,
                    "feedback_count": len(p["feedback_history"]),
                    "avg_rating": p["avg_rating"],
                    "auto_evolved": evolved,
                    "message": f"已记录反馈（评分: {rating}/5）" + ("，已触发自动进化" if evolved else ""),
                }

        return {"error": f"未找到提示词: {prompt_id}"}

    def _check_and_trigger_evolution(self, prompt: Dict[str, Any], vault: Dict[str, Any]) -> bool:
        """检查是否满足自动进化条件"""
        evo_config = self.config.get("evolution", {})
        min_feedback = evo_config.get("min_feedback_count", 3)
        low_rating = evo_config.get("low_rating_threshold", 3.5)
        min_usage = evo_config.get("min_usage_for_score_check", 5)
        low_score = evo_config.get("low_score_threshold", 70)

        feedback_count = len(prompt.get("feedback_history", []))
        avg_rating = prompt.get("avg_rating", 5.0)
        usage_count = prompt.get("usage_count", 0)
        score = prompt.get("score", 100)

        # 条件1: 反馈够多 且 评分低
        if feedback_count >= min_feedback and avg_rating < low_rating:
            result = self._do_evolve(prompt, vault, f"平均评分 {avg_rating} 低于阈值 {low_rating}（{feedback_count}次反馈）")
            return result.get("evolved", False)

        # 条件2: 使用够多 且 评分低
        if usage_count >= min_usage and score < low_score:
            result = self._do_evolve(prompt, vault, f"评分 {score} 低于阈值 {low_score}（已使用{usage_count}次）")
            return result.get("evolved", False)

        return False

    def evolve_prompt(self, prompt_id: str = "", reason: str = "", **kwargs) -> Dict[str, Any]:
        """
        手动触发 prompt 进化

        Args:
            prompt_id: 提示词 ID
            reason: 进化原因（可选）
        """
        if not prompt_id:
            return {"error": "请指定 prompt_id"}

        vault = self._load_vault()
        for p in vault["prompts"]:
            if p["id"] == prompt_id:
                p.setdefault("feedback_history", [])
                p.setdefault("evolution_history", [])
                return self._do_evolve(p, vault, reason or "手动触发进化")

        return {"error": f"未找到提示词: {prompt_id}"}

    def _do_evolve(self, prompt: Dict[str, Any], vault: Dict[str, Any], reason: str) -> Dict[str, Any]:
        """执行进化：优化 prompt 内容并记录历史"""
        optimizer = self._get_optimizer()
        if not optimizer:
            return {"evolved": False, "reason": "prompt_optimizer_skill 不可用"}

        old_content = prompt["content"]
        old_score = prompt.get("score", 0)

        # 从反馈中提取改进方向
        feedback_summary = self._summarize_feedback(prompt.get("feedback_history", []))

        # 调用 optimizer 优化
        opt_result = optimizer.optimize_prompt(
            prompt=old_content,
            goal="general",
            context={"feedback": feedback_summary},
        )

        new_content = opt_result.get("optimized_prompt", old_content)
        new_score = opt_result.get("score_after", old_score)

        # 如果优化后没有实质变化，跳过
        if new_content.strip() == old_content.strip() and new_score <= old_score:
            return {"evolved": False, "reason": "优化后无实质改进"}

        # 记录进化历史（快照旧版本）
        evolution_entry = {
            "version": prompt.get("version", 1),
            "content_snapshot": old_content,
            "score_before": old_score,
            "score_after": new_score,
            "reason": reason,
            "feedback_summary": feedback_summary,
            "timestamp": datetime.now().isoformat(),
        }
        prompt.setdefault("evolution_history", []).append(evolution_entry)

        # 更新 prompt
        prompt["content"] = new_content
        prompt["score"] = new_score
        prompt["version"] = prompt.get("version", 1) + 1
        prompt["updated_at"] = datetime.now().isoformat()
        prompt["last_evolved"] = datetime.now().isoformat()

        self._save_vault(vault)

        # 重新导出到 Obsidian
        self._export_single_to_obsidian(prompt)

        return {
            "evolved": True,
            "prompt_id": prompt["id"],
            "title": prompt["title"],
            "version": prompt["version"],
            "score_before": old_score,
            "score_after": new_score,
            "improvement": new_score - old_score,
            "reason": reason,
            "message": f"已进化: v{prompt['version']-1} ({old_score}分) -> v{prompt['version']} ({new_score}分)",
        }

    def _summarize_feedback(self, feedback_history: List[Dict[str, Any]]) -> str:
        """从反馈历史中提取改进方向摘要"""
        if not feedback_history:
            return "无反馈记录"

        contexts = [f.get("context", "") for f in feedback_history if f.get("context")]
        low_ratings = [f for f in feedback_history if f.get("rating", 5) <= 3]
        failures = [f for f in feedback_history if not f.get("success", True)]

        parts = []
        if contexts:
            parts.append("用户反馈: " + "; ".join(contexts[-5:]))  # 最近5条
        if low_ratings:
            parts.append(f"低评分次数: {len(low_ratings)}/{len(feedback_history)}")
        if failures:
            parts.append(f"失败次数: {len(failures)}/{len(feedback_history)}")

        return " | ".join(parts) if parts else "无具体反馈"

    def get_evolution_history(self, prompt_id: str = "", **kwargs) -> Dict[str, Any]:
        """查看某个 prompt 的进化历史"""
        if not prompt_id:
            return {"error": "请指定 prompt_id"}

        vault = self._load_vault()
        for p in vault["prompts"]:
            if p["id"] == prompt_id:
                history = p.get("evolution_history", [])
                return {
                    "prompt_id": prompt_id,
                    "title": p["title"],
                    "current_version": p.get("version", 1),
                    "current_score": p.get("score", 0),
                    "avg_rating": p.get("avg_rating", 0),
                    "feedback_count": len(p.get("feedback_history", [])),
                    "evolution_count": len(history),
                    "history": history,
                }

        return {"error": f"未找到提示词: {prompt_id}"}

    # ==================== 工具方法 ====================

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        vault = self._load_vault()
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "actions": ["save", "search", "list", "get", "update", "use_prompt",
                        "export_to_obsidian", "import_presets",
                        "record_feedback", "evolve_prompt", "evolution_history"],
            "total_prompts": vault["stats"]["total"],
            "categories": ["coding", "analysis", "writing", "business", "system", "custom"],
            "frameworks": ["CO-STAR", "RISEN", "TIDD-EC", "chain_of_thought", "few_shot", "xml_structure", "custom"],
        }


# 向后兼容
Prompt_Vault_Skill = PromptVaultSkill


def main():
    """入口函数 - 演示用法"""
    print("=" * 60)
    print("Prompt Vault Skill - 演示")
    print("=" * 60)

    skill = PromptVaultSkill()

    # 导入预置
    print("\n1. 导入预置提示词")
    result = skill.execute(action="import_presets")
    print(f"  导入: {result['result']['imported']} 个")

    # 列出所有
    print("\n2. 列出提示词库")
    result = skill.execute(action="list")
    for p in result["result"]["prompts"][:3]:
        print(f"  [{p['id']}] {p['title']} (评分:{p['score']}, 框架:{p['framework']})")

    # 保存新 prompt
    print("\n3. 保存新提示词")
    result = skill.execute(
        action="save",
        title="测试提示词",
        content="请帮我分析这段代码的性能瓶颈，给出优化建议",
        category="coding",
        tags=["测试", "性能"],
    )
    print(f"  保存成功: {result['result']['message']}")

    # 搜索
    print("\n4. 搜索提示词")
    result = skill.execute(action="search", query="代码")
    print(f"  找到: {result['result']['count']} 个匹配")

    print("\n" + "=" * 60)
    print("演示完成！")
    return skill


if __name__ == "__main__":
    main()
