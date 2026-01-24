# 全栈项目脚手架 Skill

## 技能描述

一键生成完整的全栈项目结构，包含前后端代码、Docker配置、文档等。

## 激活词

- "创建项目"
- "生成项目结构"
- "项目脚手架"

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_name | string | 是 | 项目名称 |
| template | string | 否 | 项目模板（flask-vue/flask-miniprogram/fastapi-react） |
| features | list | 否 | 额外特性 |

## 支持的模板

| 模板 | 后端 | 前端 | 数据库 |
|------|------|------|--------|
| flask-vue | Flask | Vue3 | MySQL |
| flask-miniprogram | Flask | 微信小程序 | MySQL |
| fastapi-react | FastAPI | React | PostgreSQL |

## 输出

完整的项目结构：
```
project/
├── backend/
│   ├── app/
│   ├── config.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── package.json
├── docker-compose.yml
├── .gitignore
├── .env.example
└── README.md
```

## 使用示例

```
创建项目
项目名：裂变小程序
模板：flask-miniprogram
```

## 版本

- 版本: 1.0.0
- 作者: Leo Liu
- 更新: 2026-01-14
