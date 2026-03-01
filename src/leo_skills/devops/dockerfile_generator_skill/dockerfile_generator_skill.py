"""
dockerfile_generator_skill

Dockerfile 生成技能 - 自动生成优化的 Dockerfile、.dockerignore 和 docker-compose 配置。
支持 Flask / FastAPI / Node.js / Vue / React 等应用类型，
支持多阶段构建、开发 / 生产环境双配置。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from leo_skills.core.base_executor import BaseExecutor


class DockerfileGenerator(BaseExecutor):
    """Dockerfile 生成器。

    根据应用类型自动生成：
    - Dockerfile（支持多阶段构建）
    - .dockerignore
    - docker-compose.yml（开发环境）
    - docker-compose.prod.yml（生产环境）
    """

    # 各应用类型的默认配置
    APP_CONFIGS: Dict[str, Dict[str, Any]] = {
        "flask": {
            "base_image": "python:3.9-slim",
            "port": 5000,
            "install_cmd": "pip install --no-cache-dir -r requirements.txt",
            "run_cmd": "gunicorn -w 4 -b 0.0.0.0:5000 app:app",
        },
        "fastapi": {
            "base_image": "python:3.9-slim",
            "port": 8000,
            "install_cmd": "pip install --no-cache-dir -r requirements.txt",
            "run_cmd": "uvicorn app.main:app --host 0.0.0.0 --port 8000",
        },
        "node": {
            "base_image": "node:18-alpine",
            "port": 3000,
            "install_cmd": "npm ci --only=production",
            "run_cmd": "node server.js",
        },
        "vue": {
            "base_image": "node:18-alpine",
            "build_image": "nginx:alpine",
            "port": 80,
            "install_cmd": "npm ci",
            "build_cmd": "npm run build",
        },
        "react": {
            "base_image": "node:18-alpine",
            "build_image": "nginx:alpine",
            "port": 80,
            "install_cmd": "npm ci",
            "build_cmd": "npm run build",
        },
    }

    def __init__(self, output_dir: str = ".") -> None:
        self.name = "dockerfile_generator_skill"
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
            app_type (str): 应用类型 (flask / fastapi / node / vue / react)
            runtime (str): 自定义基础镜像
            port (int): 暴露端口
            multi_stage (bool): 是否多阶段构建（默认 True）
            with_compose (bool): 是否生成 docker-compose（默认 True）
            services (list[str]): 额外服务（mysql / redis / nginx）
            save (bool): 是否保存到磁盘（默认 False）
        """
        params: Dict[str, Any] = dict(context or {})
        params.update(kwargs)

        app_type = params.get("app_type", "flask")
        runtime = params.get("runtime")
        port = params.get("port")
        multi_stage = params.get("multi_stage", True)
        with_compose = params.get("with_compose", True)
        services = params.get("services", [])

        results = self.generate(
            app_type=app_type,
            runtime=runtime,
            port=port,
            multi_stage=multi_stage,
            with_compose=with_compose,
            services=services,
        )

        # 可选：保存到磁盘
        saved_paths: Dict[str, str] = {}
        if params.get("save", False):
            saved = self.save_files(results)
            saved_paths = {k: str(v) for k, v in saved.items()}

        return {
            "status": "success",
            "action": action,
            "app_type": app_type,
            "files": list(results.keys()),
            "saved_paths": saved_paths,
            "data": results,
        }

    # ------------------------------------------------------------------
    # 核心生成方法
    # ------------------------------------------------------------------

    def generate(
        self,
        app_type: str,
        runtime: Optional[str] = None,
        port: Optional[int] = None,
        multi_stage: bool = True,
        with_compose: bool = True,
        services: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """生成 Docker 配置文件集合。

        Args:
            app_type: 应用类型
            runtime: 自定义基础镜像
            port: 暴露端口
            multi_stage: 是否多阶段构建
            with_compose: 是否生成 docker-compose
            services: 额外服务列表

        Returns:
            配置文件名 -> 文件内容 的字典
        """
        services = services or []
        # 复制一份配置避免修改原始字典
        config = dict(self.APP_CONFIGS.get(app_type, self.APP_CONFIGS["flask"]))

        if runtime:
            config["base_image"] = runtime
        if port:
            config["port"] = port

        results: Dict[str, str] = {}

        # 1. 生成 Dockerfile
        if app_type in ("vue", "react") and multi_stage:
            results["dockerfile"] = self._frontend_dockerfile(app_type, config)
        elif app_type in ("flask", "fastapi"):
            results["dockerfile"] = self._python_dockerfile(app_type, config, multi_stage)
        else:
            results["dockerfile"] = self._node_dockerfile(config)

        # 2. 生成 .dockerignore
        results["dockerignore"] = self._dockerignore(app_type)

        # 3. 生成 docker-compose (可选)
        if with_compose:
            results["compose"] = self._compose_dev(app_type, config, services)
            results["compose_prod"] = self._compose_prod(app_type, config, services)

        return results

    # ------------------------------------------------------------------
    # Dockerfile 模板
    # ------------------------------------------------------------------

    def _python_dockerfile(
        self, app_type: str, config: Dict[str, Any], multi_stage: bool
    ) -> str:
        """生成 Python 应用 Dockerfile。"""
        base = config["base_image"]
        port = config["port"]
        run_cmd = config["run_cmd"]
        run_parts = run_cmd.split()

        if multi_stage:
            # CMD 指令：将 run_cmd 拆成 JSON 数组格式
            cmd_items = ", ".join(f'"{p}"' for p in run_parts)
            return f'''# ==========================================
# Dockerfile for {app_type.upper()} Application
# Generated by Leo Dockerfile Generator
# ==========================================

# Stage 1: Builder - 安装编译依赖
FROM {base} AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime - 精简运行镜像
FROM {base}

WORKDIR /app

# 创建非 root 用户
RUN useradd --create-home --shell /bin/bash appuser

# 从 builder 阶段复制依赖
COPY --from=builder /root/.local /home/appuser/.local

# 复制应用代码
COPY --chown=appuser:appuser . .

# 设置环境变量
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

USER appuser

EXPOSE {port}

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{port}/health || exit 1

CMD [{cmd_items}]
'''
        else:
            return f'''# Dockerfile for {app_type.upper()} Application
FROM {base}

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE {port}

CMD {run_parts}
'''

    def _frontend_dockerfile(self, app_type: str, config: Dict[str, Any]) -> str:
        """生成前端应用 Dockerfile（多阶段构建 + Nginx）。"""
        base = config["base_image"]
        build_image = config.get("build_image", "nginx:alpine")
        port = config["port"]

        return f'''# ==========================================
# Dockerfile for {app_type.upper()} Application
# Multi-stage build with Nginx
# Generated by Leo Dockerfile Generator
# ==========================================

# Stage 1: Build - 编译前端资源
FROM {base} AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Production - Nginx 静态托管
FROM {build_image}

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE {port}

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{port}/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
'''

    def _node_dockerfile(self, config: Dict[str, Any]) -> str:
        """生成 Node.js 应用 Dockerfile。"""
        base = config["base_image"]
        port = config["port"]

        return f'''# Dockerfile for Node.js Application
# Generated by Leo Dockerfile Generator
FROM {base}

WORKDIR /app

# 创建非 root 用户
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001

COPY package*.json ./
RUN npm ci --only=production

COPY --chown=nodejs:nodejs . .

USER nodejs

EXPOSE {port}

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{port}/health || exit 1

CMD ["node", "server.js"]
'''

    # ------------------------------------------------------------------
    # .dockerignore
    # ------------------------------------------------------------------

    def _dockerignore(self, app_type: str) -> str:
        """生成 .dockerignore 文件。"""
        common = """# Git
.git
.gitignore

# IDE
.idea
.vscode
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Docker
Dockerfile*
docker-compose*
.docker

# Documentation
README.md
docs/
"""

        if app_type in ("flask", "fastapi"):
            return common + """
# Python
__pycache__/
*.py[cod]
*$py.class
.Python
venv/
.venv/
env/
.env
*.egg-info/
.pytest_cache/
.coverage
htmlcov/
"""
        else:
            return common + """
# Node
node_modules/
npm-debug.log
yarn-error.log
.npm
.yarn

# Build
dist/
build/
.next/
.nuxt/

# Environment
.env
.env.local
.env.*.local
"""

    # ------------------------------------------------------------------
    # docker-compose 开发环境
    # ------------------------------------------------------------------

    def _compose_dev(
        self, app_type: str, config: Dict[str, Any], services: List[str]
    ) -> str:
        """生成开发环境 docker-compose.yml。"""
        port = config["port"]

        compose = f'''# docker-compose.yml
# Development environment
# Generated by Leo Dockerfile Generator

version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "{port}:{port}"
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
      - FLASK_ENV=development
      - DATABASE_URL=mysql://root:password@db:3306/app
      - REDIS_URL=redis://cache:6379/0
    depends_on:
      - db
      - cache
    restart: unless-stopped
'''

        if "mysql" in services or "db" in services:
            compose += '''
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: app
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    restart: unless-stopped
'''

        if "redis" in services or "cache" in services:
            compose += '''
  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
'''

        if "nginx" in services or "proxy" in services:
            compose += '''
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - app
    restart: unless-stopped
'''

        compose += '''
volumes:
  mysql_data:
  redis_data:

networks:
  default:
    name: app_network
'''

        return compose

    # ------------------------------------------------------------------
    # docker-compose 生产环境
    # ------------------------------------------------------------------

    def _compose_prod(
        self, app_type: str, config: Dict[str, Any], services: List[str]
    ) -> str:
        """生成生产环境 docker-compose.prod.yml。"""
        return f'''# docker-compose.prod.yml
# Production environment
# Usage: docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    environment:
      - NODE_ENV=production
      - FLASK_ENV=production
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  db:
    environment:
      MYSQL_ROOT_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    deploy:
      resources:
        limits:
          memory: 1G

  cache:
    deploy:
      resources:
        limits:
          memory: 256M

secrets:
  db_password:
    file: ./secrets/db_password.txt
'''

    # ------------------------------------------------------------------
    # 文件保存
    # ------------------------------------------------------------------

    def save_files(self, results: Dict[str, str]) -> Dict[str, Path]:
        """将生成的配置保存到磁盘。

        Returns:
            key -> 保存路径 的字典
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)

        file_mapping = {
            "dockerfile": "Dockerfile",
            "dockerignore": ".dockerignore",
            "compose": "docker-compose.yml",
            "compose_prod": "docker-compose.prod.yml",
        }

        saved: Dict[str, Path] = {}
        for key, filename in file_mapping.items():
            if key in results:
                file_path = self.output_dir / filename
                file_path.write_text(results[key], encoding="utf-8")
                saved[key] = file_path

        return saved


__all__ = ["DockerfileGenerator"]
