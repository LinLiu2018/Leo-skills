# Control UI 控制界面配置指南

**创建时间**: 2026-02-27  
**状态**: ⏳ 配置框架已创建

---

## 一、Control UI 功能

### 核心功能

| 功能 | 说明 |
|------|------|
| Gateway 管理 | 启动/停止/重启 Gateway |
| 会话管理 | 查看/管理活跃会话 |
| Cron 管理 | 查看/编辑定时任务 |
| 渠道状态 | 查看各渠道连接状态 |
| 技能管理 | 安装/卸载/更新技能 |
| 使用统计 | Token 使用/成本分析 |
| 日志查看 | 实时日志流 |

---

## 二、部署步骤

```bash
# 1. 启用 Control UI
openclaw config set ui.enabled true

# 2. 配置端口
openclaw config set ui.port 18788

# 3. 启动 UI
openclaw ui start

# 4. 访问
# http://localhost:18788
```

---

## 三、配置示例

```json
{
  "ui": {
    "enabled": true,
    "port": 18788,
    "host": "0.0.0.0",
    "auth": {
      "enabled": true,
      "type": "password",
      "password": "YOUR_PASSWORD"
    }
  }
}
```

---

## 四、验收标准

- [ ] Control UI 可访问
- [ ] 可管理 Gateway
- [ ] 可查看会话
- [ ] 可管理 Cron
- [ ] 可查看日志

---

*配置完成时间：待实施*
