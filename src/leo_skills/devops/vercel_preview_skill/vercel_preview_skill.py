# -*- coding: utf-8 -*-
"""
vercel_preview_skill - Vercel Preview 技能

解析当前 Git 分支的 Vercel 预览部署 URL。
用于浏览器验证和阶段检查点。
基于 obra/superpowers 的 vercel-preview 技能实现。
"""
from leo_skills.core.base_executor import BaseExecutor

import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PreviewResult:
    """预览 URL 解析结果"""
    success: bool
    url: str
    branch: str
    commit: str
    status: str
    message: str


class VercelPreviewSkill(BaseExecutor):
    """
    Vercel Preview 技能

    功能：
    - 获取 Git 上下文（分支、提交）
    - 检查 Vercel 项目链接
    - 查询分支的部署
    - 等待部署完成（可选）
    - 返回预览 URL

    使用场景：
    - 浏览器验证前获取预览 URL
    - 阶段检查点浏览器测试
    - 直接检查部署状态
    """

    def __init__(self, base_path: str = "."):
        self.name = "vercel_preview_skill"
        self.version = "1.0.0"
        self.description = "Vercel Preview 技能 - 解析预览部署 URL"
        self.base_path = Path(base_path)

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行技能主入口

        Args:
            wait_for_deployment: 是否等待部署完成
            timeout: 等待超时（秒）
            work_dir: 工作目录

        Returns:
            Dict 包含预览 URL
        """
        wait = kwargs.get("wait_for_deployment", True)
        timeout = kwargs.get("timeout", 300)
        work_dir = Path(kwargs.get("work_dir", self.base_path))

        try:
            result = self.resolve_preview(
                wait_for_deployment=wait,
                timeout=timeout,
                work_dir=work_dir
            )

            return {
                "status": "success" if result.success else "error",
                "skill": self.name,
                "url": result.url,
                "branch": result.branch,
                "commit": result.commit,
                "deployment_status": result.status,
                "message": result.message
            }

        except Exception as e:
            return {
                "status": "error",
                "skill": self.name,
                "error": str(e)
            }

    def resolve_preview(
        self,
        wait_for_deployment: bool = True,
        timeout: int = 300,
        work_dir: Optional[Path] = None
    ) -> PreviewResult:
        """
        解析预览 URL

        Args:
            wait_for_deployment: 是否等待部署完成
            timeout: 等待超时
            work_dir: 工作目录

        Returns:
            PreviewResult 解析结果
        """
        work_dir = Path(work_dir) if work_dir else self.base_path

        # 1. 检查 Vercel 项目链接
        vercel_config = work_dir / ".vercel" / "project.json"
        if not vercel_config.exists():
            return PreviewResult(
                success=False,
                url="",
                branch="",
                commit="",
                status="NOT_LINKED",
                message="项目未链接到 Vercel，请运行 'vercel link'"
            )

        # 2. 获取 Git 上下文
        branch = self._get_branch(work_dir)
        commit = self._get_commit(work_dir)

        if not branch:
            return PreviewResult(
                success=False,
                url="",
                branch="",
                commit=commit,
                status="NO_BRANCH",
                message="无法获取当前分支"
            )

        # 3. 查询部署
        url = self._get_deployment_url(branch, work_dir)

        if url:
            return PreviewResult(
                success=True,
                url=url,
                branch=branch,
                commit=commit,
                status="READY",
                message=f"找到就绪的部署: {url}"
            )

        # 4. 检查是否有正在构建的部署
        building_url = self._get_building_deployment(branch, work_dir)

        if building_url and wait_for_deployment:
            # 等待部署完成
            final_url = self._wait_for_deployment(branch, timeout, work_dir)

            if final_url:
                return PreviewResult(
                    success=True,
                    url=final_url,
                    branch=branch,
                    commit=commit,
                    status="READY",
                    message=f"部署已就绪: {final_url}"
                )
            else:
                return PreviewResult(
                    success=False,
                    url=building_url,
                    branch=branch,
                    commit=commit,
                    status="TIMEOUT",
                    message=f"等待部署超时 ({timeout}s)"
                )

        if building_url:
            return PreviewResult(
                success=False,
                url=building_url,
                branch=branch,
                commit=commit,
                status="BUILDING",
                message="部署正在构建中"
            )

        return PreviewResult(
            success=False,
            url="",
            branch=branch,
            commit=commit,
            status="NOT_FOUND",
            message=f"未找到分支 '{branch}' 的部署"
        )

    def _get_branch(self, work_dir: Path) -> str:
        """获取当前分支"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=work_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except Exception:
            return ""

    def _get_commit(self, work_dir: Path) -> str:
        """获取当前提交"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=work_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except Exception:
            return ""

    def _get_deployment_url(self, branch: str, work_dir: Path) -> str:
        """获取部署 URL"""
        try:
            # 使用 vercel CLI 查询部署
            result = subprocess.run(
                ["vercel", "ls", "--json", "-m", f"gitBranch={branch}", "--status", "READY"],
                cwd=work_dir,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                import json
                deployments = json.loads(result.stdout)
                if deployments and len(deployments) > 0:
                    return f"https://{deployments[0].get('url', '')}"

        except Exception:
            pass

        return ""

    def _get_building_deployment(self, branch: str, work_dir: Path) -> str:
        """获取正在构建的部署"""
        try:
            result = subprocess.run(
                ["vercel", "ls", "--json", "-m", f"gitBranch={branch}", "--status", "BUILDING"],
                cwd=work_dir,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                import json
                deployments = json.loads(result.stdout)
                if deployments and len(deployments) > 0:
                    return f"https://{deployments[0].get('url', '')}"

        except Exception:
            pass

        return ""

    def _wait_for_deployment(
        self,
        branch: str,
        timeout: int,
        work_dir: Path
    ) -> str:
        """等待部署完成"""
        import time

        start_time = time.time()
        check_interval = 10  # 每 10 秒检查一次

        while time.time() - start_time < timeout:
            url = self._get_deployment_url(branch, work_dir)
            if url:
                return url

            time.sleep(check_interval)

        return ""

    def check_deployment_status(self, url: str, work_dir: Optional[Path] = None) -> str:
        """检查部署状态"""
        work_dir = Path(work_dir) if work_dir else self.base_path

        try:
            result = subprocess.run(
                ["vercel", "inspect", url, "--json"],
                cwd=work_dir,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                import json
                info = json.loads(result.stdout)
                return info.get("readyState", "UNKNOWN")

        except Exception:
            pass

        return "UNKNOWN"

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "features": [
                "branch_detection",
                "commit_resolution",
                "deployment_query",
                "url_resolution",
                "wait_for_ready",
                "status_check"
            ],
            "requires": [
                "vercel_cli",
                "vercel_project_link"
            ]
        }


# 向后兼容
Vercel_Preview_Skill = VercelPreviewSkill


def main():
    """入口函数 - 演示用法"""
    print("=" * 60)
    print("Vercel Preview Skill - 演示")
    print("=" * 60)

    skill = VercelPreviewSkill()

    # 演示: 技能能力
    print("\n1. 技能能力")
    print("-" * 40)
    caps = skill.get_capabilities()
    print(f"技能: {caps['name']}")
    print(f"功能: {', '.join(caps['features'])}")

    # 演示: 解析预览 URL
    print("\n2. 解析预览 URL")
    print("-" * 40)
    result = skill.resolve_preview(wait_for_deployment=False)
    print(f"状态: {result.status}")
    print(f"分支: {result.branch}")
    print(f"提交: {result.commit}")
    if result.url:
        print(f"URL: {result.url}")
    print(f"消息: {result.message}")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return skill


if __name__ == "__main__":
    main()
