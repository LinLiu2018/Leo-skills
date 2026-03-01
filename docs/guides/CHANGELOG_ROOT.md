# CHANGELOG.md - 变更日志

**项目**: Leo AI System  
**仓库**: github.com/leo-ai-system/leo_ai_system

---

## [2026.2.27] - 2026-02-27

### Added - 新增

#### P0 核心工具
- **Browser 技能** (`browser_skill`) - Playwright 浏览器控制
- **WebChat 配置** - 网页聊天界面配置
- **Control UI 配置** - 控制界面配置
- **Model Failover** - 模型故障转移配置
- **onboard 向导** - 快速入门向导文档

#### P1 安全运维
- **Sandboxing** - 技能沙箱隔离配置
- **OAuth Rotation** - OAuth 令牌轮换配置
- **doctor 健康检查** - 系统健康检查脚本
- **Usage Tracking** - 使用追踪技能
- **Auto Update** - 自动更新技能

#### P2 扩展功能
- **消息渠道扩展** - WhatsApp/Telegram/企业微信配置
- **ClawHub 技能引入** - 社区技能引入配置
- **Docker 部署** - Docker Compose 配置
- **Voice Wake** - 语音唤醒配置
- **Nodes** - 设备节点配置

#### 文档
- **VISION.md** - 项目愿景文档
- **CONTRIBUTING.md** - 贡献指南
- **SECURITY.md** - 安全策略
- **CHANGELOG.md** - 变更日志 (本文件)

### Changed - 变更

#### 技能优化
- **skill_vetter_skill** (v1.1.0) - 优化代码生成器识别，误报率降低
- **web_search_enhanced_skill** - 添加速率限制优化

#### 配置优化
- **Cron 时间分散** - 19 个任务分散到 7:00-20:00
- **Workspace 隔离** - 7 个业务板块独立 Workspace

### Fixed - 修复

- 修复 ai_news_summary_agent 导入错误
- 修复测试导入路径问题
- 修复 GBK 编码问题 (Windows 兼容)

### Stats - 统计

| 指标 | 之前 | 现在 | 变化 |
|------|------|------|------|
| **Skills** | 113 | 121 | +8 |
| **Agents** | 24 | 24 | 0 |
| **Workflows** | 8 | 8 | 0 |
| **Cron Jobs** | 19 | 22 | +3 |
| **配置文件** | 5 | 17 | +12 |
| **文档** | 20 | 35 | +15 |
| **实现率** | 33% | 75% | +42% |

### Health Check - 健康检查

```
Leo AI Doctor - Health Check
Result: 7/7 passed
[OK] All checks passed! System healthy.

- Gateway: ✅
- Channels: ✅
- Skills: 121
- Agents: 24
- Cron: ✅
- Security: ✅
- Models: ✅
```

---

## [2026.2.26] - 2026-02-26

### Added - 新增

#### 房产军团 (4 个 Agent)
- `villa_agent` - 别墅专家
- `residential_agent` - 住宅专家
- `commercial_sales_agent` - 商业销售
- `commercial_lease_agent` - 商业租赁

#### AI 开发军团
- `memory_agent` - 记忆管家
- `github_auto_register_skill` - GitHub 技能自动注册
- `skill_deduplication_skill` - 技能去重检查

#### 跨境电商军团 (3 个 Agent)
- `product_agent` - 选品专家
- `operation_agent` - 运营专家
- `logistics_agent` - 物流专家

#### 贷款金融 (2 个 Agent)
- `loan_agent` - 贷款顾问
- `bank_product_agent` - 银行产品专家

#### 商业地产 (2 个 Agent)
- `commercial_agent` - 商业地产顾问
- `investment_agent` - 投资顾问

#### 内容创意
- `distribution_agent` - 内容分发专家

### Changed - 变更

#### Cron 优化
- 所有定时任务调整到 8:00 推送
- 添加 staggerMs 错开执行

#### 能力索引
- Skills: 106 → 113 (+7)
- Agents: 22 → 24 (+2)
- 总能力：136 → 143 (+7)

---

## [2026.2.25] - 2026-02-25

### Added - 新增

#### 定时任务
- 宁波新房_定时检查_v2 (每 4 小时)
- 房产资讯_每日 8 点_v2
- AI 财经资讯_每日 8 点_v2
- 优质内容_每日 OpenClaw (21:00)

#### 技能
- 多个基础技能

### Stats

- Skills: 106
- Agents: 22
- Cron Jobs: 18

---

## [2026.2.18] - 2026-02-18

### Added - 新增

#### 项目初始化
- Leo AI System 项目创建
- OpenClaw 集成
- Feishu 渠道配置

#### 基础架构
- 四层架构设计
- 多代理架构设计
- 技能系统设计

### Stats

- Skills: 106 (继承)
- Agents: 9 (继承)
- Workflows: 8 (继承)

---

## 版本说明

### 版本号规则

采用 `YYYY.M.D` 格式：
- **YYYY**: 年份
- **M**: 月份
- **D**: 日期

### 变更类型

- **Added**: 新增功能
- **Changed**: 变更/优化
- **Deprecated**: 即将废弃
- **Fixed**: Bug 修复
- **Security**: 安全更新
- **Stats**: 统计数据

---

## 参考

- [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)
- [Semantic Versioning](https://semver.org/)
- [OpenClaw CHANGELOG](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

---

*最后更新：2026-02-27*  
*维护者：Leo Liu*
