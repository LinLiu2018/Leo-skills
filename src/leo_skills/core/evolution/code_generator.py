# -*- coding: utf-8 -*-
"""
代码自动生成系统

基于分析结果自动修改代码
"""

import ast
import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .analyzer import LLMAnalyzer


@dataclass
class CodeChange:
    """代码变更"""
    change_id: str
    change_type: str  # add, modify, delete
    target: str  # 文件路径或函数名
    original_code: str = ""
    new_code: str = ""
    description: str = ""
    line_start: int = 0
    line_end: int = 0


@dataclass
class PatchResult:
    """补丁应用结果"""
    success: bool
    applied_changes: List[CodeChange] = field(default_factory=list)
    failed_changes: List[CodeChange] = field(default_factory=list)
    backup_path: str = ""
    error: str = ""


class CodeGenerator:
    """
    代码生成器

    功能：
    - AST 解析与修改
    - 安全代码替换
    - 增量更新
    - 代码验证
    """

    def __init__(self):
        self.llm_analyzer = LLMAnalyzer()
        self.changes_history: List[Dict] = []

    def parse_skill(self, skill_path: str) -> ast.AST:
        """
        解析技能代码为 AST

        Args:
            skill_path: 技能路径

        Returns:
            AST 对象
        """
        file_path = self._find_skill_file(skill_path)
        if not file_path:
            raise FileNotFoundError(f"Skill file not found: {skill_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()

        return ast.parse(source, filename=str(file_path))

    def generate_patch(
        self,
        skill_path: str,
        improvements: List[str],
        use_llm: bool = True
    ) -> List[CodeChange]:
        """
        生成代码补丁

        Args:
            skill_path: 技能路径
            improvements: 改进点列表
            use_llm: 是否使用 LLM

        Returns:
            代码变更列表
        """
        file_path = self._find_skill_file(skill_path)
        if not file_path:
            raise FileNotFoundError(f"Skill file not found: {skill_path}")

        # 读取原始代码
        with open(file_path, 'r', encoding='utf-8') as f:
            original_code = f.read()

        changes = []

        if use_llm and self.llm_analyzer.llm:
            # 使用 LLM 生成改进
            try:
                result = self.llm_analyzer.generate_code_improvement(
                    original_code,
                    improvements
                )

                # 解析 LLM 响应
                if result.get("status") == "success":
                    # 从 LLM 响应中提取变更
                    changes = self._parse_llm_changes(
                        original_code,
                        result.get("changes", []),
                        file_path
                    )
            except Exception as e:
                print(f"[CodeGenerator] LLM generation failed: {e}")

        # 如果没有 LLM 变更，使用简单规则
        if not changes:
            changes = self._generate_rule_based_changes(
                original_code,
                improvements,
                file_path
            )

        return changes

    def apply_patch(
        self,
        skill_path: str,
        changes: List[CodeChange],
        create_backup: bool = True
    ) -> PatchResult:
        """
        应用代码补丁

        Args:
            skill_path: 技能路径
            changes: 代码变更列表
            create_backup: 是否创建备份

        Returns:
            应用结果
        """
        file_path = self._find_skill_file(skill_path)
        if not file_path:
            return PatchResult(
                success=False,
                error=f"Skill file not found: {skill_path}"
            )

        # 创建备份
        backup_path = ""
        if create_backup:
            backup_path = self.create_backup(file_path)

        # 读取原始代码
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return PatchResult(
                success=False,
                error=f"Failed to read file: {e}",
                backup_path=backup_path
            )

        applied = []
        failed = []

        # 应用每个变更
        for change in changes:
            try:
                content = self._apply_change(content, change)
                applied.append(change)
            except Exception as e:
                change.error = str(e)
                failed.append(change)

        # 写回文件
        if applied:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            except Exception as e:
                # 回滚
                if backup_path:
                    shutil.copy(backup_path, file_path)
                return PatchResult(
                    success=False,
                    error=f"Failed to write file: {e}",
                    backup_path=backup_path,
                    applied_changes=applied,
                    failed_changes=failed
                )

        # 验证语法
        if applied:
            try:
                ast.parse(content)
            except SyntaxError as e:
                # 回滚
                if backup_path:
                    shutil.copy(backup_path, file_path)
                return PatchResult(
                    success=False,
                    error=f"Syntax error after patch: {e}",
                    backup_path=backup_path,
                    applied_changes=[],
                    failed_changes=applied + failed
                )

        # 记录历史
        self._record_change(skill_path, changes, applied, failed)

        return PatchResult(
            success=len(failed) == 0,
            applied_changes=applied,
            failed_changes=failed,
            backup_path=backup_path
        )

    def validate_syntax(self, code: str) -> bool:
        """
        验证语法正确性

        Args:
            code: 代码字符串

        Returns:
            是否有效
        """
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    def create_backup(self, file_path: Path) -> str:
        """
        创建备份

        Args:
            file_path: 文件路径

        Returns:
            备份文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = file_path.parent / "backups"
        backup_dir.mkdir(exist_ok=True)

        backup_path = backup_dir / f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"

        shutil.copy2(file_path, backup_path)

        return str(backup_path)

    # ========== 辅助方法 ==========

    def _find_skill_file(self, skill_path: str) -> Optional[Path]:
        """查找技能文件"""
        base_path = Path("src/leo_skills")
        skill_dir = base_path / skill_path

        if not skill_dir.exists():
            return None

        # 查找 Python 文件
        for py_file in skill_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            return py_file

        return None

    def _parse_llm_changes(
        self,
        original_code: str,
        improvements: List[str],
        file_path: Path
    ) -> List[CodeChange]:
        """解析 LLM 生成的变更"""
        changes = []

        for i, imp in enumerate(improvements):
            change = CodeChange(
                change_id=f"llm_change_{i}",
                change_type="modify",
                target=str(file_path),
                description=imp,
                new_code=imp  # 简化处理
            )
            changes.append(change)

        return changes

    def _generate_rule_based_changes(
        self,
        original_code: str,
        improvements: List[str],
        file_path: Path
    ) -> List[CodeChange]:
        """基于规则的变更生成"""
        changes = []

        for i, imp in enumerate(improvements):
            # 简单的改进映射
            if "timeout" in imp.lower():
                change = CodeChange(
                    change_id=f"rule_change_{i}",
                    change_type="add",
                    target=str(file_path),
                    description="Add timeout handling",
                    new_code="# Consider adding timeout parameter to API calls\n"
                )
                changes.append(change)

            elif "retry" in imp.lower():
                change = CodeChange(
                    change_id=f"rule_change_{i}",
                    change_type="add",
                    target=str(file_path),
                    description="Add retry logic",
                    new_code="# Consider adding retry logic for failed operations\n"
                )
                changes.append(change)

            elif "error" in imp.lower():
                change = CodeChange(
                    change_id=f"rule_change_{i}",
                    change_type="modify",
                    target=str(file_path),
                    description="Improve error handling",
                    new_code="# Consider adding more specific error handling\n"
                )
                changes.append(change)

        return changes

    def _apply_change(self, content: str, change: CodeChange) -> str:
        """应用单个变更"""
        if change.change_type == "add":
            # 在文件末尾添加
            return content + "\n" + change.new_code

        elif change.change_type == "modify":
            # 简单替换
            if change.original_code and change.original_code in content:
                return content.replace(change.original_code, change.new_code)
            else:
                # 添加到文件开头
                return change.new_code + "\n" + content

        elif change.change_type == "delete":
            if change.original_code and change.original_code in content:
                return content.replace(change.original_code, "")
            return content

        return content

    def _record_change(
        self,
        skill_path: str,
        requested: List[CodeChange],
        applied: List[CodeChange],
        failed: List[CodeChange]
    ):
        """记录变更历史"""
        record = {
            "skill_path": skill_path,
            "timestamp": datetime.now().isoformat(),
            "requested_count": len(requested),
            "applied_count": len(applied),
            "failed_count": len(failed),
            "changes": [
                {
                    "id": c.change_id,
                    "type": c.change_type,
                    "description": c.description,
                    "success": c in applied
                }
                for c in requested
            ]
        }

        self.changes_history.append(record)

    def get_change_history(
        self,
        skill_path: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """获取变更历史"""
        history = self.changes_history

        if skill_path:
            history = [h for h in history if h["skill_path"] == skill_path]

        return history[-limit:]


# 全局实例
_global_code_generator: Optional[CodeGenerator] = None


def get_code_generator() -> CodeGenerator:
    """获取全局代码生成器"""
    global _global_code_generator
    if _global_code_generator is None:
        _global_code_generator = CodeGenerator()
    return _global_code_generator
