import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from leo_skills.core.evolution import EvolvableSkill


class SkillEvolutionManagerSkill(EvolvableSkill):
    """
    技能持续改进管理器

    基于用户反馈持续改进技能，与现有 evolution 框架深度集成。
    """

    def __init__(self, skill_name: str = "skill_evolution_manager", config_path: Optional[str] = None):
        super().__init__(skill_name, Path(__file__).parent / "evolution.json")
        # 从 skill_evolution_manager_skill/ 向上两级到 leo_skills
        self.skills_root = Path(__file__).parents[2]
        self.config_path = Path(config_path) if config_path else Path(__file__).parent / "config.yaml"
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_path.exists():
            import yaml
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {
            "evolution_dir": "src/leo_skills/core/evolution",
            "auto_update_skill_md": True,
            "batch_scan_depth": 3,
            "merge_strategy": "smart",  # smart, append, replace
        }

    def execute(self, action: str = "evolve_from_feedback", **kwargs) -> Dict[str, Any]:
        """
        执行进化管理操作

        Args:
            action: 操作类型
                - evolve_from_feedback: 从反馈进化
                - evolve_from_session: 从会话进化
                - batch_evolve: 批量进化
                - get_history: 获取进化历史
                - merge_experience: 合并经验
                - analyze_patterns: 分析进化模式
            skill_name: 技能名称
            feedback: 反馈内容
            session_log: 会话日志路径

        Returns:
            执行结果
        """
        actions = {
            "evolve_from_feedback": self._evolve_from_feedback,
            "evolve_from_session": self._evolve_from_session,
            "batch_evolve": self._batch_evolve,
            "get_history": self._get_history,
            "merge_experience": self._merge_experience,
            "analyze_patterns": self._analyze_patterns,
        }

        if action not in actions:
            return {"success": False, "error": f"Unknown action: {action}"}

        return actions[action](**kwargs)

    def _evolve_from_feedback(self, skill_name: str, feedback: str, **kwargs) -> Dict[str, Any]:
        """从用户反馈进化技能"""
        # 找到技能的 evolution.json
        evolution_path = self._find_evolution_path(skill_name)

        if not evolution_path:
            return {"success": False, "error": f"Skill not found: {skill_name}"}

        # 提取反馈中的经验
        extracted_tips = self._extract_tips_from_feedback(feedback)

        # 加载现有进化数据
        evolution_data = self._load_evolution_data(evolution_path)

        # 添加新经验
        new_tips = []
        for tip in extracted_tips:
            if tip not in evolution_data.get("tips", []):
                entry = {
                    "tip": tip,
                    "context": feedback,
                    "timestamp": datetime.now().isoformat(),
                    "source": "user_feedback"
                }
                evolution_data.setdefault("tips", []).append(entry)
                evolution_data.setdefault("history", []).append(entry)
                new_tips.append(tip)

        # 保存
        self._save_evolution_data(evolution_path, evolution_data)

        # 更新 SKILL.md
        if self.config.get("auto_update_skill_md", True):
            self._update_skill_md(skill_name, evolution_data)

        self.learn(f"Evolved {skill_name} with feedback: {len(new_tips)} new tips")

        return {
            "success": True,
            "skill_name": skill_name,
            "new_tips": new_tips,
            "total_tips": len(evolution_data.get("tips", []))
        }

    def _extract_tips_from_feedback(self, feedback: str) -> List[str]:
        """从反馈中提取经验"""
        tips = []

        # 匹配 "Add/Use/Remember/Always + verb" 模式
        patterns = [
            r"(?:Add|Use|Remember|Always|Don't forget to|No debe|Asegúrate de)\s+(.+?)(?:\.|，|$)",
            r"(?:When|In case of|Si|Al)\s+(.+?)(?:\.|，|$)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, feedback, re.IGNORECASE)
            for match in matches:
                tip = match.strip()
                if len(tip) > 10 and len(tip) < 200:
                    tips.append(tip)

        # 如果没有匹配，返回原始反馈作为提示
        if not tips and len(feedback) > 10:
            tips = [feedback[:100] + "..." if len(feedback) > 100 else feedback]

        return tips

    def _find_evolution_path(self, skill_name: str) -> Optional[Path]:
        """查找技能的 evolution.json 路径"""
        # 首先检查 skills_root 下是否有该名称的目录（snake_case 格式）
        skill_dir = self.skills_root / skill_name
        if skill_dir.exists():
            for ep in [skill_dir / "evolution.json", skill_dir / f"{skill_name}_evolution.json"]:
                if ep.exists():
                    return ep

        # 搜索所有技能目录
        for category in ["content-creation", "development", "utilities", "tools", "intelligence"]:
            category_path = self.skills_root / category
            if not category_path.exists():
                continue

            for skill_subdir in category_path.iterdir():
                if skill_subdir.name == skill_name:
                    for ep in [skill_subdir / "evolution.json", skill_subdir / f"{skill_name}_evolution.json"]:
                        if ep.exists():
                            return ep

        return None

    def _load_evolution_data(self, path: Path) -> Dict[str, Any]:
        """加载进化数据"""
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[Warning] Failed to load {path}: {e}")

        return {"version": 1, "tips": [], "history": []}

    def _save_evolution_data(self, path: Path, data: Dict):
        """保存进化数据"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _update_skill_md(self, skill_name: str, evolution_data: Dict):
        """更新 SKILL.md 的进化部分"""
        # 找到 SKILL.md
        skill_md_path = None
        for category in ["content-creation", "development", "utilities", "tools", "intelligence"]:
            path = self.skills_root / category / skill_name / "SKILL.md"
            if path.exists():
                skill_md_path = path
                break

        if not skill_md_path:
            return

        # 读取现有内容
        content = skill_md_path.read_text(encoding="utf-8")

        # 生成新的进化部分
        tips = evolution_data.get("tips", [])
        evolution_section = "\n## 进化历史\n\n"

        if tips:
            evolution_section += f"已积累 {len(tips)} 条经验：\n\n"
            for i, tip in enumerate(tips[-10:], 1):  # 只显示最近10条
                tip_text = tip.get("tip", tip) if isinstance(tip, dict) else tip
                evolution_section += f"{i}. {tip_text}\n"
        else:
            evolution_section += "暂无进化经验。\n"

        # 检查是否已有进化部分
        if "## 进化历史" in content:
            # 替换现有部分
            pattern = r"## 进化历史\n\n.*?(?=\n## |\n# |\Z)"
            content = re.sub(pattern, evolution_section.rstrip(), content, flags=re.DOTALL)
        else:
            # 添加到末尾
            content += evolution_section

        # 写回
        skill_md_path.write_text(content, encoding="utf-8")

    def _evolve_from_session(self, session_log: str, **kwargs) -> Dict[str, Any]:
        """从会话日志进化"""
        if not Path(session_log).exists():
            return {"success": False, "error": "Session log not found"}

        content = Path(session_log).read_text(encoding="utf-8")

        # 提取所有反馈
        feedbacks = self._extract_feedbacks_from_session(content)

        results = []
        for skill_name, feedback in feedbacks:
            result = self._evolve_from_feedback(skill_name=skill_name, feedback=feedback)
            results.append(result)

        return {
            "success": True,
            "total_extracted": len(feedbacks),
            "successful_evolutions": sum(1 for r in results if r.get("success")),
            "results": results
        }

    def _extract_feedbacks_from_session(self, content: str) -> List[tuple]:
        """从会话中提取反馈"""
        feedbacks = []

        # 匹配 "Skill: feedback" 模式
        pattern = r"(\w+_skill)\s*[:：]\s*(.+?)(?=\n\w+_skill\s*:|$)"
        matches = re.findall(pattern, content, re.DOTALL)

        for skill_name, feedback in matches:
            feedback = feedback.strip()[:500]  # 限制长度
            feedbacks.append((skill_name, feedback))

        return feedbacks

    def _batch_evolve(self, **kwargs) -> Dict[str, Any]:
        """批量进化所有技能"""
        # 扫描所有 evolution.json
        evolution_files = list(Path(self.skills_root).rglob("*_evolution.json"))
        evolution_files.extend(list(Path(self.skills_root).rglob("evolution.json")))

        results = []
        for ev_path in evolution_files[:50]:  # 限制数量
            skill_name = ev_path.stem.replace("_evolution", "")
            # 获取最近的修改
            stats = ev_path.stat()
            if stats.st_mtime > (datetime.now().timestamp() - 86400):  # 最近24小时
                results.append({
                    "skill": skill_name,
                    "path": str(ev_path),
                    "status": "recently_updated"
                })

        return {
            "success": True,
            "total_evolution_files": len(evolution_files),
            "recently_updated": len(results),
            "files": results[:20]
        }

    def _get_history(self, skill_name: str, **kwargs) -> Dict[str, Any]:
        """获取技能进化历史"""
        evolution_path = self._find_evolution_path(skill_name)

        if not evolution_path:
            return {"success": False, "error": f"Skill not found: {skill_name}"}

        data = self._load_evolution_data(evolution_path)

        return {
            "success": True,
            "skill_name": skill_name,
            "evolution_path": str(evolution_path),
            "total_tips": len(data.get("tips", [])),
            "history": data.get("history", []),
            "version": data.get("version", 1)
        }

    def _merge_experience(self, skill_name: str, source_skill: str, strategy: str = "smart", **kwargs) -> Dict[str, Any]:
        """合并其他技能的经验"""
        target_path = self._find_evolution_path(skill_name)
        source_path = self._find_evolution_path(source_skill)

        if not target_path:
            return {"success": False, "error": f"Target skill not found: {skill_name}"}
        if not source_path:
            return {"success": False, "error": f"Source skill not found: {source_skill}"}

        target_data = self._load_evolution_data(target_path)
        source_data = self._load_evolution_data(source_path)

        source_tips = source_data.get("tips", [])
        merged_tips = target_data.get("tips", [])

        new_tips = []
        for tip in source_tips:
            tip_text = tip.get("tip", tip) if isinstance(tip, dict) else tip
            if tip_text not in [t.get("tip", t) if isinstance(t, dict) else t for t in merged_tips]:
                new_entry = {
                    "tip": tip_text,
                    "context": f"Merged from {source_skill}",
                    "timestamp": datetime.now().isoformat(),
                    "source": "merge",
                    "original_source": source_skill
                }
                merged_tips.append(new_entry)
                new_tips.append(tip_text)

        target_data["tips"] = merged_tips
        self._save_evolution_data(target_path, target_data)

        self.learn(f"Merged {len(new_tips)} tips from {source_skill} to {skill_name}")

        return {
            "success": True,
            "target_skill": skill_name,
            "source_skill": source_skill,
            "new_tips_merged": len(new_tips),
            "total_tips": len(merged_tips)
        }

    def _analyze_patterns(self, **kwargs) -> Dict[str, Any]:
        """分析进化模式"""
        # 收集所有进化数据
        all_data = []
        evolution_files = list(Path(self.skills_root).rglob("*_evolution.json"))
        evolution_files.extend(list(Path(self.skills_root).rglob("evolution.json")))

        for ev_path in evolution_files:
            data = self._load_evolution_data(ev_path)
            skill_name = ev_path.stem.replace("_evolution", "")
            all_data.append({
                "skill": skill_name,
                "tips_count": len(data.get("tips", [])),
                "tips": [t.get("tip", t) if isinstance(t, dict) else t for t in data.get("tips", [])]
            })

        # 分析常见模式
        all_tips = []
        for d in all_data:
            all_tips.extend(d["tips"])

        # 关键词分析
        keywords = {}
        for tip in all_tips:
            words = tip.lower().split()
            for word in words:
                if len(word) > 3:
                    keywords[word] = keywords.get(word, 0) + 1

        top_keywords = sorted(keywords.items(), key=lambda x: -x[1])[:20]

        return {
            "success": True,
            "total_skills_analyzed": len(all_data),
            "total_tips": len(all_tips),
            "skills_with_most_tips": sorted(all_data, key=lambda x: -x["tips_count"])[:5],
            "top_keywords": top_keywords,
            "average_tips_per_skill": len(all_tips) / max(1, len(all_data))
        }
