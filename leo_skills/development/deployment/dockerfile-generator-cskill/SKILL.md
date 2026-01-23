# Dockerfile 生成器 Skill

## 技能描述

自动生成优化的Dockerfile和docker-compose配置，支持多种应用类型和部署场景。

## 激活词

- "生成Dockerfile"
- "创建Docker配置"
- "docker部署"
- "容器化"

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| app_type | string | 是 | 应用类型（flask/fastapi/node/vue/react） |
| runtime | string | 否 | 运行时版本（如python:3.9） |
| port | int | 否 | 暴露端口，默认根据应用类型 |
| multi_stage | bool | 否 | 是否使用多阶段构建，默认true |
| with_compose | bool | 否 | 是否生成docker-compose，默认true |
| services | list | 否 | 额外服务（mysql/redis/nginx） |

## 输出

- `Dockerfile` - Docker镜像构建文件
- `.dockerignore` - Docker忽略文件
- `docker-compose.yml` - 编排配置（可选）
- `docker-compose.prod.yml` - 生产环境配置（可选）

## 使用示例

### 示例1：Flask应用

```
生成Dockerfile，应用类型：flask
运行时：python:3.9-slim
端口：5000
额外服务：mysql, redis
```

### 示例2：Vue前端应用

```
生成Dockerfile，应用类型：vue
使用多阶段构建
生产环境使用nginx
```

### 示例3：全栈应用

```
生成docker-compose配置
服务：
- frontend: vue应用
- backend: flask应用
- db: mysql
- cache: redis
- proxy: nginx
```

## 支持的应用类型

| 类型 | 基础镜像 | 默认端口 |
|------|----------|----------|
| flask | python:3.9-slim | 5000 |
| fastapi | python:3.9-slim | 8000 |
| node | node:18-alpine | 3000 |
| vue | node:18-alpine + nginx | 80 |
| react | node:18-alpine + nginx | 80 |

## 最佳实践

生成的Dockerfile遵循以下最佳实践：
- 多阶段构建减小镜像体积
- 非root用户运行
- 健康检查配置
- 合理的层缓存策略
- 安全扫描友好

## 版本

- 版本: 1.0.0
- 作者: Leo Liu
- 更新: 2026-01-12
