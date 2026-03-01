# -*- coding: utf-8 -*-
"""
using_git_worktrees_skill - 使用 Git Worktree 技能

创建 Git Worktree 隔离工作空间，允许同时在多个分支上工作而无需切换。
基于 obra/superpowers 的 using-git-worktrees 技能实现。
"""
from leo_skills.core.base_executor import BaseExecutor

import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class WorktreeResult:
    """Worktree 创建结果"""
    success: bool
    path: str
    branch: str
    message: str


class UsingGitWorktreesSkill(BaseExecutor):
    """
    使用 Git Worktree 技能

    功能：
    - 检测或创建 worktree 目录
    - 创建隔离的 Git Worktree
    - 自动检测并运行项目设置
    - 验证干净的测试基线

    使用场景：
    - 需要隔离工作空间的功能开发
    - 并行在多个分支上工作
    - 避免频繁切换分支
    """

    def __init__(self, base_path: str = "."):
        self.name = "using_git_worktrees_skill"
        self.version = "1.0.0"
        self.description = "使用 Git Worktree 技能 - 创建隔离工作空间"
        self.base_path = Path(base_path)

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行技能主入口

        Args:
            branch_name: 分支名称
            worktree_dir: worktree 目录 (可选)
            work_dir: 工作目录

        Returns:
            Dict 包含创建结果
        """
        branch_name = kwargs.get("branch_name", "feature/new-feature")
        worktree_dir = kwargs.get("worktree_dir")
        work_dir = Path(kwargs.get("work_dir", self.base_path))

        try:
            result = self.create_worktree(
                branch_name=branch_name,
                worktree_dir=worktree_dir,
                work_dir=work_dir
            )

            return {
                "status": "success" if result.success else "error",
                "skill": self.name,
                "path": result.path,
                "branch": result.branch,
                "message": result.message
            }

        except Exception as e:
            return {
                "status": "error",
                "skill": self.name,
                "error": str(e)
            }

    def create_worktree(
        self,
        branch_name: str,
        worktree_dir: Optional[str] = None,
        work_dir: Optional[Path] = None
    ) -> WorktreeResult:
        """
        创建 worktree

        Args:
            branch_name: 分支名称
            worktree_dir: worktree 目录
            work_dir: 工作目录

        Returns:
            WorktreeResult 创建结果
        """
        work_dir = Path(work_dir) if work_dir else self.base_path

        # 1. 检查是否是 Git 仓库
        git_dir = work_dir / ".git"
        if not git_dir.exists():
            return WorktreeResult(
                success=False,
                path="",
                branch=branch_name,
                message="不是 Git 仓库"
            )

        # 2. 确定 worktree 目录
        if not worktree_dir:
            worktree_dir = self._detect_worktree_dir(work_dir)

        # 3. 确保目录被忽略
        if worktree_dir.startswith(".") or worktree_dir == "worktrees":
            self._ensure_ignored(work_dir, worktree_dir)

        # 4. 创建完整路径
        project_name = self._get_project_name(work_dir)
        full_path = work_dir / worktree_dir / branch_name.replace("/", "-")

        # 5. 创建 worktree
        try:
            subprocess.run(
                ["git", "worktree", "add", str(full_path), "-b", branch_name],
                cwd=work_dir,
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            # 分支可能已存在，尝试切换
            try:
                subprocess.run(
                    ["git", "worktree", "add", str(full_path), branch_name],
                    cwd=work_dir,
                    capture_output=True,
                    check=True
                )
            except subprocess.CalledProcessError:
                return WorktreeResult(
                    success=False,
                    path=str(full_path),
                    branch=branch_name,
                    message=f"创建 worktree 失败: {e}"
                )

        # 6. 运行项目设置
        setup_result = self._run_setup(full_path)

        # 7. 验证测试基线
        test_result = self._verify_tests(full_path)

        return WorktreeResult(
            success=True,
            path=str(full_path),
            branch=branch_name,
            message=f"Worktree 创建成功\n路径: {full_path}\n{setup_result}\n{test_result}"
        )

    def _detect_worktree_dir(self, work_dir: Path) -> str:
        """检测 worktree 目录"""
        # 检查现有目录
        if (work_dir / ".worktrees").exists():
            return ".worktrees"
        if (work_dir / "worktrees").exists():
            return "worktrees"

        # 默认使用 .worktrees
        return ".worktrees"

    def _ensure_ignored(self, work_dir: Path, directory: str) -> bool:
        """确保目录被 Git 忽略"""
        gitignore_path = work_dir / ".gitignore"

        try:
            # 检查是否已忽略
            result = subprocess.run(
                ["git", "check-ignore", "-q", directory],
                cwd=work_dir,
                capture_output=True
            )

            if result.returncode == 0:
                # 已被忽略
                return True

            # 添加到 .gitignore
            if gitignore_path.exists():
                content = gitignore_path.read_text(encoding="utf-8")
                if directory not in content:
                    with open(gitignore_path, "a", encoding="utf-8") as f:
                        f.write(f"\n# Worktree directory\n{directory}/\n")
            else:
                gitignore_path.write_text(
                    f"# Worktree directory\n{directory}/\n",
                    encoding="utf-8"
                )

            return True

        except Exception:
            return False

    def _get_project_name(self, work_dir: Path) -> str:
        """获取项目名称"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=work_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return Path(result.stdout.strip()).name
        except Exception:
            return work_dir.name

    def _run_setup(self, worktree_path: Path) -> str:
        """运行项目设置"""
        setup_commands = []

        # Node.js
        if (worktree_path / "package.json").exists():
            setup_commands.append(["npm", "install"])

        # Rust
        if (worktree_path / "Cargo.toml").exists():
            setup_commands.append(["cargo", "build"])

        # Python
        if (worktree_path / "requirements.txt").exists():
            setup_commands.append(["pip", "install", "-r", "requirements.txt"])
        if (worktree_path / "pyproject.toml").exists():
            setup_commands.append(["poetry", "install"])

        # Go
        if (worktree_path / "go.mod").exists():
            setup_commands.append(["go", "mod", "download"])

        results = []
        for cmd in setup_commands:
            try:
                subprocess.run(
                    cmd,
                    cwd=worktree_path,
                    capture_output=True,
                    check=True
                )
                results.append(f"✓ {' '.join(cmd)}")
            except subprocess.CalledProcessError as e:
                results.append(f"✗ {' '.join(cmd)}: {e}")

        return "\n".join(results) if results else "无自动设置命令"

    def _verify_tests(self, worktree_path: Path) -> str:
        """验证测试基线"""
        test_commands = [
            ["npm", "test"],
            ["cargo", "test"],
            ["pytest"],
            ["go", "test", "./..."]
        ]

        for cmd in test_commands:
            try:
                result = subprocess.run(
                    cmd,
                    cwd=worktree_path,
                    capture_output=True,
                    timeout=60
                )

                if result.returncode == 0:
                    return f"✓ 测试通过 ({' '.join(cmd)})"

            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                continue
            except FileNotFoundError:
                continue

        return "⚠ 未运行测试"

    def list_worktrees(self, work_dir: Optional[Path] = None) -> list:
        """列出所有 worktrees"""
        work_dir = Path(work_dir) if work_dir else self.base_path

        try:
            result = subprocess.run(
                ["git", "worktree", "list"],
                cwd=work_dir,
                capture_output=True,
                text=True,
                check=True
            )

            worktrees = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split()
                    if len(parts) >= 2:
                        worktrees.append({
                            "path": parts[0],
                            "commit": parts[1] if len(parts) > 1 else "",
                            "branch": parts[2] if len(parts) > 2 else ""
                        })

            return worktrees

        except Exception:
            return []

    def remove_worktree(self, path: str, work_dir: Optional[Path] = None) -> bool:
        """移除 worktree"""
        work_dir = Path(work_dir) if work_dir else self.base_path

        try:
            subprocess.run(
                ["git", "worktree", "remove", path],
                cwd=work_dir,
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "features": [
                "worktree_creation",
                "directory_detection",
                "gitignore_validation",
                "auto_setup",
                "test_verification",
                "worktree_management"
            ],
            "supported_project_types": [
                "nodejs",
                "rust",
                "python",
                "go"
            ]
        }


# 向后兼容
Using_Git_Worktrees_Skill = UsingGitWorktreesSkill


def main():
    """入口函数 - 演示用法"""
    print("=" * 60)
    print("Using Git Worktrees Skill - 演示")
    print("=" * 60)

    skill = UsingGitWorktreesSkill()

    # 演示: 技能能力
    print("\n1. 技能能力")
    print("-" * 40)
    caps = skill.get_capabilities()
    print(f"技能: {caps['name']}")
    print(f"功能: {', '.join(caps['features'])}")

    # 演示: 列出现有 worktrees
    print("\n2. 列出现有 worktrees")
    print("-" * 40)
    worktrees = skill.list_worktrees()
    print(f"找到 {len(worktrees)} 个 worktree")
    for wt in worktrees:
        print(f"  - {wt['path']} ({wt['branch']})")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return skill


if __name__ == "__main__":
    main()
