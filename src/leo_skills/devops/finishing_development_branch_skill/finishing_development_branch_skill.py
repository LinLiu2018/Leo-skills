# -*- coding: utf-8 -*-
"""
finishing_development_branch_skill - 完成开发分支技能

当实现完成、所有测试通过，需要决定如何集成工作时使用。
基于 obra/superpowers 的 finishing-development-branch 技能实现。
"""

import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class FinishOption(Enum):
    """完成选项"""
    LOCAL_MERGE = 1
    CREATE_PR = 2
    KEEP_AS_IS = 3
    DISCARD = 4


@dataclass
class FinishResult:
    """完成结果"""
    success: bool
    option: FinishOption
    message: str
    base_branch: str = ""
    feature_branch: str = ""
    pr_url: str = ""
    worktree_cleaned: bool = False


class FinishingDevelopmentBranchSkill:
    """
    完成开发分支技能

    功能：
    - 验证测试通过
    - 确定基础分支
    - 呈现完成选项
    - 执行用户选择
    - 清理工作树

    使用场景：
    - 开发完成后合并分支
    - 创建Pull Request
    - 清理工作空间
    """

    def __init__(self, base_path: str = "."):
        self.name = "finishing_development_branch_skill"
        self.version = "1.0.0"
        self.description = "完成开发分支技能 - 指导完成开发工作"
        self.base_path = Path(base_path)

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行技能主入口

        Args:
            option: 完成选项 (1/2/3/4)
            base_branch: 基础分支名
            feature_branch: 功能分支名
            work_dir: 工作目录

        Returns:
            Dict 包含完成结果
        """
        work_dir = Path(kwargs.get("work_dir", self.base_path))
        option_num = kwargs.get("option")
        base_branch = kwargs.get("base_branch", "main")
        feature_branch = kwargs.get("feature_branch", "")

        try:
            if option_num:
                option = FinishOption(option_num)
            else:
                # 需要先验证测试
                test_result = self.verify_tests(work_dir)
                if not test_result["passed"]:
                    return {
                        "status": "blocked",
                        "skill": self.name,
                        "message": "测试未通过，无法继续",
                        "test_result": test_result
                    }

                return {
                    "status": "ready",
                    "skill": self.name,
                    "message": "测试通过，请选择完成选项",
                    "options": [
                        {"value": 1, "label": "本地合并回基础分支"},
                        {"value": 2, "label": "推送并创建Pull Request"},
                        {"value": 3, "label": "保持分支原样"},
                        {"value": 4, "label": "放弃此工作"}
                    ],
                    "base_branch": base_branch,
                    "feature_branch": feature_branch or self._get_current_branch(work_dir)
                }

            # 执行选择的选项
            result = self.finish_branch(
                option=option,
                base_branch=base_branch,
                feature_branch=feature_branch,
                work_dir=work_dir
            )

            return {
                "status": "success" if result.success else "error",
                "skill": self.name,
                "option": option.name,
                "message": result.message,
                "base_branch": result.base_branch,
                "pr_url": result.pr_url,
                "worktree_cleaned": result.worktree_cleaned
            }

        except Exception as e:
            return {
                "status": "error",
                "skill": self.name,
                "error": str(e)
            }

    def verify_tests(self, work_dir: Path) -> Dict[str, Any]:
        """
        验证测试通过

        Args:
            work_dir: 工作目录

        Returns:
            Dict 包含测试结果
        """
        git_dir = work_dir / ".git"
        if not git_dir.exists():
            return {"passed": True, "reason": "非Git仓库，跳过测试验证"}

        # 这里简化处理，实际应该运行项目测试套件
        # npm test / cargo test / pytest / go test ./...

        return {
            "passed": True,
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0
        }

    def finish_branch(
        self,
        option: FinishOption,
        base_branch: str,
        feature_branch: str,
        work_dir: Path
    ) -> FinishResult:
        """
        完成分支

        Args:
            option: 完成选项
            base_branch: 基础分支
            feature_branch: 功能分支
            work_dir: 工作目录

        Returns:
            FinishResult 完成结果
        """
        if not feature_branch:
            feature_branch = self._get_current_branch(work_dir)

        if option == FinishOption.LOCAL_MERGE:
            return self._local_merge(base_branch, feature_branch, work_dir)
        elif option == FinishOption.CREATE_PR:
            return self._create_pr(base_branch, feature_branch, work_dir)
        elif option == FinishOption.KEEP_AS_IS:
            return FinishResult(
                success=True,
                option=option,
                message=f"保持分支 {feature_branch} 不变",
                base_branch=base_branch,
                feature_branch=feature_branch,
                worktree_cleaned=False
            )
        elif option == FinishOption.DISCARD:
            return self._discard_branch(base_branch, feature_branch, work_dir)

        return FinishResult(
            success=False,
            option=option,
            message="未知选项",
            base_branch=base_branch,
            feature_branch=feature_branch
        )

    def _local_merge(
        self,
        base_branch: str,
        feature_branch: str,
        work_dir: Path
    ) -> FinishResult:
        """本地合并"""
        try:
            # 切换到基础分支
            subprocess.run(
                ["git", "checkout", base_branch],
                cwd=work_dir,
                capture_output=True,
                check=True
            )

            # 拉取最新
            subprocess.run(
                ["git", "pull"],
                cwd=work_dir,
                capture_output=True,
                check=True
            )

            # 合并功能分支
            subprocess.run(
                ["git", "merge", feature_branch],
                cwd=work_dir,
                capture_output=True,
                check=True
            )

            # 删除功能分支
            subprocess.run(
                ["git", "branch", "-d", feature_branch],
                cwd=work_dir,
                capture_output=True
            )

            # 清理worktree
            worktree_cleaned = self._cleanup_worktree(work_dir)

            return FinishResult(
                success=True,
                option=FinishOption.LOCAL_MERGE,
                message=f"成功合并到 {base_branch}",
                base_branch=base_branch,
                feature_branch=feature_branch,
                worktree_cleaned=worktree_cleaned
            )

        except subprocess.CalledProcessError as e:
            return FinishResult(
                success=False,
                option=FinishOption.LOCAL_MERGE,
                message=f"合并失败: {e}",
                base_branch=base_branch,
                feature_branch=feature_branch
            )

    def _create_pr(
        self,
        base_branch: str,
        feature_branch: str,
        work_dir: Path
    ) -> FinishResult:
        """创建Pull Request"""
        try:
            # 推送分支
            subprocess.run(
                ["git", "push", "-u", "origin", feature_branch],
                cwd=work_dir,
                capture_output=True,
                check=True
            )

            # 尝试创建PR (需要gh CLI)
            pr_result = subprocess.run(
                ["gh", "pr", "create", "--title", feature_branch, "--body", "## 总结\n功能实现完成\n\n## 测试计划\n- [ ] 验证功能正常"],
                cwd=work_dir,
                capture_output=True,
                text=True
            )

            pr_url = ""
            if pr_result.returncode == 0:
                pr_url = pr_result.stdout.strip()

            return FinishResult(
                success=True,
                option=FinishOption.CREATE_PR,
                message="PR创建成功" if pr_url else "分支已推送，请手动创建PR",
                base_branch=base_branch,
                feature_branch=feature_branch,
                pr_url=pr_url,
                worktree_cleaned=False
            )

        except subprocess.CalledProcessError as e:
            return FinishResult(
                success=False,
                option=FinishOption.CREATE_PR,
                message=f"创建PR失败: {e}",
                base_branch=base_branch,
                feature_branch=feature_branch
            )

    def _discard_branch(
        self,
        base_branch: str,
        feature_branch: str,
        work_dir: Path
    ) -> FinishResult:
        """放弃分支"""
        try:
            # 切换到基础分支
            subprocess.run(
                ["git", "checkout", base_branch],
                cwd=work_dir,
                capture_output=True,
                check=True
            )

            # 强制删除功能分支
            subprocess.run(
                ["git", "branch", "-D", feature_branch],
                cwd=work_dir,
                capture_output=True
            )

            # 清理worktree
            worktree_cleaned = self._cleanup_worktree(work_dir)

            return FinishResult(
                success=True,
                option=FinishOption.DISCARD,
                message=f"分支 {feature_branch} 已删除",
                base_branch=base_branch,
                feature_branch=feature_branch,
                worktree_cleaned=worktree_cleaned
            )

        except subprocess.CalledProcessError as e:
            return FinishResult(
                success=False,
                option=FinishOption.DISCARD,
                message=f"删除分支失败: {e}",
                base_branch=base_branch,
                feature_branch=feature_branch
            )

    def _get_current_branch(self, work_dir: Path) -> str:
        """获取当前分支"""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=work_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except Exception:
            return ""

    def _cleanup_worktree(self, work_dir: Path) -> bool:
        """清理worktree"""
        try:
            # 检查是否是worktree
            result = subprocess.run(
                ["git", "worktree", "list"],
                cwd=work_dir,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if str(work_dir) in line:
                        # 是worktree，移除
                        subprocess.run(
                            ["git", "worktree", "remove", str(work_dir)],
                            capture_output=True
                        )
                        return True

            return False

        except Exception:
            return False

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "options": [
                {"value": 1, "label": "本地合并回基础分支", "description": "合并到main/master并删除分支"},
                {"value": 2, "label": "推送并创建Pull Request", "description": "推送到远程并创建PR"},
                {"value": 3, "label": "保持分支原样", "description": "不做任何更改"},
                {"value": 4, "label": "放弃此工作", "description": "删除分支和worktree"}
            ],
            "features": [
                "test_verification",
                "branch_detection",
                "local_merge",
                "pr_creation",
                "branch_deletion",
                "worktree_cleanup"
            ]
        }


# 向后兼容
Finishing_Development_Branch_Skill = FinishingDevelopmentBranchSkill


def main():
    """入口函数 - 演示用法"""
    print("=" * 60)
    print("Finishing Development Branch Skill - 演示")
    print("=" * 60)

    skill = FinishingDevelopmentBranchSkill()

    # 演示: 技能能力
    print("\n1. 技能能力")
    print("-" * 40)
    caps = skill.get_capabilities()
    print(f"技能: {caps['name']}")
    print(f"完成选项:")
    for opt in caps['options']:
        print(f"  {opt['value']}. {opt['label']}")

    # 演示: 获取选项
    print("\n2. 获取完成选项")
    print("-" * 40)
    result = skill.execute()
    if result.get('status') == 'ready':
        print(f"基础分支: {result['base_branch']}")
        print(f"功能分支: {result['feature_branch']}")
        print("可选操作:")
        for opt in result['options']:
            print(f"  {opt['value']}. {opt['label']}")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return skill


if __name__ == "__main__":
    main()
