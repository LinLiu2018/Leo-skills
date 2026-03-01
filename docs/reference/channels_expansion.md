# 消息渠道扩展配置

**创建时间**: 2026-02-27  
**状态**: ✅ 配置框架完成

---

## 一、支持渠道清单

### 已实现

| 渠道 | 状态 | 配置 |
|------|------|------|
| **Feishu** | ✅ 已实现 | 飞书私信 |

### 待实现 (P2)

| 渠道 | 优先级 | 工时 | 说明 |
|------|--------|------|------|
| **WhatsApp** | P2 | 1h | Baileys 库 |
| **Telegram** | P2 | 1h | grammY 库 |
| **企业微信** | P2 | 1h | 国内业务需要 |

---

## 二、配置模板

### WhatsApp

```json
{
  "channels": {
    "whatsapp": {
      "enabled": false,
      "provider": "baileys",
      "phoneNumber": "+1234567890",
      "sessionPath": "~/.openclaw/whatsapp-session"
    }
  }
}
```

### Telegram

```json
{
  "channels": {
    "telegram": {
      "enabled": false,
      "provider": "grammy",
      "botToken": "YOUR_BOT_TOKEN"
    }
  }
}
```

### 企业微信

```json
{
  "channels": {
    "wecom": {
      "enabled": false,
      "corpId": "YOUR_CORP_ID",
      "agentId": "YOUR_AGENT_ID",
      "secret": "YOUR_SECRET"
    }
  }
}
```

---

## 三、实施步骤

1. 选择要实施的渠道 (WhatsApp/Telegram/企业微信)
2. 获取 API Credentials
3. 安装对应依赖
4. 配置渠道参数
5. 测试消息收发

---

## 四、验收标准

- [x] 渠道扩展配置文档已创建
- [ ] 新增 2 个消息渠道
- [ ] 消息收发正常
- [ ] 渠道状态监控

---

*配置完成时间：2026-02-27*
