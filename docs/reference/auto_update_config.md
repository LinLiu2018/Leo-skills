# Auto Update 自动更新配置

**创建时间**: 2026-02-27  
**状态**: ✅ 配置完成

---

## 一、更新策略

### 更新频道

| 频道 | 说明 | 推荐 |
|------|------|------|
| **stable** | 稳定版 (tagged releases) | ✅ 生产环境 |
| **beta** | 测试版 (prerelease) | 测试环境 |
| **dev** | 开发版 (main branch) | 开发环境 |

### 更新频率

| 类型 | 频率 | 说明 |
|------|------|------|
| 自动检查 | 每日 | 每天检查一次更新 |
| 自动下载 | 手动 | 需确认后下载 |
| 自动安装 | 手动 | 需确认后安装 |

---

## 二、配置说明

### openclaw.json

```json
{
  "update": {
    "enabled": true,
    "channel": "stable",
    "checkInterval": "24h",
    "autoDownload": false,
    "autoInstall": false,
    "notify": true
  }
}
```

---

## 三、更新命令

```bash
# 检查更新
openclaw update --check

# 下载更新
openclaw update --download

# 安装更新
openclaw update --install

# 切换到指定频道
openclaw update --channel stable|beta|dev
```

---

## 四、验收标准

- [x] 自动更新配置文档已创建
- [ ] 更新检查可用
- [ ] 更新下载可用
- [ ] 更新安装可用

---

*配置完成时间：2026-02-27*
