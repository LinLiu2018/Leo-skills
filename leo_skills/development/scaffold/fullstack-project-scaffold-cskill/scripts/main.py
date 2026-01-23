"""
全栈项目脚手架 Skill
====================
一键生成完整的全栈项目结构
"""

from pathlib import Path
from typing import Dict, Optional, List
import json


class FullstackProjectScaffold:
    """全栈项目脚手架生成器"""

    TEMPLATES = {
        'flask-vue': {
            'backend': 'flask',
            'frontend': 'vue3',
            'database': 'mysql'
        },
        'flask-miniprogram': {
            'backend': 'flask',
            'frontend': 'miniprogram',
            'database': 'mysql'
        },
        'fastapi-react': {
            'backend': 'fastapi',
            'frontend': 'react',
            'database': 'postgresql'
        }
    }

    def __init__(self, output_dir: str = "."):
        self.output_dir = Path(output_dir)

    def generate(
        self,
        project_name: str,
        template: str = "flask-vue",
        features: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        生成全栈项目结构

        Args:
            project_name: 项目名称
            template: 项目模板
            features: 额外特性

        Returns:
            生成的文件字典
        """
        features = features or []
        config = self.TEMPLATES.get(template, self.TEMPLATES['flask-vue'])

        results = {}

        # 后端结构
        results.update(self._generate_backend(project_name, config['backend']))

        # 前端结构
        results.update(self._generate_frontend(project_name, config['frontend']))

        # Docker配置
        results['docker-compose'] = self._generate_docker_compose(
            project_name, config
        )

        # 项目README
        results['readme'] = self._generate_readme(project_name, config, features)

        # .gitignore
        results['gitignore'] = self._generate_gitignore(config)

        # 环境变量模板
        results['env_example'] = self._generate_env_example(config)

        return results

    def _generate_backend(self, project_name: str, framework: str) -> Dict[str, str]:
        """生成后端结构"""
        results = {}

        if framework == 'flask':
            results['backend/app/__init__.py'] = f'''"""
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

            results['backend/app/api/__init__.py'] = '''from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import routes
'''

            results['backend/app/api/routes.py'] = '''from flask import jsonify
from app.api import bp


@bp.route('/health')
def health():
    return jsonify({'status': 'ok'})
'''

            results['backend/app/models/__init__.py'] = '# Models\n'

            results['backend/config.py'] = '''import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
'''

            results['backend/requirements.txt'] = '''flask==3.0.0
flask-sqlalchemy==3.1.1
flask-cors==4.0.0
flask-migrate==4.0.5
gunicorn==21.2.0
python-dotenv==1.0.0
marshmallow==3.20.1
'''

            results['backend/run.py'] = '''from app import create_app, db

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
'''

        return results

    def _generate_frontend(self, project_name: str, framework: str) -> Dict[str, str]:
        """生成前端结构"""
        results = {}

        if framework == 'vue3':
            results['frontend/package.json'] = json.dumps({
                "name": project_name.lower().replace(' ', '-'),
                "version": "0.1.0",
                "private": True,
                "scripts": {
                    "dev": "vite",
                    "build": "vite build",
                    "preview": "vite preview",
                    "test": "vitest"
                },
                "dependencies": {
                    "vue": "^3.4.0",
                    "vue-router": "^4.2.0",
                    "pinia": "^2.1.0",
                    "axios": "^1.6.0"
                },
                "devDependencies": {
                    "@vitejs/plugin-vue": "^5.0.0",
                    "vite": "^5.0.0",
                    "typescript": "^5.3.0",
                    "vitest": "^1.0.0"
                }
            }, indent=2, ensure_ascii=False)

            results['frontend/vite.config.ts'] = '''import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})
'''

            results['frontend/src/main.ts'] = '''import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
'''

            results['frontend/src/App.vue'] = '''<template>
  <router-view />
</template>

<script setup lang="ts">
// App setup
</script>
'''

            results['frontend/src/router/index.ts'] = '''import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/Home.vue')
    }
  ]
})

export default router
'''

            results['frontend/src/views/Home.vue'] = f'''<template>
  <div class="home">
    <h1>Welcome to {project_name}</h1>
  </div>
</template>

<script setup lang="ts">
// Home page
</script>

<style scoped>
.home {{
  text-align: center;
  padding: 40px;
}}
</style>
'''

            results['frontend/index.html'] = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{project_name}</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
'''

        elif framework == 'miniprogram':
            results['miniprogram/app.json'] = json.dumps({
                "pages": ["pages/index/index"],
                "window": {
                    "navigationBarTitleText": project_name,
                    "navigationBarBackgroundColor": "#ffffff"
                }
            }, indent=2, ensure_ascii=False)

            results['miniprogram/app.js'] = f'''App({{
  globalData: {{
    baseUrl: 'http://localhost:5000/api'
  }},
  onLaunch() {{
    console.log('{project_name} launched')
  }}
}})
'''

            results['miniprogram/pages/index/index.wxml'] = f'''<view class="container">
  <text class="title">{project_name}</text>
</view>
'''

            results['miniprogram/pages/index/index.js'] = '''Page({
  data: {},
  onLoad() {}
})
'''

        return results

    def _generate_docker_compose(self, project_name: str, config: Dict) -> str:
        """生成docker-compose配置"""
        service_name = project_name.lower().replace(' ', '-')

        return f'''version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=mysql://root:password@db:3306/{service_name}
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
      MYSQL_DATABASE: {service_name}
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
'''

    def _generate_readme(
        self,
        project_name: str,
        config: Dict,
        features: List[str]
    ) -> str:
        """生成README"""
        return f'''# {project_name}

## 技术栈

- 后端: {config['backend'].capitalize()}
- 前端: {config['frontend'].capitalize()}
- 数据库: {config['database'].upper()}

## 快速开始

### 开发环境

```bash
# 启动所有服务
docker-compose up -d

# 后端开发
cd backend
pip install -r requirements.txt
flask run

# 前端开发
cd frontend
npm install
npm run dev
```

### 生产部署

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 项目结构

```
{project_name}/
├── backend/          # 后端代码
│   ├── app/
│   ├── config.py
│   └── requirements.txt
├── frontend/         # 前端代码
│   ├── src/
│   └── package.json
├── docker-compose.yml
└── README.md
```

---
Generated by Leo AI Agent System
'''

    def _generate_gitignore(self, config: Dict) -> str:
        """生成.gitignore"""
        return '''# Python
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
'''

    def _generate_env_example(self, config: Dict) -> str:
        """生成环境变量模板"""
        return '''# Backend
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=mysql://root:password@localhost:3306/app

# Frontend
VITE_API_URL=http://localhost:5000/api
'''

    def save_files(self, project_name: str, results: Dict[str, str]) -> Dict[str, Path]:
        """保存生成的文件"""
        saved = {}
        project_dir = self.output_dir / project_name

        for file_path, content in results.items():
            full_path = project_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
            saved[file_path] = full_path

        return saved


def main():
    """示例用法"""
    generator = FullstackProjectScaffold(output_dir="./output")

    results = generator.generate(
        project_name="MyProject",
        template="flask-vue",
        features=["auth", "docker"]
    )

    saved = generator.save_files("MyProject", results)
    print("生成完成！")
    print(f"共生成 {len(saved)} 个文件")


if __name__ == '__main__':
    main()
