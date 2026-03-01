"""
github_actions_generator_skill

GitHub Actions 工作流生成技能 - 生成 CI/CD 工作流配置文件。
支持 Python CI / Node.js CI / Docker Build / Deploy 等工作流类型，
也支持一键生成完整流水线（full 模式）。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from leo_skills.core.base_executor import BaseExecutor


class GitHubActionsGenerator(BaseExecutor):
    """GitHub Actions 工作流生成器。

    根据工作流类型自动生成：
    - ci.yml（Python CI 或 Node.js CI）
    - docker.yml（Docker 镜像构建 + 推送）
    - deploy.yml（SSH 部署 + 健康检查）
    """

    # 支持的工作流模板元信息
    TEMPLATES: Dict[str, Dict[str, Any]] = {
        "python-ci": {
            "name": "Python CI",
            "triggers": ["push", "pull_request"],
            "python_version": "3.9",
        },
        "node-ci": {
            "name": "Node.js CI",
            "triggers": ["push", "pull_request"],
            "node_version": "18",
        },
        "docker-build": {
            "name": "Docker Build",
            "triggers": ["push"],
            "registry": "ghcr.io",
        },
        "deploy": {
            "name": "Deploy",
            "triggers": ["push"],
            "environment": "production",
        },
    }

    def __init__(self, output_dir: str = ".") -> None:
        self.name = "github_actions_generator_skill"
        self.output_dir = Path(output_dir)

    # ------------------------------------------------------------------
    # BaseExecutor 接口
    # ------------------------------------------------------------------

    def execute(
        self,
        action: str = "generate",
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """执行技能主入口。

        context / kwargs 支持的参数：
            workflow_type (str): python-ci / node-ci / docker-build / deploy / full
            project_name (str): 项目名称
            options (dict): 额外选项（python_version / node_version / registry 等）
            save (bool): 是否保存到磁盘（默认 False）
        """
        params: Dict[str, Any] = dict(context or {})
        params.update(kwargs)

        workflow_type = params.get("workflow_type", "python-ci")
        project_name = params.get("project_name", "MyProject")
        options = params.get("options", {})

        results = self.generate(
            workflow_type=workflow_type,
            project_name=project_name,
            options=options,
        )

        # 可选：保存到磁盘
        saved_paths: Dict[str, str] = {}
        if params.get("save", False):
            saved = self.save_files(results)
            saved_paths = {k: str(v) for k, v in saved.items()}

        return {
            "status": "success",
            "action": action,
            "workflow_type": workflow_type,
            "project_name": project_name,
            "files": list(results.keys()),
            "saved_paths": saved_paths,
            "data": results,
        }

    # ------------------------------------------------------------------
    # 核心生成方法
    # ------------------------------------------------------------------

    def generate(
        self,
        workflow_type: str,
        project_name: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """生成 GitHub Actions 工作流配置。

        Args:
            workflow_type: 工作流类型 (python-ci / node-ci / docker-build / deploy / full)
            project_name: 项目名称
            options: 额外选项

        Returns:
            工作流名称 -> YAML 内容 的字典
        """
        options = options or {}
        results: Dict[str, str] = {}

        if workflow_type == "python-ci":
            results["ci"] = self._python_ci(project_name, options)
        elif workflow_type == "node-ci":
            results["ci"] = self._node_ci(project_name, options)
        elif workflow_type == "docker-build":
            results["docker"] = self._docker_build(project_name, options)
        elif workflow_type == "deploy":
            results["deploy"] = self._deploy(project_name, options)
        elif workflow_type == "full":
            # 完整流水线：CI + Docker + Deploy
            results["ci"] = self._python_ci(project_name, options)
            results["docker"] = self._docker_build(project_name, options)
            results["deploy"] = self._deploy(project_name, options)

        return results

    # ------------------------------------------------------------------
    # Python CI 工作流
    # ------------------------------------------------------------------

    def _python_ci(self, project_name: str, options: Dict[str, Any]) -> str:
        """生成 Python CI 工作流。"""
        python_version = options.get("python_version", "3.9")
        test_command = options.get("test_command", "pytest")

        workflow = {
            "name": "Python CI",
            "on": {
                "push": {"branches": ["main", "master", "develop"]},
                "pull_request": {"branches": ["main", "master"]},
            },
            "jobs": {
                "test": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"uses": "actions/checkout@v4"},
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v5",
                            "with": {"python-version": python_version},
                        },
                        {
                            "name": "Cache pip",
                            "uses": "actions/cache@v4",
                            "with": {
                                "path": "~/.cache/pip",
                                "key": "${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}",
                            },
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install -r requirements.txt",
                        },
                        {
                            "name": "Lint with flake8",
                            "run": (
                                "pip install flake8 && "
                                "flake8 . --count --select=E9,F63,F7,F82 "
                                "--show-source --statistics"
                            ),
                        },
                        {
                            "name": "Run tests",
                            "run": (
                                f"pip install pytest pytest-cov && "
                                f"{test_command} --cov=./ --cov-report=xml"
                            ),
                        },
                        {
                            "name": "Upload coverage",
                            "uses": "codecov/codecov-action@v4",
                            "with": {"file": "./coverage.xml"},
                        },
                    ],
                }
            },
        }

        header = f"# {project_name} CI\n# Generated by Leo GitHub Actions Generator\n\n"
        return header + yaml.dump(
            workflow, default_flow_style=False, allow_unicode=True, sort_keys=False,
        )

    # ------------------------------------------------------------------
    # Node.js CI 工作流
    # ------------------------------------------------------------------

    def _node_ci(self, project_name: str, options: Dict[str, Any]) -> str:
        """生成 Node.js CI 工作流。"""
        node_version = options.get("node_version", "18")

        workflow = {
            "name": "Node.js CI",
            "on": {
                "push": {"branches": ["main", "master"]},
                "pull_request": {"branches": ["main", "master"]},
            },
            "jobs": {
                "build": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"uses": "actions/checkout@v4"},
                        {
                            "name": "Setup Node.js",
                            "uses": "actions/setup-node@v4",
                            "with": {
                                "node-version": node_version,
                                "cache": "npm",
                            },
                        },
                        {"name": "Install dependencies", "run": "npm ci"},
                        {"name": "Lint", "run": "npm run lint --if-present"},
                        {"name": "Test", "run": "npm test"},
                        {"name": "Build", "run": "npm run build"},
                    ],
                }
            },
        }

        header = f"# {project_name} CI\n\n"
        return header + yaml.dump(
            workflow, default_flow_style=False, allow_unicode=True, sort_keys=False,
        )

    # ------------------------------------------------------------------
    # Docker Build 工作流
    # ------------------------------------------------------------------

    def _docker_build(self, project_name: str, options: Dict[str, Any]) -> str:
        """生成 Docker 镜像构建 + 推送工作流。"""
        registry = options.get("registry", "ghcr.io")

        workflow = {
            "name": "Docker Build",
            "on": {
                "push": {
                    "branches": ["main"],
                    "tags": ["v*"],
                },
            },
            "env": {
                "REGISTRY": registry,
                "IMAGE_NAME": "${{ github.repository }}",
            },
            "jobs": {
                "build-and-push": {
                    "runs-on": "ubuntu-latest",
                    "permissions": {
                        "contents": "read",
                        "packages": "write",
                    },
                    "steps": [
                        {"uses": "actions/checkout@v4"},
                        {
                            "name": "Set up Docker Buildx",
                            "uses": "docker/setup-buildx-action@v3",
                        },
                        {
                            "name": "Login to Registry",
                            "uses": "docker/login-action@v3",
                            "with": {
                                "registry": "${{ env.REGISTRY }}",
                                "username": "${{ github.actor }}",
                                "password": "${{ secrets.GITHUB_TOKEN }}",
                            },
                        },
                        {
                            "name": "Extract metadata",
                            "id": "meta",
                            "uses": "docker/metadata-action@v5",
                            "with": {
                                "images": "${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}",
                            },
                        },
                        {
                            "name": "Build and push",
                            "uses": "docker/build-push-action@v5",
                            "with": {
                                "context": ".",
                                "push": True,
                                "tags": "${{ steps.meta.outputs.tags }}",
                                "labels": "${{ steps.meta.outputs.labels }}",
                                "cache-from": "type=gha",
                                "cache-to": "type=gha,mode=max",
                            },
                        },
                    ],
                }
            },
        }

        header = f"# {project_name} Docker Build\n\n"
        return header + yaml.dump(
            workflow, default_flow_style=False, allow_unicode=True, sort_keys=False,
        )

    # ------------------------------------------------------------------
    # Deploy 工作流
    # ------------------------------------------------------------------

    def _deploy(self, project_name: str, options: Dict[str, Any]) -> str:
        """生成 SSH 部署工作流。"""
        environment = options.get("environment", "production")

        workflow = {
            "name": "Deploy",
            "on": {
                "push": {"branches": ["main"]},
                "workflow_dispatch": None,
            },
            "jobs": {
                "deploy": {
                    "runs-on": "ubuntu-latest",
                    "environment": environment,
                    "steps": [
                        {"uses": "actions/checkout@v4"},
                        {
                            "name": "Deploy to server",
                            "uses": "appleboy/ssh-action@v1.0.3",
                            "with": {
                                "host": "${{ secrets.SERVER_HOST }}",
                                "username": "${{ secrets.SERVER_USER }}",
                                "key": "${{ secrets.SSH_PRIVATE_KEY }}",
                                "script": (
                                    "cd /var/www/${{ github.repository }}\n"
                                    "git pull origin main\n"
                                    "docker-compose pull\n"
                                    "docker-compose up -d\n"
                                ),
                            },
                        },
                        {
                            "name": "Health check",
                            "run": "curl -f ${{ secrets.HEALTH_CHECK_URL }} || exit 1",
                        },
                    ],
                }
            },
        }

        header = f"# {project_name} Deploy\n\n"
        return header + yaml.dump(
            workflow, default_flow_style=False, allow_unicode=True, sort_keys=False,
        )

    # ------------------------------------------------------------------
    # 文件保存
    # ------------------------------------------------------------------

    def save_files(self, results: Dict[str, str]) -> Dict[str, Path]:
        """将生成的工作流文件保存到 .github/workflows/ 目录。"""
        workflows_dir = self.output_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        file_mapping = {
            "ci": "ci.yml",
            "docker": "docker.yml",
            "deploy": "deploy.yml",
        }

        saved: Dict[str, Path] = {}
        for key, filename in file_mapping.items():
            if key in results:
                file_path = workflows_dir / filename
                file_path.write_text(results[key], encoding="utf-8")
                saved[key] = file_path

        return saved


__all__ = ["GitHubActionsGenerator"]
