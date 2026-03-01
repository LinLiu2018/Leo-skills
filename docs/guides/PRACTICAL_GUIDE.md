# Leo AI System 实操手册

> **目标**: 解决"系统文件代码很多，但真正用不起来"的困局，聚焦可落地业务场景

---

## 一、现状诊断

### 1.1 系统能力概览

| 能力类型 | 数量 | 实际可用 |
|---------|------|---------|
| Skills（技能） | 117 | ~15个 |
| Agents（代理） | 9 | ~3个 |
| Workflows（工作流） | 9 | ~2个 |
| 业务脚本 | 9 | ~5个 |

### 1.2 困局根因分析

```
问题: 117个技能 = 看起来很强，用不起来
  │
  ├─ 原因1: 技能是"生成器"不是"执行器"
  │   └─ 大多数skill是"生成代码/文档"的工具，不是直接执行任务的自动化
  │
  ├─ 原因2: 缺乏业务场景串联
  │   └─ 技能是散落的珠子，没有串成项链（业务链）
  │
  └─ 原因3: 缺少触发机制
      └─ 技能需要手动调用，无法自动触发
```

### 1.3 核心教训

> **技能 ≠ 自动化**
> - 能生成代码 ≠ 能帮你干活
> - 需要把"生成"变成"执行"，才能真正提效

---

## 二、你的核心业务场景（2026版）

基于 `user_profile.md` 分析，你当前有三大核心业务：

### 2.1 业务矩阵

| 业务 | 当前阶段 | 核心痛点 | AI提效点 |
|------|---------|---------|---------|
| 🏠 **房产经纪** | 核心业务 | 获客转化、内容生产 | 短视频/广告/话术 |
| 🏪 **商业地产** | 拓展期 | 市场调研、竞品分析 | 市场报告自动化 |
| 👓 **跨境电商** | 筹备期 | 选品、竞品监测 | 数据采集分析 |

### 2.2 重点落地项目

| 项目 | 状态 | 已产出 |
|------|------|-------|
| 乐橙荟商铺 | 销售中 | 短视频4平台、话术、销售手册 |
| 建华官园菜场 | 销售中 | 裂变方案、销售速查卡 |
| 嘉华小程序 | 开发中 | Vant Weapp + 裂变能力 |
| 视频号监测 | 规划中 | 账号数据监测 |

---

## 三、可落地业务场景（实操清单）

以下是从117个技能中筛选出的**真正能干活**的场景，按业务分类：

### 3.1 内容生产（立即可用 ⭐⭐⭐）

| 场景 | 工具 | 调用方式 | 产出 |
|------|------|---------|------|
| 短视频脚本 | 飞书发送需求 | 触发 `realestate_news_publisher_skill` | 4平台适配脚本 |
| 项目营销手册 | `generate_marketing_manual.py` | 脚本执行 | 完整营销方案 |
| 朋友圈文案 | 飞书对话 | AI即时生成 | 推广文案 |
| 广告文案 | 飞书对话 | AI即时生成 | 抖音/微信广告 |

**调用示例**:
```
飞书发送: "帮我写一个乐橙荟的30秒短视频脚本，重点强调投资回报"
```

### 3.2 市场调研（立即可用 ⭐⭐⭐）

| 场景 | 工具 | 调用方式 | 产出 |
|------|------|---------|------|
| 区域市场分析 | `research_ningbo_commercial.py` | 脚本执行 | 市场分析报告 |
| 竞品研究 | `competitor_scraper_skill` | 技能调用 | 竞品数据 |
| 微信文章采集 | `research_wechat_article.py` | 脚本执行 | 行业资讯 |

**调用示例**:
```
# 每周市场动态
python scripts/business/research_ningbo_commercial.py
```

### 3.3 获客自动化（部分可用 ⭐⭐）

| 场景 | 工具 | 当前状态 | 说明 |
|------|------|---------|------|
| 裂变小程序 | `fission_miniprogram` | 已有代码 | 需要部署 |
| 视频号监测 | `video_monitor_skill` | 已开发 | 需要配置 |
| 电话机器人 | 飞书+AI | 已有话术 | 需要对接外呼 |
| 抖音广告 | 手动 | 已有方案 | 投放执行 |

### 3.4 运营自动化（规划中 ⭐）

| 场景 | 工具 | 依赖 | 落地计划 |
|------|------|------|---------|
| 每日数据汇总 | `send_daily_intelligence.py` | 飞书机器人 | Q2 |
| 客户自动跟进 | n8n工作流 | 线索系统 | Q3 |
| 知识库问答 | OpenClaw技能 | 训练数据 | Q3 |

---

## 四、实操执行手册

### 4.1 日常高频操作（每天用）

#### 操作1: 快速生成销售物料

```
场景: 客户问"这个铺子怎么样？"

步骤:
1. 打开飞书/企业微信
2. 召唤 Leo AI
3. 输入: "根据乐橙荟调研报告，生成一段面向投资客的推荐话术"
4. AI生成 → 复制使用
```

#### 操作2: 每周市场调研

```
场景: 每周一更新市场动态

步骤:
1. 执行: python scripts/business/research_ningbo_commercial.py
2. AI分析报告
3. 生成: 每周市场简报
4. 发送到工作群
```

#### 操作3: 短视频脚本生成

```
场景: 需要发抖音/视频号

步骤:
1. 飞书发送需求
2. AI生成4平台适配脚本
3. 人工审核调整
4. 拍摄发布
```

### 4.2 中频操作（每周/每月）

| 操作 | 频率 | 命令 |
|------|------|------|
| 更新能力索引 | 每周 | `python scripts/maintenance/update_capability_index.py` |
| 技能审计 | 每月 | `python scripts/development/validate_skills.py` |
| 竞品数据采集 | 每周 | 触发 `competitor_scraper_skill` |
| 微信文章存档 | 每天 | `python scripts/business/research_wechat_article.py` |

### 4.3 低频操作（按需）

| 操作 | 场景 | 命令 |
|------|------|------|
| 生成新项目营销手册 | 新项目启动 | `python scripts/business/generate_marketing_manual_real.py` |
| 创建小程序页面 | 嘉华小程序迭代 | 调用 `miniprogram_page_generator_skill` |
| 生成API后端 | 小程序后端 | 调用 `flask_api_generator_skill` |

---

## 五、落地路线图（3个月）

### 阶段1: 夯实基础（第1个月）

| 周 | 目标 | 验收标准 |
|----|------|---------|
| 第1周 | 跑通内容生产流程 | 短视频脚本生成 → 审核 → 发布 |
| 第2周 | 跑通市场调研流程 | 市场报告生成 → 发送飞书 |
| 第3周 | 部署裂变小程序 | 嘉华小程序上线测试 |
| 第4周 | 建立数据监测 | 视频号数据看板 |

### 阶段2: 自动化提升（第2个月）

| 周 | 目标 | 验收标准 |
|----|------|---------|
| 第5周 | 飞书日报自动化 | 每日自动推送市场数据 |
| 第6周 | 竞品监测自动化 | 每周自动生成竞品报告 |
| 第7周 | 线索跟进自动化 | n8n工作流打通 |
| 第8周 | 知识库建设 | 常见问题AI问答 |

### 阶段3: 全面AI化（第3个月）

| 周 | 目标 | 验收标准 |
|----|------|---------|
| 第9周 | 短视频批量生产 | 日产5条以上 |
| 第10周 | 电话机器人部署 | AI外呼测试 |
| 第11周 | 全流程打通 | 获客→转化→跟进全自动化 |
| 第12周 | 复盘优化 | 效率提升50%验证 |

---

## 六、问题解决指南

### 6.1 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 技能调用没反应 | 技能未注册 | 运行 `python scripts/maintenance/update_capability_index.py` |
| 脚本执行报错 | 依赖缺失 | `pip install -r requirements.txt` |
| 飞书没响应 | OpenClaw网关停止 | 重启网关: `cd D:\openclaw && node openclaw.mjs gateway --port 18789` |
| 生成的文档不满意 | prompt不够具体 | 提供更多背景信息、参考案例 |

### 6.2 故障排查命令

```bash
# 检查OpenClaw状态
netstat -ano | findstr "18789"

# 检查Python环境
python --version
pip list | findstr "openai"

# 检查飞书消息
type \tmp\openclaw\openclaw-2026-02-*.log | findstr "feishu"
```

---

## 七、快速索引表

### 7.1 常用脚本

| 脚本 | 路径 | 用途 |
|------|------|------|
| 生成营销手册 | `scripts/business/generate_marketing_manual_real.py` | 新项目启动 |
| 市场调研 | `scripts/business/research_ningbo_commercial.py` | 每周市场 |
| 飞书报告 | `scripts/business/send_feishu_report.py` | 自动推送 |
| 微信文章 | `scripts/business/research_wechat_article.py` | 行业资讯 |

### 7.2 常用技能

| 技能 | 路径 | 用途 |
|------|------|------|
| 短视频脚本 | `content_creation/realestate_news_publisher_skill` | 内容生产 |
| 小程序生成 | `frontend/miniprogram_page_generator_skill` | 嘉华小程序 |
| API生成 | `backend/flask_api_generator_skill` | 后端开发 |
| 竞品监测 | `business/competitor_scraper_skill` | 数据采集 |

### 7.3 常用命令

```bash
# 日常
python scripts/business/research_ningbo_commercial.py  # 市场调研
python scripts/business/generate_marketing_manual_real.py  # 生成营销手册

# 运维
cd D:\openclaw && node openclaw.mjs gateway --port 18789  # 启动飞书AI
python scripts/maintenance/update_capability_index.py  # 更新索引

# 开发
python scripts/development/create_skill.py  # 创建新技能
python scripts/development/standardize_skills.py  # 标准化技能
```

---

## 八、下一步行动

### 立即执行（今天）

1. ☐ 尝试运行市场调研脚本
   ```bash
   python scripts/business/research_ningbo_commercial.py
   ```

2. ☐ 通过飞书发送一条内容需求测试AI响应

3. ☐ 检查OpenClaw网关状态

### 本周目标

1. ☐ 完成1次完整的内容生产流程（需求→生成→审核→发布）
2. ☐ 部署嘉华小程序到测试环境
3. ☐ 配置视频号数据监测

### 本月目标

1. ☐ 建立标准化的内容生产SOP
2. ☐ 实现市场调研周报自动化
3. ☐ 跑通获客转化全流程

---

> **核心理念**: 不要追求"功能全"，要追求"用起来"
> - 10个能用的功能 > 100个没用的功能
> - 小步快跑，持续迭代
