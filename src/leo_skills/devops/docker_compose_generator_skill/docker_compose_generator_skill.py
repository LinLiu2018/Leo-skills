"""
docker_compose_generator_skill

Docker Compose 配置生成技能 - 生成 docker-compose.yml 和 .env 示例文件。
支持 Flask / FastAPI / MySQL / PostgreSQL / Redis / Nginx / Node.js 等服务类型，
同时提供常用预设组合（flask-mysql / flask-postgres-redis / fullstack 等）。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from leo_skills.core.base_executor import BaseExecutor


class DockerComposeGenerator(BaseExecutor):
    """Docker Compose 配置生成器。

    根据服务列表自动生成：
    - docker-compose.yml (YAML 配置)
    - .env.example (环境变量模板)

    支持的服务类型：flask / fastapi / mysql / postgres / redis / nginx / node / custom
    """

    # 内置预设组合
    PRESETS: Dict[str, List[Dict[str, Any]]] = {
        "flask-mysql": [
            {"name": "flask", "type": "flask", "port": 5000, "depends_on": ["mysql"]},
            {"name": "mysql", "type": "mysql"},
        ],
        "flask-postgres-redis": [
            {"name": "flask", "type": "flask", "port": 5000, "depends_on": ["postgres", "redis"]},
            {"name": "postgres", "type": "postgres"},
            {"name": "redis", "type": "redis"},
        ],
        "fastapi-postgres": [
            {"name": "fastapi", "type": "fastapi", "port": 8000, "depends_on": ["postgres"]},
            {"name": "postgres", "type": "postgres"},
        ],
        "fullstack": [
            {"name": "nginx", "type": "nginx", "depends_on": ["flask", "node"]},
            {"name": "flask", "type": "flask", "port": 5000, "depends_on": ["mysql", "redis"]},
            {"name": "node", "type": "node", "port": 3000},
            {"name": "mysql", "type": "mysql"},
            {"name": "redis", "type": "redis"},
        ],
    }

    def __init__(self, output_dir: str = ".") -> None:
        self.name = "docker_compose_generator_skill"
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
            services (list[dict]): 服务列表，每项包含 name / type / port 等
            networks (list[str]): 网络名称列表
            volumes (list[str]): 卷名称列表
            project_name (str): 项目名称
            preset (str): 预设名称，如果提供则忽略 services 参数
        """
        params: Dict[str, Any] = dict(context or {})
        params.update(kwargs)

        preset = params.get("preset")
        if preset:
            result = self.generate_preset(preset)
        else:
            services = params.get("services", [
                {"name": "app", "type": "flask", "port": 5000, "depends_on": ["db"]},
                {"name": "db", "type": "mysql"},
            ])
            networks = params.get("networks")
            volumes = params.get("volumes")
            project_name = params.get("project_name", "app")
            result = self.generate(
                services=services,
                networks=networks,
                volumes=volumes,
                project_name=project_name,
            )

        return {
            "status": "success",
            "action": action,
            "files": list(result.keys()),
            "data": result,
        }

    # ------------------------------------------------------------------
    # 核心生成方法
    # ------------------------------------------------------------------

    def generate(
        self,
        services: List[Dict[str, Any]],
        networks: Optional[List[str]] = None,
        volumes: Optional[List[str]] = None,
        project_name: str = "app",
    ) -> Dict[str, str]:
        """生成 docker-compose 配置。

        Args:
            services: 服务列表
            networks: 网络名称列表
            volumes: 卷名称列表
            project_name: 项目名称

        Returns:
            包含 docker_compose 和 env_example 的字典
        """
        networks = networks or ["default"]
        volumes = volumes or []

        compose: Dict[str, Any] = {
            "version": "3.8",
            "services": {},
            "networks": {},
            "volumes": {},
        }

        # 处理服务
        for service in services:
            service_name = service.get("name", "app")
            compose["services"][service_name] = self._build_service(service)

        # 处理网络
        for network in networks:
            compose["networks"][network] = {"driver": "bridge"}

        # 处理卷
        for volume in volumes:
            compose["volumes"][volume] = {}

        # 生成 YAML
        yaml_content = yaml.dump(
            compose, default_flow_style=False, allow_unicode=True, sort_keys=False,
        )

        # 生成 .env 示例
        env_content = self._generate_env_example(services)

        return {
            "docker_compose": yaml_content,
            "env_example": env_content,
        }

    def generate_preset(self, preset: str) -> Dict[str, str]:
        """根据预设名称生成配置。

        Args:
            preset: 预设名称（flask-mysql / flask-postgres-redis / fastapi-postgres / fullstack）

        Returns:
            docker_compose + env_example
        """
        services = self.PRESETS.get(preset, self.PRESETS["flask-mysql"])
        # 自动收集需要持久化的卷
        volumes = [
            f'{s["name"]}_data'
            for s in services
            if s.get("type") in ("mysql", "postgres", "redis")
        ]
        return self.generate(services=services, volumes=volumes)

    # ------------------------------------------------------------------
    # 服务类型分发
    # ------------------------------------------------------------------

    def _build_service(self, service: Dict[str, Any]) -> Dict[str, Any]:
        """根据 type 字段分发到具体的服务生成器。"""
        dispatch = {
            "flask": self._flask_service,
            "fastapi": self._fastapi_service,
            "mysql": self._mysql_service,
            "postgres": self._postgres_service,
            "redis": self._redis_service,
            "nginx": self._nginx_service,
            "node": self._node_service,
        }
        builder = dispatch.get(service.get("type", "custom"), self._custom_service)
        return builder(service)

    # ------------------------------------------------------------------
    # 各服务类型模板
    # ------------------------------------------------------------------

    def _flask_service(self, svc: Dict[str, Any]) -> Dict[str, Any]:
        """Flask 服务配置。"""
        name = svc.get("name", "flask")
        port = svc.get("port", 5000)
        context = svc.get("context", "./backend")
        return {
            "build": {
                "context": context,
                "dockerfile": svc.get("dockerfile", "Dockerfile"),
            },
            "container_name": f"{name}-container",
            "ports": [f"{port}:{port}"],
            "environment": [
                "FLASK_ENV=${FLASK_ENV:-development}",
                "DATABASE_URL=${DATABASE_URL}",
                "SECRET_KEY=${SECRET_KEY}",
            ],
            "volumes": [f"{context}:/app"],
            "depends_on": svc.get("depends_on", []),
            "networks": svc.get("networks", ["default"]),
            "restart": "unless-stopped",
        }

    def _fastapi_service(self, svc: Dict[str, Any]) -> Dict[str, Any]:
        """FastAPI 服务配置。"""
        name = svc.get("name", "fastapi")
        port = svc.get("port", 8000)
        context = svc.get("context", "./backend")
        return {
            "build": {
                "context": context,
                "dockerfile": svc.get("dockerfile", "Dockerfile"),
            },
            "container_name": f"{name}-container",
            "ports": [f"{port}:{port}"],
            "environment": [
                "DATABASE_URL=${DATABASE_URL}",
                "SECRET_KEY=${SECRET_KEY}",
            ],
            "command": "uvicorn main:app --host 0.0.0.0 --port 8000 --reload",
            "volumes": [f"{context}:/app"],
            "depends_on": svc.get("depends_on", []),
            "networks": svc.get("networks", ["default"]),
            "restart": "unless-stopped",
        }

    def _mysql_service(self, svc: Dict[str, Any]) -> Dict[str, Any]:
        """MySQL 服务配置。"""
        name = svc.get("name", "mysql")
        return {
            "image": svc.get("image", "mysql:8.0"),
            "container_name": f"{name}-container",
            "ports": ["3306:3306"],
            "environment": [
                "MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}",
                "MYSQL_DATABASE=${MYSQL_DATABASE}",
                "MYSQL_USER=${MYSQL_USER}",
                "MYSQL_PASSWORD=${MYSQL_PASSWORD}",
            ],
            "volumes": [f"{name}_data:/var/lib/mysql"],
            "networks": svc.get("networks", ["default"]),
            "restart": "unless-stopped",
            "healthcheck": {
                "test": ["CMD", "mysqladmin", "ping", "-h", "localhost"],
                "interval": "10s",
                "timeout": "5s",
                "retries": 5,
            },
        }

    def _postgres_service(self, svc: Dict[str, Any]) -> Dict[str, Any]:
        """PostgreSQL 服务配置。"""
        name = svc.get("name", "postgres")
        return {
            "image": svc.get("image", "postgres:15"),
            "container_name": f"{name}-container",
            "ports": ["5432:5432"],
            "environment": [
                "POSTGRES_USER=${POSTGRES_USER}",
                "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}",
                "POSTGRES_DB=${POSTGRES_DB}",
            ],
            "volumes": [f"{name}_data:/var/lib/postgresql/data"],
            "networks": svc.get("networks", ["default"]),
            "restart": "unless-stopped",
            "healthcheck": {
                "test": ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"],
                "interval": "10s",
                "timeout": "5s",
                "retries": 5,
            },
        }

    def _redis_service(self, svc: Dict[str, Any]) -> Dict[str, Any]:
        """Redis 服务配置。"""
        name = svc.get("name", "redis")
        return {
            "image": svc.get("image", "redis:7-alpine"),
            "container_name": f"{name}-container",
            "ports": ["6379:6379"],
            "volumes": [f"{name}_data:/data"],
            "networks": svc.get("networks", ["default"]),
            "restart": "unless-stopped",
            "healthcheck": {
                "test": ["CMD", "redis-cli", "ping"],
                "interval": "10s",
                "timeout": "5s",
                "retries": 5,
            },
        }

    def _nginx_service(self, svc: Dict[str, Any]) -> Dict[str, Any]:
        """Nginx 服务配置。"""
        name = svc.get("name", "nginx")
        return {
            "image": svc.get("image", "nginx:alpine"),
            "container_name": f"{name}-container",
            "ports": ["80:80", "443:443"],
            "volumes": [
                "./nginx/nginx.conf:/etc/nginx/nginx.conf:ro",
                "./nginx/conf.d:/etc/nginx/conf.d:ro",
            ],
            "depends_on": svc.get("depends_on", []),
            "networks": svc.get("networks", ["default"]),
            "restart": "unless-stopped",
        }

    def _node_service(self, svc: Dict[str, Any]) -> Dict[str, Any]:
        """Node.js 服务配置。"""
        name = svc.get("name", "node")
        port = svc.get("port", 3000)
        context = svc.get("context", "./frontend")
        return {
            "build": {
                "context": context,
                "dockerfile": svc.get("dockerfile", "Dockerfile"),
            },
            "container_name": f"{name}-container",
            "ports": [f"{port}:{port}"],
            "environment": [
                f"PORT={port}",
                "NODE_ENV=${NODE_ENV:-development}",
            ],
            "volumes": [f"{context}:/app", "/app/node_modules"],
            "networks": svc.get("networks", ["default"]),
            "restart": "unless-stopped",
        }

    def _custom_service(self, svc: Dict[str, Any]) -> Dict[str, Any]:
        """自定义服务配置（透传用户提供的字段）。"""
        config: Dict[str, Any] = {}

        if "image" in svc:
            config["image"] = svc["image"]
        elif "build" in svc:
            config["build"] = svc["build"]
        else:
            config["build"] = "."

        for key in ("ports", "environment", "volumes", "depends_on"):
            if key in svc:
                config[key] = svc[key]

        config["networks"] = svc.get("networks", ["default"])
        config["restart"] = svc.get("restart", "unless-stopped")
        return config

    # ------------------------------------------------------------------
    # .env 示例生成
    # ------------------------------------------------------------------

    def _generate_env_example(self, services: List[Dict[str, Any]]) -> str:
        """生成 .env.example 文件内容。"""
        lines = [
            "# Docker Compose Environment Variables",
            "# Generated by Leo Docker Compose Generator",
            "",
        ]

        # 各服务类型对应的默认环境变量
        env_map: Dict[str, List[str]] = {
            "flask": [
                "FLASK_ENV=development",
                "SECRET_KEY=your-secret-key",
                "DATABASE_URL=mysql+pymysql://user:password@mysql/dbname",
            ],
            "fastapi": [
                "SECRET_KEY=your-secret-key",
                "DATABASE_URL=postgresql://user:password@postgres/dbname",
            ],
            "mysql": [
                "MYSQL_ROOT_PASSWORD=rootpassword",
                "MYSQL_DATABASE=mydb",
                "MYSQL_USER=user",
                "MYSQL_PASSWORD=password",
            ],
            "postgres": [
                "POSTGRES_USER=user",
                "POSTGRES_PASSWORD=password",
                "POSTGRES_DB=mydb",
            ],
            "node": [
                "NODE_ENV=development",
            ],
        }

        for service in services:
            stype = service.get("type", "custom")
            sname = service.get("name", "app").upper()
            if stype in env_map:
                lines.append(f"# {sname} Configuration")
                lines.extend(env_map[stype])
                lines.append("")

        return "\n".join(lines)


__all__ = ["DockerComposeGenerator"]
