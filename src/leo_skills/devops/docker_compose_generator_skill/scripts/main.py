"""
Docker Compose配置生成器 Skill
============================
生成docker-compose配置文件
"""

from pathlib import Path
from typing import Dict, List, Optional
import yaml


class DockerComposeGenerator:
    """Docker Compose配置生成器"""

    def __init__(self, output_dir: str = "."):
        self.output_dir = Path(output_dir)

    def generate(
        self,
        services: List[Dict],
        networks: List[str] = None,
        volumes: List[str] = None,
        project_name: str = "app"
    ) -> Dict[str, str]:
        """
        生成docker-compose配置

        Args:
            services: 服务列表
            networks: 网络列表
            volumes: 卷列表
            project_name: 项目名称

        Returns:
            生成的配置字典
        """
        networks = networks or ['default']
        volumes = volumes or []

        compose = {
            'version': '3.8',
            'services': {},
            'networks': {},
            'volumes': {}
        }

        # 处理服务
        for service in services:
            service_name = service.get('name', 'app')
            compose['services'][service_name] = self._generate_service(service)

        # 处理网络
        for network in networks:
            compose['networks'][network] = {'driver': 'bridge'}

        # 处理卷
        for volume in volumes:
            compose['volumes'][volume] = {}

        # 生成YAML
        yaml_content = self._to_yaml(compose)

        # 生成.env示例
        env_content = self._generate_env_example(services)

        return {
            'docker_compose': yaml_content,
            'env_example': env_content
        }

    def _generate_service(self, service: Dict) -> Dict:
        """生成单个服务配置"""
        service_type = service.get('type', 'custom')

        if service_type == 'flask':
            return self._generate_flask_service(service)
        elif service_type == 'fastapi':
            return self._generate_fastapi_service(service)
        elif service_type == 'mysql':
            return self._generate_mysql_service(service)
        elif service_type == 'postgres':
            return self._generate_postgres_service(service)
        elif service_type == 'redis':
            return self._generate_redis_service(service)
        elif service_type == 'nginx':
            return self._generate_nginx_service(service)
        elif service_type == 'node':
            return self._generate_node_service(service)
        else:
            return self._generate_custom_service(service)

    def _generate_flask_service(self, service: Dict) -> Dict:
        """生成Flask服务配置"""
        name = service.get('name', 'flask')
        port = service.get('port', 5000)

        return {
            'build': {
                'context': service.get('context', './backend'),
                'dockerfile': service.get('dockerfile', 'Dockerfile')
            },
            'container_name': f'{name}-container',
            'ports': [f'{port}:{port}'],
            'environment': [
                'FLASK_ENV=${FLASK_ENV:-development}',
                'DATABASE_URL=${DATABASE_URL}',
                'SECRET_KEY=${SECRET_KEY}'
            ],
            'volumes': [
                f'{service.get("context", "./backend")}:/app'
            ],
            'depends_on': service.get('depends_on', []),
            'networks': service.get('networks', ['default']),
            'restart': 'unless-stopped'
        }

    def _generate_fastapi_service(self, service: Dict) -> Dict:
        """生成FastAPI服务配置"""
        name = service.get('name', 'fastapi')
        port = service.get('port', 8000)

        return {
            'build': {
                'context': service.get('context', './backend'),
                'dockerfile': service.get('dockerfile', 'Dockerfile')
            },
            'container_name': f'{name}-container',
            'ports': [f'{port}:{port}'],
            'environment': [
                'DATABASE_URL=${DATABASE_URL}',
                'SECRET_KEY=${SECRET_KEY}'
            ],
            'command': 'uvicorn main:app --host 0.0.0.0 --port 8000 --reload',
            'volumes': [
                f'{service.get("context", "./backend")}:/app'
            ],
            'depends_on': service.get('depends_on', []),
            'networks': service.get('networks', ['default']),
            'restart': 'unless-stopped'
        }

    def _generate_mysql_service(self, service: Dict) -> Dict:
        """生成MySQL服务配置"""
        name = service.get('name', 'mysql')

        return {
            'image': service.get('image', 'mysql:8.0'),
            'container_name': f'{name}-container',
            'ports': ['3306:3306'],
            'environment': [
                'MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}',
                'MYSQL_DATABASE=${MYSQL_DATABASE}',
                'MYSQL_USER=${MYSQL_USER}',
                'MYSQL_PASSWORD=${MYSQL_PASSWORD}'
            ],
            'volumes': [
                f'{name}_data:/var/lib/mysql'
            ],
            'networks': service.get('networks', ['default']),
            'restart': 'unless-stopped',
            'healthcheck': {
                'test': ['CMD', 'mysqladmin', 'ping', '-h', 'localhost'],
                'interval': '10s',
                'timeout': '5s',
                'retries': 5
            }
        }

    def _generate_postgres_service(self, service: Dict) -> Dict:
        """生成PostgreSQL服务配置"""
        name = service.get('name', 'postgres')

        return {
            'image': service.get('image', 'postgres:15'),
            'container_name': f'{name}-container',
            'ports': ['5432:5432'],
            'environment': [
                'POSTGRES_USER=${POSTGRES_USER}',
                'POSTGRES_PASSWORD=${POSTGRES_PASSWORD}',
                'POSTGRES_DB=${POSTGRES_DB}'
            ],
            'volumes': [
                f'{name}_data:/var/lib/postgresql/data'
            ],
            'networks': service.get('networks', ['default']),
            'restart': 'unless-stopped',
            'healthcheck': {
                'test': ['CMD-SHELL', 'pg_isready -U ${POSTGRES_USER}'],
                'interval': '10s',
                'timeout': '5s',
                'retries': 5
            }
        }

    def _generate_redis_service(self, service: Dict) -> Dict:
        """生成Redis服务配置"""
        name = service.get('name', 'redis')

        return {
            'image': service.get('image', 'redis:7-alpine'),
            'container_name': f'{name}-container',
            'ports': ['6379:6379'],
            'volumes': [
                f'{name}_data:/data'
            ],
            'networks': service.get('networks', ['default']),
            'restart': 'unless-stopped',
            'healthcheck': {
                'test': ['CMD', 'redis-cli', 'ping'],
                'interval': '10s',
                'timeout': '5s',
                'retries': 5
            }
        }

    def _generate_nginx_service(self, service: Dict) -> Dict:
        """生成Nginx服务配置"""
        name = service.get('name', 'nginx')

        return {
            'image': service.get('image', 'nginx:alpine'),
            'container_name': f'{name}-container',
            'ports': ['80:80', '443:443'],
            'volumes': [
                './nginx/nginx.conf:/etc/nginx/nginx.conf:ro',
                './nginx/conf.d:/etc/nginx/conf.d:ro'
            ],
            'depends_on': service.get('depends_on', []),
            'networks': service.get('networks', ['default']),
            'restart': 'unless-stopped'
        }

    def _generate_node_service(self, service: Dict) -> Dict:
        """生成Node.js服务配置"""
        name = service.get('name', 'node')
        port = service.get('port', 3000)

        return {
            'build': {
                'context': service.get('context', './frontend'),
                'dockerfile': service.get('dockerfile', 'Dockerfile')
            },
            'container_name': f'{name}-container',
            'ports': [f'{port}:{port}'],
            'environment': [
                f'PORT={port}',
                'NODE_ENV=${NODE_ENV:-development}'
            ],
            'volumes': [
                f'{service.get("context", "./frontend")}:/app',
                '/app/node_modules'
            ],
            'networks': service.get('networks', ['default']),
            'restart': 'unless-stopped'
        }

    def _generate_custom_service(self, service: Dict) -> Dict:
        """生成自定义服务配置"""
        config = {}

        if 'image' in service:
            config['image'] = service['image']
        elif 'build' in service:
            config['build'] = service['build']
        else:
            config['build'] = '.'

        if 'ports' in service:
            config['ports'] = service['ports']

        if 'environment' in service:
            config['environment'] = service['environment']

        if 'volumes' in service:
            config['volumes'] = service['volumes']

        if 'depends_on' in service:
            config['depends_on'] = service['depends_on']

        config['networks'] = service.get('networks', ['default'])
        config['restart'] = service.get('restart', 'unless-stopped')

        return config

    def _to_yaml(self, data: Dict) -> str:
        """转换为YAML格式"""
        # 自定义YAML格式，更易读
        return yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def _generate_env_example(self, services: List[Dict]) -> str:
        """生成.env示例文件"""
        env_vars = [
            '# Docker Compose Environment Variables',
            '# Generated by Leo Docker Compose Generator',
            ''
        ]

        for service in services:
            service_type = service.get('type', 'custom')
            service_name = service.get('name', 'app').upper()

            env_vars.append(f'# {service_name} Configuration')

            if service_type == 'flask':
                env_vars.extend([
                    'FLASK_ENV=development',
                    'SECRET_KEY=your-secret-key',
                    'DATABASE_URL=mysql+pymysql://user:password@mysql/dbname',
                    ''
                ])
            elif service_type == 'fastapi':
                env_vars.extend([
                    'SECRET_KEY=your-secret-key',
                    'DATABASE_URL=postgresql://user:password@postgres/dbname',
                    ''
                ])
            elif service_type == 'mysql':
                env_vars.extend([
                    'MYSQL_ROOT_PASSWORD=rootpassword',
                    'MYSQL_DATABASE=mydb',
                    'MYSQL_USER=user',
                    'MYSQL_PASSWORD=password',
                    ''
                ])
            elif service_type == 'postgres':
                env_vars.extend([
                    'POSTGRES_USER=user',
                    'POSTGRES_PASSWORD=password',
                    'POSTGRES_DB=mydb',
                    ''
                ])
            elif service_type == 'node':
                env_vars.extend([
                    'NODE_ENV=development',
                    ''
                ])

        return '\n'.join(env_vars)

    def generate_preset(self, preset: str) -> Dict[str, str]:
        """生成预设配置"""
        presets = {
            'flask-mysql': [
                {'name': 'flask', 'type': 'flask', 'port': 5000, 'depends_on': ['mysql']},
                {'name': 'mysql', 'type': 'mysql'}
            ],
            'flask-postgres-redis': [
                {'name': 'flask', 'type': 'flask', 'port': 5000, 'depends_on': ['postgres', 'redis']},
                {'name': 'postgres', 'type': 'postgres'},
                {'name': 'redis', 'type': 'redis'}
            ],
            'fastapi-postgres': [
                {'name': 'fastapi', 'type': 'fastapi', 'port': 8000, 'depends_on': ['postgres']},
                {'name': 'postgres', 'type': 'postgres'}
            ],
            'fullstack': [
                {'name': 'nginx', 'type': 'nginx', 'depends_on': ['flask', 'node']},
                {'name': 'flask', 'type': 'flask', 'port': 5000, 'depends_on': ['mysql', 'redis']},
                {'name': 'node', 'type': 'node', 'port': 3000},
                {'name': 'mysql', 'type': 'mysql'},
                {'name': 'redis', 'type': 'redis'}
            ]
        }

        services = presets.get(preset, presets['flask-mysql'])
        volumes = [s['name'] + '_data' for s in services if s['type'] in ['mysql', 'postgres', 'redis']]

        return self.generate(services=services, volumes=volumes)


def main():
    """示例用法"""
    generator = DockerComposeGenerator(output_dir="./output")

    # 使用预设
    results = generator.generate_preset('flask-mysql')

    print("=== docker-compose.yml ===")
    print(results['docker_compose'])
    print("\n=== .env.example ===")
    print(results['env_example'])


if __name__ == '__main__':
    main()
