# Microsoft Store 代理问题调研报告

## 一、问题分析

### 1.1 根本原因

| 组件 | 使用的API | 代理设置 |
|------|-----------|----------|
| 浏览器、CLI工具 | WinINET | 走系统代理 ✅ |
| **Microsoft Store** | **WinHTTP** | **不走系统代理** ❌ |
| Windows更新 | BITS | 单独配置 |

**Microsoft Store 使用 WinHTTP 而不是 WinINET**，所以不认系统代理设置。

### 1.2 TUN模式问题

| 特性 | TUN模式 | 系统代理模式 |
|------|---------|--------------|
| 工作层级 | IP层 | HTTP层 |
| 截获范围 | 所有流量 | 仅HTTP/HTTPS |
| Microsoft Store | **可能被TUN错误路由** | **不劫持，直连** |

---

## 二、解决方案

### 方案A：添加Microsoft域名直连规则（推荐）

在 Clash 配置中添加：

```yaml
# Microsoft Store 必须直连
- DOMAIN-SUFFIX,microsoft.com,DIRECT
- DOMAIN-SUFFIX,microsoftonline.com,DIRECT
- DOMAIN-SUFFIX,live.com,DIRECT
- DOMAIN-SUFFIX,account.microsoft.com,DIRECT
- DOMAIN-SUFFIX,storeedgefd.dsx.mp.microsoft.com,DIRECT
- DOMAIN-SUFFIX,licensing.mp.microsoft.com,DIRECT
- DOMAIN-SUFFIX,displaycatalog.mp.microsoft.com,DIRECT
- DOMAIN-KEYWORD,microsoft,DIRECT
```

### 方案B：关闭TUN模式，改用系统代理

1. 设置 → 虚拟网卡模式 → 关闭
2. 重启 Clash Verge
3. Microsoft Store 直连，不走代理

### 方案C：使用第三方下载器

访问 https://store.rg-adguard.net 下载 Microsoft Store 应用

---

## 三、已实施的配置

### 当前代理规则

| 域名 | 代理组 | 状态 |
|------|--------|------|
| Microsoft Store 相关 | 🚀 节点选择 | ✅ 直连/机场 |
| GitHub / Azure AI | 🤖 AI专用-链式代理 | ✅ IPRoyal |
| AI 应用 (Claude等) | 🤖 AI专用-链式代理 | ✅ IPRoyal |
| TikTok | 🤖 AI专用-链式代理 | ✅ IPRoyal |
| 国内网站 | 🎯 全球直连 | ✅ 直连 |

### WSL 分流状态

| 流量 | 路径 | 延迟 |
|------|------|------|
| 国内IP | 直连 | 0.1秒 ✅ |
| 国外IP | Windows → IPRoyal | 正常 ✅ |

---

## 四、iPhone小火箭配置建议

### 链式代理
```
iPhone → 机场(美国01) → IPRoyal(住宅IP) → AI/TikTok
```

### 分流规则
```
DOMAIN-SUFFIX,microsoft.com,DIRECT
DOMAIN-KEYWORD,microsoft,DIRECT
GEOIP,CN,DIRECT
MATCH,海外流量
```

---

## 五、执行建议

1. **立即测试**：重新导入配置，关闭TUN模式试Microsoft Store
2. **如仍失败**：使用 store.rg-adguard.net 下载应用
3. **长期方案**：配置Microsoft域名直连规则

---

*调研时间：2026-04-19*
