# 建华观园小程序 - 快速启动指南

## 项目结构

```
jianhua-miniprogram/
├── miniprogram/          # 小程序前端
│   ├── pages/            # 页面
│   ├── config/           # 配置
│   └── utils/            # 工具
├── server/               # 后端API
│   ├── routes/           # 路由
│   ├── config/           # 配置
│   └── sql/              # 数据库脚本
└── DEPLOYMENT.md         # 详细部署指南
```

## 本地开发

### 1. 启动后端

```bash
cd server
npm install
cp .env.example .env
# 编辑.env填写数据库配置
npm run dev
```

### 2. 初始化数据库

```bash
mysql -u root -p < server/sql/init.sql
```

### 3. 打开小程序

- 使用微信开发者工具打开 `miniprogram` 目录
- 修改 `config/api.js` 中的API地址
- 点击编译运行

## 生产部署

详细步骤请查看 [DEPLOYMENT.md](./DEPLOYMENT.md)

## 核心功能

- ✅ 一键手机号登录
- ✅ 邀请好友裂变
- ✅ 阶梯礼品解锁
- ✅ 预约到访领取
- ✅ 个人中心管理

## 技术栈

- 前端：微信小程序
- 后端：Node.js + Express
- 数据库：MySQL
- 部署：Nginx + PM2

## 联系方式

如有问题，请查看 DEPLOYMENT.md 中的常见问题部分。
