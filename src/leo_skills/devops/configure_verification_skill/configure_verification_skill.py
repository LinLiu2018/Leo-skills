# -*- coding: utf-8 -*-
"""
configure_verification_skill - 配置验证技能

配置项目的验证命令，用于测试、lint、类型检查等。
基于 obra/superpowers 的 configure-verification 技能实现。
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class VerificationConfig:
    """验证配置"""
    test: str = ""
    lint: str = ""
    typecheck: str = ""
    build: str = ""
    coverage: str = ""
    dev_server_command: str = ""
    dev_server_url: str = ""
    dev_server_startup_seconds: int = 5


class ConfigureVerificationSkill:
    """
    配置验证技能

    功能：
    - 检测项目类型和配置
    - 自动发现验证命令
    - 创建 verification-config.json
    - 配置开发服务器
    - 配置认证信息

    使用场景：
    - 新项目设置
    - 验证配置丢失或损坏
    - 更新验证流程
    """

    DEFAULT_CONFIG = {
        "commands": {
            "test": "",
            "lint": "",
            "typecheck": "",
            "build": "",
            "coverage": ""
        },
        "devServer": {
            "command": "",
            "url": "",
            "startupSeconds": 5
        },
        "auth": {
            "strategy": "none",
            "loginRoute": "/login",
            "credentials": {
                "usernameVar": "TEST_USER_EMAIL",
                "passwordVar": "TEST_USER_PASSWORD"
            },
            "storageState": ".claude/verification/auth-state.json"
        },
        "deployment": {
            "enabled": False,
            "service": "vercel",
            "useForBrowserVerification": True,
            "fallbackToLocal": True,
            "waitForDeployment": True,
            "deploymentTimeout": 300,
            "tokenVar": "VERCEL_TOKEN"
        },
        "browser": {
            "tool": "auto"
        }
    }

    def __init__(self, base_path: str = "."):
        self.name = "configure_verification_skill"
        self.version = "1.0.0"
        self.description = "配置验证技能 - 设置项目验证命令"
        self.base_path = Path(base_path)

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行技能主入口

        Args:
            work_dir: 工作目录
            auto_detect: 是否自动检测

        Returns:
            Dict 包含配置结果
        """
        work_dir = Path(kwargs.get("work_dir", self.base_path))
        auto_detect = kwargs.get("auto_detect", True)

        try:
            config = self.configure(work_dir, auto_detect)

            return {
                "status": "success",
                "skill": self.name,
                "config_path": str(work_dir / ".claude" / "verification-config.json"),
                "config": config,
                "message": "验证配置完成"
            }

        except Exception as e:
            return {
                "status": "error",
                "skill": self.name,
                "error": str(e)
            }

    def configure(
        self,
        work_dir: Path,
        auto_detect: bool = True
    ) -> Dict[str, Any]:
        """
        配置验证

        Args:
            work_dir: 工作目录
            auto_detect: 是否自动检测

        Returns:
            Dict 配置
        """
        config = self.DEFAULT_CONFIG.copy()

        if auto_detect:
            # 检测项目类型并配置命令
            commands = self._detect_commands(work_dir)
            config["commands"].update(commands)

            # 检测开发服务器
            dev_server = self._detect_dev_server(work_dir)
            config["devServer"].update(dev_server)

            # 检测部署配置
            deployment = self._detect_deployment(work_dir)
            if deployment:
                config["deployment"].update(deployment)

        # 确保 .claude 目录存在
        claude_dir = work_dir / ".claude"
        claude_dir.mkdir(parents=True, exist_ok=True)

        # 写入配置
        config_path = claude_dir / "verification-config.json"
        config_path.write_text(
            json.dumps(config, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        # 更新 .gitignore
        self._update_gitignore(work_dir)

        return config

    def _detect_commands(self, work_dir: Path) -> Dict[str, str]:
        """检测验证命令"""
        commands = {}

        # Node.js 项目
        if (work_dir / "package.json").exists():
            pkg = json.loads((work_dir / "package.json").read_text())
            scripts = pkg.get("scripts", {})

            if "test" in scripts:
                commands["test"] = "npm test"
            if "lint" in scripts:
                commands["lint"] = "npm run lint"
            if "build" in scripts:
                commands["build"] = "npm run build"
            if "typecheck" in scripts:
                commands["typecheck"] = "npm run typecheck"
            elif "tsc" in scripts:
                commands["typecheck"] = "npm run tsc"

        # Python 项目
        elif (work_dir / "requirements.txt").exists() or (work_dir / "pyproject.toml").exists():
            commands["test"] = "pytest"
            commands["lint"] = "flake8"
            commands["typecheck"] = "mypy"

        # Rust 项目
        elif (work_dir / "Cargo.toml").exists():
            commands["test"] = "cargo test"
            commands["build"] = "cargo build"
            commands["lint"] = "cargo clippy"

        # Go 项目
        elif (work_dir / "go.mod").exists():
            commands["test"] = "go test ./..."
            commands["build"] = "go build"
            commands["lint"] = "golangci-lint run"

        return commands

    def _detect_dev_server(self, work_dir: Path) -> Dict[str, Any]:
        """检测开发服务器"""
        dev_server = {
            "command": "",
            "url": "",
            "startupSeconds": 5
        }

        # Node.js 项目
        if (work_dir / "package.json").exists():
            pkg = json.loads((work_dir / "package.json").read_text())
            scripts = pkg.get("scripts", {})

            if "dev" in scripts:
                dev_server["command"] = "npm run dev"
                dev_server["url"] = "http://localhost:3000"
            elif "start" in scripts:
                dev_server["command"] = "npm start"
                dev_server["url"] = "http://localhost:3000"

            # 检查 Next.js
            if "next" in str(pkg.get("dependencies", {})):
                dev_server["url"] = "http://localhost:3000"
            # 检查 Vite
            elif "vite" in str(pkg.get("devDependencies", {})):
                dev_server["url"] = "http://localhost:5173"

        # Python Flask/Django
        elif (work_dir / "requirements.txt").exists():
            if (work_dir / "manage.py").exists():
                dev_server["command"] = "python manage.py runserver"
                dev_server["url"] = "http://localhost:8000"
            elif (work_dir / "app.py").exists():
                dev_server["command"] = "flask run"
                dev_server["url"] = "http://localhost:5000"

        return dev_server

    def _detect_deployment(self, work_dir: Path) -> Optional[Dict[str, Any]]:
        """检测部署配置"""
        # 检查 Vercel 配置
        if (work_dir / ".vercel" / "project.json").exists() or (work_dir / "vercel.json").exists():
            return {
                "enabled": True,
                "service": "vercel",
                "useForBrowserVerification": True,
                "fallbackToLocal": True,
                "waitForDeployment": True,
                "deploymentTimeout": 300,
                "tokenVar": "VERCEL_TOKEN"
            }

        return None

    def _update_gitignore(self, work_dir: Path) -> bool:
        """更新 .gitignore"""
        gitignore_path = work_dir / ".gitignore"

        entries_to_add = [
            ".claude/verification/auth-state.json",
            ".env.verification"
        ]

        try:
            if gitignore_path.exists():
                content = gitignore_path.read_text(encoding="utf-8")
                new_entries = [e for e in entries_to_add if e not in content]

                if new_entries:
                    with open(gitignore_path, "a", encoding="utf-8") as f:
                        f.write("\n# Verification\n")
                        for entry in new_entries:
                            f.write(f"{entry}\n")
            else:
                gitignore_path.write_text(
                    "# Verification\n" + "\n".join(entries_to_add) + "\n",
                    encoding="utf-8"
                )

            return True

        except Exception:
            return False

    def load_config(self, work_dir: Optional[Path] = None) -> Optional[Dict[str, Any]]:
        """加载配置"""
        work_dir = Path(work_dir) if work_dir else self.base_path
        config_path = work_dir / ".claude" / "verification-config.json"

        if not config_path.exists():
            return None

        try:
            return json.loads(config_path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "features": [
                "project_detection",
                "command_discovery",
                "config_generation",
                "dev_server_config",
                "auth_config",
                "deployment_config",
                "gitignore_update"
            ],
            "supported_project_types": [
                "nodejs",
                "python",
                "rust",
                "go"
            ],
            "config_file": ".claude/verification-config.json"
        }


# 向后兼容
Configure_Verification_Skill = ConfigureVerificationSkill


def main():
    """入口函数 - 演示用法"""
    print("=" * 60)
    print("Configure Verification Skill - 演示")
    print("=" * 60)

    skill = ConfigureVerificationSkill()

    # 演示: 技能能力
    print("\n1. 技能能力")
    print("-" * 40)
    caps = skill.get_capabilities()
    print(f"技能: {caps['name']}")
    print(f"支持项目类型: {', '.join(caps['supported_project_types'])}")

    # 演示: 配置验证
    print("\n2. 配置验证")
    print("-" * 40)
    result = skill.execute()
    print(f"状态: {result['status']}")
    print(f"配置路径: {result.get('config_path', 'N/A')}")
    if result.get('config'):
            print(f"命令:")
            for cmd, value in result['config'].get('commands', {}).items():
                if value:
                    print(f"  - {cmd}: {value}")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return skill


if __name__ == "__main__":
    main()
