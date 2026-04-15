# -*- coding: utf-8 -*-
"""
Harness Audit Skill - Agent性能审计工具
=======================================

参考 everything-claude-code 的 /harness-audit 设计
提供Leo AI系统的全面健康检查和性能诊断

Author: Leo AI System
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from base import BaseSkill, SkillResult


@dataclass
class AuditCheck:
    """审计检查项"""
    name: str
    status: str  # pass, warn, fail, skip
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    fix_suggestion: Optional[str] = None


class HarnessAuditSkill(BaseSkill):
    """
    Harness Audit Skill

    提供系统级别的健康检查和性能诊断
    """

    @property
    def name(self) -> str:
        return "harness_audit"

    @property
    def description(self) -> str:
        return "Agent Harness性能审计工具 - 系统健康检查和诊断"

    def execute(self, action: str = "default", **kwargs) -> SkillResult:
        """
        执行审计

        Actions:
            default: 完整审计
            quick: 快速检查
            fix: 自动修复
        """
        if action == "fix":
            return self._fix_issues()
        elif action == "quick":
            return self._quick_check()
        else:
            return self._full_audit()

    def _full_audit(self) -> SkillResult:
        """完整审计"""
        start_time = time.time()
        checks = []

        # 1. 系统配置检查
        checks.append(self._check_system_config())

        # 2. Skills注册检查
        checks.append(self._check_skills_registration())

        # 3. 记忆系统检查
        checks.append(self._check_memory_system())

        # 4. Hooks状态检查
        checks.append(self._check_hooks_status())

        # 5. 项目结构检查
        checks.append(self._check_project_structure())

        # 6. 性能指标检查
        checks.append(self._check_performance_metrics())

        duration = (time.time() - start_time) * 1000

        # 汇总结果
        passed = sum(1 for c in checks if c.status == "pass")
        warnings = sum(1 for c in checks if c.status == "warn")
        failed = sum(1 for c in checks if c.status == "fail")

        result_data = {
            "summary": {
                "total_checks": len(checks),
                "passed": passed,
                "warnings": warnings,
                "failed": failed,
                "score": self._calculate_score(passed, warnings, failed),
                "duration_ms": round(duration, 2)
            },
            "checks": [c.__dict__ for c in checks],
            "timestamp": datetime.now().isoformat()
        }

        return SkillResult.ok(
            data=result_data,
            message=f"审计完成 | 通过: {passed}, 警告: {warnings}, 失败: {failed}"
        )

    def _quick_check(self) -> SkillResult:
        """快速检查"""
        checks = [
            self._check_system_config(),
            self._check_hooks_status()
        ]

        passed = sum(1 for c in checks if c.status == "pass")
        return SkillResult.ok(
            data={"quick_checks": [c.__dict__ for c in checks], "passed": passed},
            message=f"快速检查完成 | 通过: {passed}/{len(checks)}"
        )

    def _fix_issues(self) -> SkillResult:
        """自动修复问题"""
        fixes_applied = []

        # 修复1: 确保必要目录存在
        required_dirs = [
            "leo_knowledge/memory/auto_storage",
            ".claude/hooks/logs",
            "data/vector_memory"
        ]

        for dir_path in required_dirs:
            p = Path(dir_path)
            if not p.exists():
                p.mkdir(parents=True, exist_ok=True)
                fixes_applied.append(f"创建目录: {dir_path}")

        # 修复2: 初始化记忆索引
        index_file = Path("leo_knowledge/memory/auto_storage/memory_index.json")
        if not index_file.exists():
            index_file.parent.mkdir(parents=True, exist_ok=True)
            with open(index_file, "w", encoding="utf-8") as f:
                json.dump({"sessions": [], "stats": {}}, f, ensure_ascii=False, indent=2)
            fixes_applied.append("初始化记忆索引")

        return SkillResult.ok(
            data={"fixes_applied": fixes_applied},
            message=f"已应用 {len(fixes_applied)} 项修复"
        )

    def _check_system_config(self) -> AuditCheck:
        """检查系统配置"""
        project_root = Path(".")

        # 检查关键配置文件
        config_files = {
            "CLAUDE.md": project_root / "CLAUDE.md",
            "pyproject.toml": project_root / "pyproject.toml",
            "mcp.json": project_root / "mcp.json",
            "settings.local.json": project_root / ".claude" / "settings.local.json"
        }

        missing = []
        for name, path in config_files.items():
            if not path.exists():
                missing.append(name)

        if missing:
            return AuditCheck(
                name="system_config",
                status="warn",
                message=f"缺少配置文件: {', '.join(missing)}",
                fix_suggestion="运行 /harness-audit --fix 自动创建必要配置"
            )

        return AuditCheck(
            name="system_config",
            status="pass",
            message="所有关键配置文件存在",
            details={"config_files": list(config_files.keys())}
        )

    def _check_skills_registration(self) -> AuditCheck:
        """检查Skills注册"""
        skills_dir = Path("src/leo_skills")

        if not skills_dir.exists():
            return AuditCheck(
                name="skills_registration",
                status="fail",
                message="Skills目录不存在"
            )

        # 统计Skills
        skill_count = 0
        skill_categories = {}

        for category_dir in skills_dir.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith("_"):
                skills_in_category = list(category_dir.iterdir())
                skill_count += len([s for s in skills_in_category if s.is_dir() and (s / "SKILL.md").exists()])
                skill_categories[category_dir.name] = len(skills_in_category)

        if skill_count == 0:
            return AuditCheck(
                name="skills_registration",
                status="warn",
                message="未发现注册的Skills"
            )

        return AuditCheck(
            name="skills_registration",
            status="pass",
            message=f"发现 {skill_count} 个注册Skills",
            details={"total": skill_count, "categories": skill_categories}
        )

    def _check_memory_system(self) -> AuditCheck:
        """检查记忆系统"""
        memory_dirs = [
            Path("leo_knowledge/memory"),
            Path("src/leo_memory")
        ]

        all_exist = all(d.exists() for d in memory_dirs)

        if not all_exist:
            missing = [str(d) for d in memory_dirs if not d.exists()]
            return AuditCheck(
                name="memory_system",
                status="warn",
                message=f"记忆系统目录不完整: {', '.join(missing)}",
                fix_suggestion="运行 /harness-audit --fix 初始化记忆目录"
            )

        # 检查向量记忆
        vector_db = Path("data/vector_memory/vectors.json")
        memory_entries = 0
        if vector_db.exists():
            try:
                with open(vector_db, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    memory_entries = len(data) if isinstance(data, list) else 0
            except:
                pass

        return AuditCheck(
            name="memory_system",
            status="pass",
            message=f"记忆系统正常 | 当前条目: {memory_entries}",
            details={"vector_entries": memory_entries}
        )

    def _check_hooks_status(self) -> AuditCheck:
        """检查Hooks状态"""
        hooks_dir = Path(".claude/hooks")

        if not hooks_dir.exists():
            return AuditCheck(
                name="hooks_status",
                status="fail",
                message="Hooks目录不存在"
            )

        # 检查Hook脚本
        hook_files = ["session_start.sh", "session_end.sh", "post_tool.sh", "stop.sh", "user_prompt.sh"]
        existing_hooks = [f for f in hook_files if (hooks_dir / f).exists()]

        if not existing_hooks:
            return AuditCheck(
                name="hooks_status",
                status="warn",
                message="未发现Hook脚本"
            )

        return AuditCheck(
            name="hooks_status",
            status="pass",
            message=f"发现 {len(existing_hooks)}/{len(hook_files)} 个Hook脚本",
            details={"hooks": existing_hooks}
        )

    def _check_project_structure(self) -> AuditCheck:
        """检查项目结构"""
        required_dirs = ["src", "tests", "docs", "scripts", "leo_knowledge"]
        missing = []

        for dir_name in required_dirs:
            if not Path(dir_name).exists():
                missing.append(dir_name)

        if missing:
            return AuditCheck(
                name="project_structure",
                status="warn",
                message=f"缺少目录: {', '.join(missing)}"
            )

        return AuditCheck(
            name="project_structure",
            status="pass",
            message="项目结构完整"
        )

    def _check_performance_metrics(self) -> AuditCheck:
        """检查性能指标"""
        # 统计代码行数
        total_lines = 0
        file_count = 0

        for ext in ["*.py", "*.sh"]:
            for f in Path("src").rglob(ext):
                try:
                    with open(f, "r", encoding="utf-8") as fp:
                        total_lines += len(fp.readlines())
                        file_count += 1
                except:
                    pass

        return AuditCheck(
            name="performance_metrics",
            status="pass",
            message=f"代码规模: {total_lines} 行 / {file_count} 文件",
            details={"total_lines": total_lines, "file_count": file_count}
        )

    def _calculate_score(self, passed: int, warnings: int, failed: int) -> int:
        """计算健康分数"""
        total = passed + warnings + failed
        if total == 0:
            return 100

        score = (passed / total) * 100
        if failed > 0:
            score -= (failed * 10)
        if warnings > 2:
            score -= (warnings - 2) * 2

        return max(0, min(100, int(score)))

    def get_actions(self) -> List[str]:
        return ["default", "quick", "fix"]


# 快捷函数
def run_audit() -> Dict[str, Any]:
    """运行审计"""
    skill = HarnessAuditSkill()
    result = skill.execute()
    return result.to_dict()


if __name__ == "__main__":
    result = run_audit()
    print(json.dumps(result, ensure_ascii=False, indent=2))