# Leo AI System - Web UI v2

现代化的 React + TypeScript + Tailwind CSS 前端界面，替代原有的 Streamlit 应用。

## 功能特性

- **仪表盘**: 系统概览、统计数据、快速操作
- **Skills 管理**: 创建、编辑、查看技能
- **Agents 管理**: 配置和管理智能代理
- **Workflows 管理**: YAML 工作流编辑器和可视化
- **共享记忆**: 持久化记忆管理界面
- **意图调试**: 测试意图识别引擎
- **技能进化**: 技能改进任务管理
- **系统设置**: 配置和系统维护

## 技术栈

- **前端**: React 18 + TypeScript
- **构建工具**: Vite 5
- **样式**: Tailwind CSS
- **状态管理**: Zustand
- **HTTP 客户端**: Axios
- **图标**: Lucide React
- **后端**: FastAPI (Python)

## 快速开始

### 1. 安装依赖

```bash
# 前端依赖
cd src/leo_interface/web_v2
npm install

# 后端依赖 (在项目根目录)
pip install fastapi uvicorn
```

### 2. 启动开发服务器

```bash
# 启动前端 (端口 5173)
npm run dev

# 启动后端 API (端口 8000)
python api/main.py
```

### 3. 构建生产版本

```bash
npm run build
```

## 项目结构

```
src/leo_interface/web_v2/
├── api/                    # FastAPI 后端
│   └── main.py            # API 路由
├── src/
│   ├── components/        # React 组件
│   │   ├── Layout.tsx    # 布局组件
│   │   ├── Sidebar.tsx   # 侧边导航
│   │   └── Header.tsx    # 顶部导航
│   ├── pages/            # 页面组件
│   │   ├── Dashboard.tsx
│   │   ├── Skills.tsx
│   │   ├── Agents.tsx
│   │   ├── Workflows.tsx
│   │   ├── Memory.tsx
│   │   ├── Intent.tsx
│   │   ├── Evolution.tsx
│   │   └── Settings.tsx
│   ├── services/         # API 服务
│   │   └── api.ts
│   ├── store/           # 状态管理
│   │   └── appStore.ts
│   ├── types/           # TypeScript 类型
│   │   └── index.ts
│   ├── utils/           # 工具函数
│   │   └── cn.ts
│   ├── App.tsx          # 主应用
│   ├── main.tsx         # 入口
│   └── index.css        # 全局样式
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## API 端点

所有 API 端点前缀为 `/api`:

- `GET/POST /skills` - Skills 管理
- `GET/POST /agents` - Agents 管理
- `GET/POST /workflows` - Workflows 管理
- `GET/POST /memory` - 共享记忆
- `POST /intent/recognize` - 意图识别
- `GET /system/stats` - 系统统计

## 开发计划

### 已实现
- [x] 项目结构和配置
- [x] 导航栏组件
- [x] Dashboard 首页
- [x] Skills 管理页面
- [x] Agents 管理页面
- [x] Workflows 管理页面
- [x] 共享记忆页面
- [x] 意图识别调试页面
- [x] 后端 API 路由 (Mock 数据)

### 待开发
- [ ] 连接真实后端数据
- [ ] 工作流可视化编辑器
- [ ] 实时日志和监控
- [ ] 用户认证
- [ ] 部署脚本

## 许可证

MIT
