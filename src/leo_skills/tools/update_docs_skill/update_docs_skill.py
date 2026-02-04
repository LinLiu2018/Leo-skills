# -*- coding: utf-8 -*-
"""
update_docs_skill - 更新文档技能

在提交后更新文档，同步README、AGENTS.md、CHANGELOG等。
基于 obra/superpowers 的 update-docs 技能实现。
"""

import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field


@dataclass
class DocChange:
    """文档变更"""
    file: str
    change_type: str  # added, modified, removed
    description: str = ""


@dataclass
class DocUpdateResult:
    """文档更新结果"""
    success: bool
    changes_made: List[DocChange]
    files_modified: List[str]
    files_created: List[str]
    changelog_updated: bool = False
    summary: str = ""


class UpdateDocsSkill:
    """
    更新文档技能

    功能：
    - 检测代码变更
    - 更新README、CHANGELOG等文档
    - 路由文档到正确位置
    - 支持工作树和提交范围分析

    使用场景：
    - 提交后自动更新文档
    - 分析工作树变更
    - 文档结构迁移
    """

    def __init__(self, base_path: str = "."):
        self.name = "update_docs_skill"
        self.version = "1.0.0"
        self.description = "更新文档技能 - 同步文档与代码变更"
        self.base_path = Path(base_path)

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行技能主入口

        Args:
            mode: 模式 (commit/working-tree/audit)
            commit_range: 提交范围 (如 HEAD~3..HEAD)
            work_dir: 工作目录

        Returns:
            Dict 包含更新结果
        """
        mode = kwargs.get("mode", "commit")
        commit_range = kwargs.get("commit_range", "HEAD")
        work_dir = kwargs.get("work_dir", self.base_path)

        try:
            if mode == "working-tree":
                result = self.analyze_working_tree(work_dir)
            elif mode == "audit":
                result = self.audit_documentation(work_dir)
            else:
                result = self.update_from_commits(commit_range, work_dir)

            return {
                "status": "success" if result.success else "warning",
                "skill": self.name,
                "mode": mode,
                "changes": len(result.changes_made),
                "files_modified": result.files_modified,
                "files_created": result.files_created,
                "changelog_updated": result.changelog_updated,
                "summary": result.summary
            }

        except Exception as e:
            return {
                "status": "error",
                "skill": self.name,
                "error": str(e)
            }

    def update_from_commits(
        self,
        commit_range: str = "HEAD",
        work_dir: Optional[Path] = None
    ) -> DocUpdateResult:
        """
        从提交更新文档

        Args:
            commit_range: 提交范围
            work_dir: 工作目录

        Returns:
            DocUpdateResult 更新结果
        """
        work_dir = Path(work_dir) if work_dir else self.base_path

        # 1. 获取变更文件
        changed_files = self._get_changed_files(commit_range, work_dir)

        # 2. 分类变更
        changes = self._categorize_changes(changed_files)

        # 3. 更新CHANGELOG
        changelog_updated = False
        if self._should_update_changelog(changes):
            changelog_updated = self._update_changelog(changes, work_dir)

        # 4. 检查README健康度
        readme_issues = self._check_readme_health(work_dir)

        # 5. 生成总结
        summary = self._generate_update_summary(changes, changelog_updated, readme_issues)

        return DocUpdateResult(
            success=True,
            changes_made=changes,
            files_modified=[c.file for c in changes if c.change_type == "modified"],
            files_created=[c.file for c in changes if c.change_type == "added"],
            changelog_updated=changelog_updated,
            summary=summary
        )

    def analyze_working_tree(self, work_dir: Optional[Path] = None) -> DocUpdateResult:
        """
        分析工作树变更

        Args:
            work_dir: 工作目录

        Returns:
            DocUpdateResult 分析结果
        """
        work_dir = Path(work_dir) if work_dir else self.base_path

        # 1. 获取工作树状态
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=work_dir,
                capture_output=True,
                text=True
            )

            changes = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    status = line[:2]
                    file = line[3:].strip()

                    if status.startswith("M"):
                        changes.append(DocChange(file, "modified"))
                    elif status.startswith("A") or status.startswith("?"):
                        changes.append(DocChange(file, "added"))
                    elif status.startswith("D"):
                        changes.append(DocChange(file, "removed"))

            return DocUpdateResult(
                success=True,
                changes_made=changes,
                files_modified=[c.file for c in changes if c.change_type == "modified"],
                files_created=[c.file for c in changes if c.change_type == "added"],
                summary=f"工作树中有 {len(changes)} 个变更"
            )

        except Exception as e:
            return DocUpdateResult(
                success=False,
                changes_made=[],
                files_modified=[],
                files_created=[],
                summary=f"分析工作树失败: {e}"
            )

    def audit_documentation(self, work_dir: Optional[Path] = None) -> DocUpdateResult:
        """
        审计文档健康度

        Args:
            work_dir: 工作目录

        Returns:
            DocUpdateResult 审计结果
        """
        work_dir = Path(work_dir) if work_dir else self.base_path
        readme_path = work_dir / "README.md"

        if not readme_path.exists():
            return DocUpdateResult(
                success=False,
                changes_made=[],
                files_modified=[],
                files_created=[],
                summary="README.md 不存在"
            )

        try:
            content = readme_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            issues = []

            # 检查行数
            if len(lines) > 500:
                issues.append(f"README 过长 ({len(lines)} 行)，建议迁移到 docs/")

            # 检查章节
            sections_to_migrate = []

            if "## Commands Reference" in content or "## 命令参考" in content:
                sections_to_migrate.append("Commands Reference → docs/commands.md")

            if "## API Reference" in content or "## API参考" in content:
                sections_to_migrate.append("API Reference → docs/api.md")

            if "## Configuration" in content or "## 配置" in content:
                sections_to_migrate.append("Configuration → docs/configuration.md")

            if "## File Structure" in content or "## 文件结构" in content:
                sections_to_migrate.append("File Structure → docs/file-structure.md")

            # 检查代码块数量
            code_blocks = len(re.findall(r"```", content)) // 2
            if code_blocks > 10:
                issues.append(f"代码块过多 ({code_blocks} 个)，建议移到 docs/examples.md")

            # 生成报告
            summary_lines = [
                f"README.md 审计报告",
                f"行数: {len(lines)}",
                f"代码块: {code_blocks}",
            ]

            if sections_to_migrate:
                summary_lines.append("\n建议迁移的章节:")
                for section in sections_to_migrate:
                    summary_lines.append(f"  - {section}")

            if issues:
                summary_lines.append("\n发现的问题:")
                for issue in issues:
                    summary_lines.append(f"  ⚠️ {issue}")

            return DocUpdateResult(
                success=True,
                changes_made=[],
                files_modified=[],
                files_created=[],
                summary="\n".join(summary_lines)
            )

        except Exception as e:
            return DocUpdateResult(
                success=False,
                changes_made=[],
                files_modified=[],
                files_created=[],
                summary=f"审计失败: {e}"
            )

    def _get_changed_files(self, commit_range: str, work_dir: Path) -> List[str]:
        """获取变更的文件列表"""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", commit_range],
                cwd=work_dir,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]

        except Exception:
            pass

        return []

    def _categorize_changes(self, files: List[str]) -> List[DocChange]:
        """分类变更"""
        changes = []

        for file in files:
            if file.endswith(".py") or file.endswith(".js") or file.endswith(".ts"):
                changes.append(DocChange(file, "modified", "代码文件变更"))
            elif file.startswith("docs/"):
                changes.append(DocChange(file, "modified", "文档变更"))
            elif file.endswith(".md"):
                changes.append(DocChange(file, "modified", "Markdown文档"))
            elif file.endswith(".json") or file.endswith(".yaml") or file.endswith(".yml"):
                changes.append(DocChange(file, "modified", "配置文件"))
            else:
                changes.append(DocChange(file, "modified", "其他文件"))

        return changes

    def _should_update_changelog(self, changes: List[DocChange]) -> bool:
        """判断是否应该更新CHANGELOG"""
        # 如果有代码文件变更，则更新
        return any(
            c.file.endswith((".py", ".js", ".ts"))
            for c in changes
        )

    def _update_changelog(self, changes: List[DocChange], work_dir: Path) -> bool:
        """更新CHANGELOG"""
        changelog_path = work_dir / "CHANGELOG.md"

        try:
            # 构建变更条目
            entries = []
            for change in changes:
                if change.file.endswith((".py", ".js", ".ts")):
                    entries.append(f"- 更新 {change.file}")

            if not entries:
                return False

            entry_text = "\n".join(entries)

            if changelog_path.exists():
                content = changelog_path.read_text(encoding="utf-8")

                # 查找 ## [Unreleased] 部分
                if "## [Unreleased]" in content:
                    # 在 Unreleased 部分添加条目
                    pattern = r"(## \[Unreleased\].*?)(\n## |\Z)"
                    match = re.search(pattern, content, re.DOTALL)

                    if match:
                        unreleased = match.group(1)
                        new_unreleased = unreleased + "\n### Changed\n" + entry_text + "\n"
                        content = content.replace(unreleased, new_unreleased)
                        changelog_path.write_text(content, encoding="utf-8")
                        return True
                else:
                    # 添加 Unreleased 部分
                    new_section = f"## [Unreleased]\n\n### Changed\n{entry_text}\n\n"
                    content = new_section + content
                    changelog_path.write_text(content, encoding="utf-8")
                    return True

            return False

        except Exception:
            return False

    def _check_readme_health(self, work_dir: Path) -> List[str]:
        """检查README健康度"""
        readme_path = work_dir / "README.md"

        if not readme_path.exists():
            return ["README.md 不存在"]

        try:
            content = readme_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            issues = []

            if len(lines) > 500:
                issues.append("README 过长")

            if content.count("```") // 2 > 10:
                issues.append("代码块过多")

            return issues

        except Exception:
            return ["无法读取 README.md"]

    def _generate_update_summary(
        self,
        changes: List[DocChange],
        changelog_updated: bool,
        readme_issues: List[str]
    ) -> str:
        """生成更新总结"""
        lines = [
            f"文档更新完成",
            f"变更文件: {len(changes)} 个",
            f"CHANGELOG 更新: {'是' if changelog_updated else '否'}"
        ]

        if readme_issues:
            lines.append(f"\nREADME 问题: {len(readme_issues)} 个")
            for issue in readme_issues:
                lines.append(f"  - {issue}")

        return "\n".join(lines)

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "modes": [
                "commit",
                "working-tree",
                "audit"
            ],
            "features": [
                "change_detection",
                "categorization",
                "changelog_update",
                "readme_health_check",
                "migration_suggestions",
                "report_generation"
            ]
        }


# 向后兼容
Update_Docs_Skill = UpdateDocsSkill


def main():
    """入口函数 - 演示用法"""
    print("=" * 60)
    print("Update Docs Skill - 演示")
    print("=" * 60)

    skill = UpdateDocsSkill()

    # 演示: 审计文档
    print("\n1. 审计文档健康度")
    print("-" * 40)
    result = skill.audit_documentation()
    print(result.summary)

    # 演示: 分析工作树
    print("\n2. 分析工作树")
    print("-" * 40)
    result = skill.analyze_working_tree()
    print(f"变更数: {len(result.changes_made)}")

    # 演示: 技能能力
    print("\n3. 技能能力")
    print("-" * 40)
    caps = skill.get_capabilities()
    print(f"技能: {caps['name']}")
    print(f"模式: {', '.join(caps['modes'])}")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return skill


if __name__ == "__main__":
    main()
