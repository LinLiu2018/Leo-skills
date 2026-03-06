# 天使虫AI操盘手系统

> 全链路AI数字员工操作系统 - 对标新榜矩阵通的专业级自媒体矩阵管理工具

## 项目概述

天使虫AI操盘手系统是一个集AI内容生成、全平台自动化运营、私域流量管理于一体的超级AI员工系统。

### 核心功能

1. **AI内容创作** - 文生视频、图生视频、数字人口播、智能混剪
2. **账号矩阵管理** - 抖音/快手/视频号/小红书/微信多平台统一管理
3. **智能发布** - 定时发布、矩阵分发、失败重试
4. **自动化运营** - 智能养号、评论截流、自动获客
5. **私域管理** - 微信自动化、朋友圈运营、AI客服
6. **AI指令控制台** - 自然语言操作，一键完成复杂任务
7. **数据分析** - 多维度数据报表、内容排行、趋势分析

## 技术架构

### 前端
- **框架**: Electron 28+ + React 19+ + TypeScript
- **UI组件库**: Ant Design 5.x
- **状态管理**: Zustand
- **图表**: AntV/G2Plot
- **路由**: React Router v7

### 后端
- **框架**: Python 3.10+ + FastAPI
- **数据库**: MySQL 8.0 + ChromaDB (向量库)
- **缓存**: Redis
- **任务队列**: Celery
- **ORM**: SQLAlchemy 2.0

## 项目结构

```
angel-worm-ai/
├── frontend/              # 前端项目
│   ├── electron/         # Electron主进程
│   │   ├── main.ts       # 主进程入口
│   │   └── preload.ts    # 预加载脚本
│   ├── src/
│   │   ├── components/   # 公共组件
│   │   ├── layouts/      # 布局组件
│   │   ├── pages/        # 页面组件
│   │   ├── stores/       # 状态管理
│   │   ├── hooks/        # 自定义Hooks
│   │   └── utils/        # 工具函数
│   ├── package.json
│   └── vite.config.ts
│
├── backend/               # 后端项目
│   ├── app/
│   │   ├── api/          # API路由
│   │   ├── core/         # 核心配置
│   │   ├── db/           # 数据库
│   │   ├── models/       # ORM模型
│   │   ├── schemas/      # 数据模型
│   │   ├── services/     # 业务服务
│   │   └── utils/        # 工具函数
│   ├── tests/            # 测试
│   ├── requirements.txt
│   └── main.py
│
└── README.md
```

## 快速开始

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

### 后端启动

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## 界面展示

系统采用新榜矩阵通的专业级界面风格：

- **整体布局**: 左侧固定导航栏 + 右侧可滚动工作区
- **配色方案**: 深色/浅色双主题，主色调蓝色系
- **数据展示**: 卡片式布局、图表可视化
- **交互特点**: 实时数据刷新、拖拽操作、批量管理

## 开发计划

- [x] Phase 1: 项目初始化与架构设计
- [x] Phase 2: 前端核心界面实现（矩阵通风格）
- [x] Phase 3: 后端API服务搭建
- [ ] Phase 4: AI模块集成（视频生成、数字人）
- [ ] Phase 5: 自动化引擎实现
- [ ] Phase 6: 测试优化与打包发布

## 技术选型理由

| 技术 | 选型 | 理由 |
|------|------|------|
| 前端框架 | Electron + React | 跨平台桌面应用，成熟生态 |
| UI组件库 | Ant Design | 企业级组件库，专业美观 |
| 后端框架 | FastAPI | 高性能异步，自动生成文档 |
| 数据库 | MySQL + ChromaDB | 结构化数据 + 向量检索 |
| AI能力 | 多API聚合 | Sora2/可灵/DeepSeek等 |

## 安全与风控

- 设备指纹模拟
- IP代理池轮换
- 操作行为随机化
- 敏感操作二次确认
- 风控预警机制

## 许可

Copyright © 2026 天使虫AI. All rights reserved.
