# WebChat 网页聊天配置指南

**创建时间**: 2026-02-27  
**状态**: ⏳ 配置框架已创建

---

## 一、WebChat 功能说明

### 核心功能

| 功能 | 说明 | 状态 |
|------|------|------|
| 网页聊天界面 | 浏览器访问的聊天 UI | ⏳ 待部署 |
| 消息收发 | 实时消息传递 | ⏳ 待实现 |
| 历史记录 | 查看聊天历史 | ⏳ 待实现 |
| 文件上传 | 上传图片/文档 | ⏳ 待实现 |

---

## 二、实施方案

### 方案 1: OpenClaw 官方 WebChat (推荐)

**部署步骤**:

```bash
# 1. 启用 WebChat
openclaw config set webchat.enabled true

# 2. 配置端口
openclaw config set webchat.port 18790

# 3. 启动 WebChat
openclaw webchat start

# 4. 访问
# http://localhost:18790
```

### 方案 2: 自定义 WebChat

**技术栈**:
- 前端：React + WebSocket
- 后端：OpenClaw Gateway API
- 部署：Docker / 本地

**文件结构**:
```
webchat/
├── public/
│   └── index.html
├── src/
│   ├── App.jsx
│   ├── ChatWindow.jsx
│   └── api.js
├── package.json
└── Dockerfile
```

---

## 三、配置示例

### openclaw.json

```json
{
  "webchat": {
    "enabled": true,
    "port": 18790,
    "host": "0.0.0.0",
    "auth": {
      "enabled": true,
      "type": "token"
    },
    "cors": {
      "enabled": true,
      "origins": ["*"]
    }
  }
}
```

---

## 四、验收标准

- [ ] WebChat 界面可访问
- [ ] 消息收发正常
- [ ] 历史记录可查看
- [ ] 支持文件上传

---

## 五、访问地址

**本地**: http://localhost:18790  
**生产**: 待部署后配置

---

*配置完成时间：待实施*
