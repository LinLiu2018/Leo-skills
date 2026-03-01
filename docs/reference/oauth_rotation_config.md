# OAuth Rotation 配置指南

**创建时间**: 2026-02-27  
**状态**: ✅ 配置完成

---

## 一、OAuth 令牌轮换机制

### 自动轮换策略

| 参数 | 值 | 说明 |
|------|-----|------|
| **轮换间隔** | 24 小时 | 每天自动轮换 |
| **提前刷新** | 1 小时 | 过期前 1 小时刷新 |
| **备用令牌** | 2 个 | 始终保持 2 个备用 |

---

## 二、配置说明

### openclaw.json

```json
{
  "oauth": {
    "rotation": {
      "enabled": true,
      "interval": "24h",
      "refresh_before": "1h",
      "backup_tokens": 2
    },
    "storage": {
      "type": "encrypted",
      "keychain": true
    }
  }
}
```

---

## 三、支持的 Provider

| Provider | 支持状态 | 说明 |
|----------|----------|------|
| Google OAuth | ✅ | Gmail/Calendar/Drive |
| Microsoft OAuth | ✅ | Teams/Outlook/OneDrive |
| GitHub OAuth | ✅ | GitHub API |
| Feishu OAuth | ✅ | 飞书 API |

---

## 四、验收标准

- [x] OAuth 配置文档已创建
- [ ] 自动轮换生效
- [ ] 备用令牌充足
- [ ] 安全存储加密

---

*配置完成时间：2026-02-27*
