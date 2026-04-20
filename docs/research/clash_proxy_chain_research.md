# 链式代理调研报告

## 一、当前环境分析

| 项目 | 信息 |
|------|------|
| **机场订阅** | WgetCloud |
| **节点IP** | `43.136.40.47` |
| **协议** | Trojan |
| **节点位置** | 香港入口，美国节点 |
| **现有客户端** | Clash Verge (Windows)、小火箭 (iPhone) |

**结论：** 当前 `43.136.40.47` 是**数据中心IP**（阿里云/腾讯云段），不是住宅IP。

---

## 二、当前节点识别

```
IP: 43.136.40.47
ISP: 阿里云/腾讯云数据中心段
结论: 数据中心IP（不是住宅IP）
```

---

## 三、链式代理方案

### 方案A：Clash为前置 + 小火箭出口（推荐）

```
iPhone小火箭 → Clash Verge (Windows) → 机场 → AI
```

**配置步骤：**

1. **Clash Verge (Windows)**
   - 导入 WgetCloud 订阅
   - 选择美国节点
   - 开启 allow-lan
   - 记录 Windows 局域网IP（如 192.168.1.100）

2. **小火箭 (iPhone)**
   - 添加上游代理：HTTP 类型
   - 地址：Windows 局域网IP
   - 端口：7890

---

### 方案B：Clash链式

```
Clash Verge → 小火箭(手机) → 机场 → AI
```

---

## 四、美国住宅静态IP获取方案

### 4.1 机场附加服务

| 机场 | 住宅IP服务 | 价格区间 |
|------|-----------|----------|
| WgetCloud | 可能有附加包 | 咨询客服 |
| 明日气象 | ¥30-80/月 | 按量付费 |
| 维度 | ¥50-100/月 | 包月 |

**操作：** 登录 WgetCloud 控制台，查看是否有"住宅IP"、"原生IP"附加选项

### 4.2 第三方静态IP服务商

| 服务商 | IP类型 | 价格 | 特点 |
|--------|--------|------|------|
| **Proxy302** | 住宅/数据中心 | ¥15-50/月 | 按量计费，中文界面 |
| **Oxylabs** | 住宅/机房 | $15+/月 | 企业级，稳定 |
| **SmartProxy** | 住宅 | $12+/月 | 住宅IP池大 |
| **Bright Data** | 住宅 | $500+/月 | 超大池，适合企业 |

**推荐入门：** Proxy302（性价比高，支持支付宝）

### 4.3 Proxy302 配置到 Clash

```yaml
proxies:
  - name: "Proxy302-美国住宅"
    type: http
    server: proxy.proxy302.com
    port: 8080
    username: your_username
    password: your_password
```

---

## 五、稳定访问AI应用最佳实践

### 5.1 推荐代理链架构

```
AI应用请求
    ↓
Clash (规则分流) → AI域名走指定节点
    ↓
WgetCloud美国节点（推荐带原生/住宅标签）
    ↓
目标服务器
```

### 5.2 Clash AI应用规则配置

```yaml
rules:
  - DOMAIN-SUFFIX,anthropic.com,美国节点
  - DOMAIN-SUFFIX,openai.com,美国节点
  - DOMAIN-SUFFIX,googleapis.com,美国节点
  - DOMAIN-KEYWORD,claude,美国节点
  - MATCH,DIRECT  # 其他直连
```

### 5.3 避免封禁策略

| 策略 | 说明 |
|------|------|
| **使用住宅IP** | 数据中心IP容易被AI平台识别和限制 |
| **设置合适超时** | 请求间隔3-5秒，模拟人类行为 |
| **多IP轮换** | 不要长时间使用同一IP |
| **User-Agent伪装** | 使用常见浏览器的UA |
| **DNS配置** | 使用 8.8.8.8 / 1.1.1.1 |

---

## 六、成本对比

| 方案 | 月成本 | IP类型 | 稳定性 |
|------|--------|--------|--------|
| WgetCloud单节点 | ¥20-50 | 数据中心 | 中 |
| WgetCloud + Proxy302 | ¥50-100 | 住宅 | 高 |
| WgetCloud + SmartProxy | ¥80-150 | 住宅 | 高 |
| 全用住宅服务 | ¥200+ | 住宅 | 最高 |

**推荐方案：** WgetCloud（主力翻墙）+ Proxy302（住宅IP专门用于AI）

---

## 七、执行建议

### 第一步：立即可执行
1. 在 Clash Verge 中导入 WgetCloud 订阅
2. 测试节点 `43.136.40.47` 的延迟和速度
3. 配置 allow-lan 并记录 Windows 局域网IP

### 第二步：验证链式
1. iPhone 小火箭添加 HTTP 上游代理指向 Windows Clash
2. 测试访问 AI 官网是否正常

### 第三步：住宅IP升级（如需要）
1. 登录 WgetCloud 控制台询问住宅IP服务
2. 或注册 Proxy302 获取住宅IP
3. 将住宅IP配置为 AI 应用的专用出口

---

*调研时间：2026-04-18*
