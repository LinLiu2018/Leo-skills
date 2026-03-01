"""
全栈项目脚手架技能

一键生成完整的全栈项目结构，支持 Flask+Vue3、Flask+小程序、FastAPI+React 等模板。
包含后端、前端、Docker Compose、README、.gitignore 等完整文件。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from leo_skills.core.base_executor import BaseExecutor


class FullstackScaffold(BaseExecutor):
    """全栈项目脚手架生成器。

    支持的操作：
        - generate: 生成项目结构（返回文件名→内容的字典）
        - save:     生成并写入磁盘
    """

    # 预置项目模板
    TEMPLATES: Dict[str, Dict[str, str]] = {
        "flask-vue": {
            "backend": "flask",
            "frontend": "vue3",
            "database": "mysql",
        },
        "flask-miniprogram": {
            "backend": "flask",
            "frontend": "miniprogram",
            "database": "mysql",
        },
        "fastapi-react": {
            "backend": "fastapi",
            "frontend": "react",
            "database": "postgresql",
        },
    }

    def __init__(self) -> None:
        self.name = "fullstack_project_scaffold_skill"

    # ------------------------------------------------------------------ #
    #  BaseExecutor 接口
    # ------------------------------------------------------------------ #

    def execute(
        self,
        action: str = "generate",
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(context or {})
        params.update(kwargs)

        if action in ("generate", "run"):
            return self._action_generate(params)
        elif action == "save":
            return self._action_save(params)
        else:
            return {"status": "error", "message": f"未知操作: {action}"}

    # ------------------------------------------------------------------ #
    #  动作方法
    # ------------------------------------------------------------------ #

    def _action_generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        project_name = params.get("project_name", "MyProject")
        template = params.get("template", "flask-vue")
        features: List[str] = params.get("features", [])

        files = self.generate(project_name, template, features)
        return {
            "status": "success",
            "action": "generate",
            "project_name": project_name,
            "template": template,
            "files": list(files.keys()),
            "data": files,
        }

    def _action_save(self, params: Dict[str, Any]) -> Dict[str, Any]:
        project_name = params.get("project_name", "MyProject")
        template = params.get("template", "flask-vue")
        features: List[str] = params.get("features", [])
        output_dir = params.get("output_dir", ".")

        files = self.generate(project_name, template, features)
        saved = self.save_files(project_name, files, output_dir)
        return {
            "status": "success",
            "action": "save",
            "project_name": project_name,
            "files_saved": len(saved),
            "paths": {k: str(v) for k, v in saved.items()},
        }

    # ------------------------------------------------------------------ #
    #  核心生成逻辑
    # ------------------------------------------------------------------ #

    def generate(
        self,
        project_name: str,
        template: str = "flask-vue",
        features: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """生成全栈项目结构。"""
        features = features or []
        config = self.TEMPLATES.get(template, self.TEMPLATES["flask-vue"])
        results: Dict[str, str] = {}

        # 后端
        results.update(self._gen_backend(project_name, config["backend"]))
        # 前端
        results.update(self._gen_frontend(project_name, config["frontend"]))
        # Docker
        results["docker-compose.yml"] = self._gen_docker_compose(project_name, config)
        # 项目文件
        results["README.md"] = self._gen_readme(project_name, config, features)
        results[".gitignore"] = self._gen_gitignore()
        results[".env.example"] = self._gen_env_example()

        return results

    def save_files(
        self,
        project_name: str,
        files: Dict[str, str],
        output_dir: str = ".",
    ) -> Dict[str, Path]:
        saved: Dict[str, Path] = {}
        project_dir = Path(output_dir) / project_name
        for file_path, content in files.items():
            full_path = project_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
            saved[file_path] = full_path
        return saved

    # ------------------------------------------------------------------ #
    #  后端模板
    # ------------------------------------------------------------------ #

    def _gen_backend(self, project_name: str, framework: str) -> Dict[str, str]:
        results: Dict[str, str] = {}

        if framework == "flask":
            results["backend/app/__init__.py"] = f'''"""
{project_name} Backend
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config

db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    CORS(app)

    # 注册蓝图
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
'''
            results["backend/app/api/__init__.py"] = (
                "from flask import Blueprint\n\n"
                "bp = Blueprint('api', __name__)\n\n"
                "from app.api import routes\n"
            )
            results["backend/app/api/routes.py"] = (
                "from flask import jsonify\n"
                "from app.api import bp\n\n\n"
                "@bp.route('/health')\n"
                "def health():\n"
                "    return jsonify({'status': 'ok'})\n"
            )
            results["backend/app/models/__init__.py"] = "# Models\n"
            results["backend/config.py"] = (
                "import os\n\n\n"
                "class Config:\n"
                "    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'\n"
                "    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'\n"
                "    SQLALCHEMY_TRACK_MODIFICATIONS = False\n"
            )
            results["backend/requirements.txt"] = (
                "flask==3.0.0\nflask-sqlalchemy==3.1.1\nflask-cors==4.0.0\n"
                "flask-migrate==4.0.5\ngunicorn==21.2.0\npython-dotenv==1.0.0\n"
                "marshmallow==3.20.1\n"
            )
            results["backend/run.py"] = (
                "from app import create_app, db\n\n"
                "app = create_app()\n\n"
                "if __name__ == '__main__':\n"
                "    app.run(debug=True)\n"
            )

        elif framework == "fastapi":
            results["backend/app/__init__.py"] = ""
            results["backend/app/main.py"] = f'''"""
{project_name} FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="{project_name}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {{"status": "ok"}}
'''
            results["backend/requirements.txt"] = (
                "fastapi>=0.100.0\nuvicorn>=0.23.0\nsqlalchemy>=2.0.0\n"
                "alembic>=1.12.0\npython-dotenv>=1.0.0\n"
            )

        return results

    # ------------------------------------------------------------------ #
    #  前端模板
    # ------------------------------------------------------------------ #

    def _gen_frontend(self, project_name: str, framework: str) -> Dict[str, str]:
        results: Dict[str, str] = {}

        if framework == "vue3":
            results["frontend/package.json"] = json.dumps(
                {
                    "name": project_name.lower().replace(" ", "-"),
                    "version": "0.1.0",
                    "private": True,
                    "scripts": {
                        "dev": "vite",
                        "build": "vite build",
                        "preview": "vite preview",
                    },
                    "dependencies": {
                        "vue": "^3.4.0",
                        "vue-router": "^4.2.0",
                        "pinia": "^2.1.0",
                        "axios": "^1.6.0",
                    },
                    "devDependencies": {
                        "@vitejs/plugin-vue": "^5.0.0",
                        "vite": "^5.0.0",
                        "typescript": "^5.3.0",
                    },
                },
                indent=2,
                ensure_ascii=False,
            )
            results["frontend/vite.config.ts"] = (
                "import { defineConfig } from 'vite'\n"
                "import vue from '@vitejs/plugin-vue'\n\n"
                "export default defineConfig({\n"
                "  plugins: [vue()],\n"
                "  server: {\n"
                "    proxy: {\n"
                "      '/api': {\n"
                "        target: 'http://localhost:5000',\n"
                "        changeOrigin: true\n"
                "      }\n"
                "    }\n"
                "  }\n"
                "})\n"
            )
            results["frontend/src/main.ts"] = (
                "import { createApp } from 'vue'\n"
                "import { createPinia } from 'pinia'\n"
                "import router from './router'\n"
                "import App from './App.vue'\n\n"
                "const app = createApp(App)\n"
                "app.use(createPinia())\n"
                "app.use(router)\n"
                "app.mount('#app')\n"
            )
            results["frontend/src/App.vue"] = (
                "<template>\n  <router-view />\n</template>\n\n"
                '<script setup lang="ts">\n// App setup\n</script>\n'
            )
            results["frontend/src/router/index.ts"] = (
                "import { createRouter, createWebHistory } from 'vue-router'\n\n"
                "const router = createRouter({\n"
                "  history: createWebHistory(),\n"
                "  routes: [\n"
                "    {\n"
                "      path: '/',\n"
                "      name: 'home',\n"
                "      component: () => import('../views/Home.vue')\n"
                "    }\n"
                "  ]\n"
                "})\n\n"
                "export default router\n"
            )
            results["frontend/src/views/Home.vue"] = (
                "<template>\n"
                f'  <div class="home">\n    <h1>Welcome to {project_name}</h1>\n  </div>\n'
                "</template>\n\n"
                '<script setup lang="ts">\n// Home page\n</script>\n\n'
                "<style scoped>\n.home {\n  text-align: center;\n  padding: 40px;\n}\n</style>\n"
            )
            results["frontend/index.html"] = (
                '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n'
                '  <meta charset="UTF-8">\n'
                '  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
                f"  <title>{project_name}</title>\n</head>\n<body>\n"
                '  <div id="app"></div>\n'
                '  <script type="module" src="/src/main.ts"></script>\n'
                "</body>\n</html>\n"
            )

        elif framework == "miniprogram":
            results["miniprogram/app.json"] = json.dumps(
                {
                    "pages": ["pages/index/index"],
                    "window": {
                        "navigationBarTitleText": project_name,
                        "navigationBarBackgroundColor": "#ffffff",
                    },
                },
                indent=2,
                ensure_ascii=False,
            )
            results["miniprogram/app.js"] = (
                "App({\n"
                "  globalData: {\n"
                "    baseUrl: 'http://localhost:5000/api'\n"
                "  },\n"
                "  onLaunch() {\n"
                f"    console.log('{project_name} launched')\n"
                "  }\n"
                "})\n"
            )
            results["miniprogram/pages/index/index.wxml"] = (
                '<view class="container">\n'
                f'  <text class="title">{project_name}</text>\n'
                "</view>\n"
            )
            results["miniprogram/pages/index/index.js"] = (
                "Page({\n  data: {},\n  onLoad() {}\n})\n"
            )

        elif framework == "react":
            results["frontend/package.json"] = json.dumps(
                {
                    "name": project_name.lower().replace(" ", "-"),
                    "version": "0.1.0",
                    "private": True,
                    "scripts": {
                        "dev": "vite",
                        "build": "vite build",
                    },
                    "dependencies": {
                        "react": "^18.2.0",
                        "react-dom": "^18.2.0",
                        "react-router-dom": "^6.20.0",
                        "axios": "^1.6.0",
                    },
                    "devDependencies": {
                        "@vitejs/plugin-react": "^4.2.0",
                        "vite": "^5.0.0",
                        "typescript": "^5.3.0",
                    },
                },
                indent=2,
                ensure_ascii=False,
            )

        return results

    # ------------------------------------------------------------------ #
    #  基础设施模板
    # ------------------------------------------------------------------ #

    def _gen_docker_compose(self, project_name: str, config: Dict) -> str:
        svc = project_name.lower().replace(" ", "-")
        return f"""version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=mysql://root:password@db:3306/{svc}
      - FLASK_ENV=development
    depends_on:
      - db
    volumes:
      - ./backend:/app

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: {svc}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  mysql_data:
"""

    def _gen_readme(self, project_name: str, config: Dict, features: List[str]) -> str:
        return f"""# {project_name}

## 技术栈

- 后端: {config['backend'].capitalize()}
- 前端: {config['frontend'].capitalize()}
- 数据库: {config['database'].upper()}

## 快速开始

```bash
# 启动所有服务
docker-compose up -d

# 后端开发
cd backend && pip install -r requirements.txt && flask run

# 前端开发
cd frontend && npm install && npm run dev
```

---
Generated by Leo AI Agent System
"""

    def _gen_gitignore(self) -> str:
        return """# Python
__pycache__/
*.py[cod]
venv/
.env

# Node
node_modules/
dist/

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite
"""

    def _gen_env_example(self) -> str:
        return """# Backend
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=mysql://root:password@localhost:3306/app

# Frontend
VITE_API_URL=http://localhost:5000/api
"""


__all__ = ["FullstackScaffold"]
