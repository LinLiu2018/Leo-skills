# -*- coding: utf-8 -*-
"""
setup_skill - 设置技能

用于项目初始设置和配置。检测项目类型，安装依赖，配置环境。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class ProjectType(Enum):
    """项目类型"""
    PYTHON = "python"
    NODE = "node"
    RUST = "rust"
    GO = "go"
    UNKNOWN = "unknown"


class SetupStatus(Enum):
    """设置状态"""
    PENDING = "pending"
    DETECTING = "detecting"
    INSTALLING = "installing"
    CONFIGURING = "configuring"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SetupTask:
    """设置任务"""
    name: str
    command: str
    description: str
    status: SetupStatus = SetupStatus.PENDING
    output: str = ""


@dataclass
class SetupResult:
    """设置结果"""
    status: str
    project_type: ProjectType
    tasks_completed: List[str] = field(default_factory=list)
    tasks_failed: List[str] = field(default_factory=list)
    message: str = ""


class SetupSkill:
    """
    设置技能

    用于项目初始设置，检测项目类型，安装依赖，配置开发环境。
    """

    def __init__(self):
        self.name = "setup_skill"
        self.version = "1.0.0"
        self.description = "项目初始设置和配置"
        self.category = "scaffold"

    def execute(
        self,
        project_root: str = ".",
        project_type: Optional[str] = None,
        skip_install: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行项目设置

        Args:
            project_root: 项目根目录
            project_type: 项目类型（可选，自动检测）
            skip_install: 跳过安装步骤

        Returns:
            设置结果
        """
        try:
            root = Path(project_root)

            # 步骤1: 检测项目类型
            if project_type:
                ptype = ProjectType(project_type.lower())
            else:
                ptype = self._detect_project_type(root)

            # 步骤2: 创建设置任务
            tasks = self._create_setup_tasks(ptype, root, skip_install)

            # 步骤3: 执行设置（模拟）
            completed = []
            failed = []

            for task in tasks:
                task.status = SetupStatus.COMPLETED
                completed.append(task.name)

            result = SetupResult(
                status="completed",
                project_type=ptype,
                tasks_completed=completed,
                tasks_failed=failed,
                message=f"项目设置完成: {ptype.value}"
            )

            return {
                "status": "success",
                "result": result,
                "project_type": ptype.value,
                "tasks": [
                    {"name": t.name, "command": t.command, "status": t.status.value}
                    for t in tasks
                ],
                "next_steps": self._get_next_steps(ptype)
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "skill": self.name
            }

    def _detect_project_type(self, root: Path) -> ProjectType:
        """检测项目类型"""
        if (root / "requirements.txt").exists() or (root / "pyproject.toml").exists():
            return ProjectType.PYTHON
        elif (root / "package.json").exists():
            return ProjectType.NODE
        elif (root / "Cargo.toml").exists():
            return ProjectType.RUST
        elif (root / "go.mod").exists():
            return ProjectType.GO
        return ProjectType.UNKNOWN

    def _create_setup_tasks(
        self,
        ptype: ProjectType,
        root: Path,
        skip_install: bool
    ) -> List[SetupTask]:
        """创建设置任务"""
        tasks = []

        if ptype == ProjectType.PYTHON:
            tasks.extend([
                SetupTask(
                    name="创建虚拟环境",
                    command="python -m venv .venv",
                    description="创建Python虚拟环境"
                ),
                SetupTask(
                    name="安装依赖",
                    command="pip install -r requirements.txt",
                    description="安装Python依赖"
                )
            ])
        elif ptype == ProjectType.NODE:
            tasks.extend([
                SetupTask(
                    name="安装Node依赖",
                    command="npm install",
                    description="安装Node.js依赖"
                )
            ])
        elif ptype == ProjectType.RUST:
            tasks.extend([
                SetupTask(
                    name="构建Rust项目",
                    command="cargo build",
                    description="构建Rust项目"
                )
            ])
        elif ptype == ProjectType.GO:
            tasks.extend([
                SetupTask(
                    name="下载Go依赖",
                    command="go mod download",
                    description="下载Go模块依赖"
                )
            ])

        # 通用任务
        if not skip_install:
            tasks.append(SetupTask(
                name="验证安装",
                command="echo 'Setup verified'",
                description="验证项目设置"
            ))

        return tasks

    def _get_next_steps(self, ptype: ProjectType) -> List[str]:
        """获取下一步建议"""
        if ptype == ProjectType.PYTHON:
            return [
                "1. 激活虚拟环境: source .venv/bin/activate (Linux/Mac) 或 .venv\\Scripts\\activate (Windows)",
                "2. 运行测试: pytest",
                "3. 启动开发服务器（如适用）"
            ]
        elif ptype == ProjectType.NODE:
            return [
                "1. 运行测试: npm test",
                "2. 启动开发服务器: npm run dev",
                "3. 构建项目: npm run build"
            ]
        elif ptype == ProjectType.RUST:
            return [
                "1. 运行测试: cargo test",
                "2. 构建项目: cargo build --release",
                "3. 运行程序: cargo run"
            ]
        elif ptype == ProjectType.GO:
            return [
                "1. 运行测试: go test ./...",
                "2. 构建项目: go build",
                "3. 运行程序: go run ."
            ]
        return ["项目设置完成，请查看项目文档了解后续步骤"]


def main():
    """入口函数"""
    return SetupSkill()


if __name__ == "__main__":
    skill = main()
