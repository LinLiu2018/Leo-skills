# -*- coding: utf-8 -*-
"""
进化执行器
==========
将经验转化为实际的技能优化

实现真正的闭环进化：经验 → 分析 → 修改 → 验证
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from .evolution_skill import EvolutionSkill


class EvolutionExecutor:
    """
    进化执行器

    功能：
    1. 分析技能经验
    2. 生成优化建议
    3. 自动修改 SKILL.md
    4. 记录进化历史
    """

    def __init__(self):
        self.evolution_skill = EvolutionSkill()
        # 延迟导入 LLMAdapter
        try:
            from leo_subagents.core.llm_adapter import LLMAdapter
            self.llm = LLMAdapter()
        except ImportError:
            self.llm = None

    def analyze_and_evolve(self, skill_name: str) -> Dict[str, Any]:
        """
        分析并进化指定技能

        Args:
            skill_name: 技能名称

        Returns:
            进化结果
        """
        print(f"[Evolution] 开始分析技能: {skill_name}")

        # 1. 获取经验
        tips_result = self.evolution_skill.execute(action="get_tips")
        tips = tips_result.data.get("tips", []) if hasattr(tips_result, 'data') else []

        if len(tips) < 5:
            return {"status": "skipped", "reason": "经验不足（需要至少5条）", "tips_count": len(tips)}

        # 2. 读取当前 SKILL.md
        skill_path = Path(f"src/leo_skills/{skill_name}/SKILL.md")
        if not skill_path.exists():
            return {"status": "error", "error": f"SKILL.md 不存在: {skill_path}"}

        current_content = skill_path.read_text(encoding="utf-8")

        # 3. 分析并生成优化建议
        suggestions = self._generate_suggestions(skill_name, tips, current_content)

        # 4. 应用优化
        evolution_result = self._apply_evolution(skill_path, current_content, suggestions)

        # 5. 记录进化历史
        self._log_evolution(skill_name, suggestions, evolution_result)

        return {
            "status": "completed",
            "skill": skill_name,
            "suggestions": suggestions,
            "evolution_result": evolution_result,
            "tips_used": len(tips)
        }

    def _generate_suggestions(self, skill_name: str, tips: List[str], current_content: str) -> List[Dict]:
        """生成优化建议"""
        suggestions = []

        # 基于经验类型分类
        success_tips = [t for t in tips if "成功" in t or "有效" in t]
        failure_tips = [t for t in tips if "失败" in t or "错误" in t]
        improvement_tips = [t for t in tips if "优化" in t or "改进" in t]

        # 生成建议
        if success_tips:
            suggestions.append({
                "type": "enhance",
                "target": "description",
                "content": f"添加最佳实践: {success_tips[0][:50]}..."
            })

        if failure_tips:
            suggestions.append({
                "type": "fix",
                "target": " pitfalls",
                "content": f"添加注意事项: {failure_tips[0][:50]}..."
            })

        if improvement_tips:
            suggestions.append({
                "type": "improve",
                "target": "usage",
                "content": f"优化使用说明: {improvement_tips[0][:50]}..."
            })

        return suggestions

    def _apply_evolution(self, skill_path: Path, current_content: str, suggestions: List[Dict]) -> Dict:
        """应用进化"""
        try:
            # 创建备份
            backup_path = skill_path.with_suffix(f".md.backup_{datetime.now().strftime('%Y%m%d')}")
            backup_path.write_text(current_content, encoding="utf-8")

            # 构建增强内容
            enhanced_content = self._enhance_skill_md(current_content, suggestions)

            # 写回文件
            skill_path.write_text(enhanced_content, encoding="utf-8")

            return {"status": "success", "backup": str(backup_path)}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _enhance_skill_md(self, content: str, suggestions: List[Dict]) -> str:
        """增强 SKILL.md 内容"""
        enhanced = content

        # 在文件末尾添加进化记录
        evolution_section = f"""

---

## 进化记录 (Auto-generated)

> 更新时间: {datetime.now().isoformat()}

### 本次优化
"""
        for i, suggestion in enumerate(suggestions, 1):
            evolution_section += f"{i}. **{suggestion['type']}**: {suggestion['content']}\n"

        if "## 进化记录" not in enhanced:
            enhanced += evolution_section

        return enhanced

    def _log_evolution(self, skill_name: str, suggestions: List[Dict], result: Dict):
        """记录进化历史"""
        log_path = Path("logs/evolution_history.json")
        log_path.parent.mkdir(exist_ok=True)

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "skill": skill_name,
            "suggestions_count": len(suggestions),
            "result": result.get("status"),
        }

        try:
            if log_path.exists():
                with open(log_path, "r", encoding="utf-8") as f:
                    history = json.load(f)
            else:
                history = []

            history.append(log_entry)

            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"[WARNING] 记录进化历史失败: {e}")

    def auto_evolve_all(self) -> List[Dict]:
        """自动进化所有符合条件的技能"""
        results = []

        # 扫描所有技能
        skills_dir = Path("src/leo_skills")
        for skill_dir in skills_dir.rglob("*_skill"):
            skill_name = skill_dir.name

            # 检查是否有足够的经验
            stage_result = self.evolution_skill.execute(action="get_stage")
            stage = stage_result.data.get("stage", "INITIAL") if hasattr(stage_result, 'data') else "INITIAL"
            tips_count = stage_result.data.get("tips_count", 0) if hasattr(stage_result, 'data') else 0

            if stage in ["OPTIMIZING", "MATURE"] and tips_count >= 10:
                result = self.analyze_and_evolve(skill_name)
                results.append(result)

        return results


# 便捷函数
def evolve_skill(skill_name: str) -> Dict:
    """进化指定技能"""
    executor = EvolutionExecutor()
    return executor.analyze_and_evolve(skill_name)


def auto_evolve() -> List[Dict]:
    """自动进化所有技能"""
    executor = EvolutionExecutor()
    return executor.auto_evolve_all()
