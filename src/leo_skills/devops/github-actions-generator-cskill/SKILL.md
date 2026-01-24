# GitHub Actions生成器 Skill

## 技能描述

生成GitHub Actions CI/CD工作流配置文件。

## 激活词

- "生成GitHub Actions"
- "创建CI/CD"
- "配置自动化部署"

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| workflow_type | string | 是 | 工作流类型（python-ci/node-ci/docker-build/deploy/full） |
| project_name | string | 是 | 项目名称 |
| options | dict | 否 | 额外选项 |

## 输出

- `.github/workflows/ci.yml` - CI工作流
- `.github/workflows/docker.yml` - Docker构建工作流
- `.github/workflows/deploy.yml` - 部署工作流

## 版本

- 版本: 1.0.0
- 作者: Leo Liu
