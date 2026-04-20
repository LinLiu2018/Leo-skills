# Business 业务数据中枢

> **用途**: 佬流地产业务运营数据的统一存储、生成、归档目录
> **维护人**: AI总助理 (leo-assistant) + 佬流（老板）
> **创建时间**: 2026-04-19
> **最后更新**: 2026-04-19

---

## 📂 目录结构与用途

```
leo_knowledge/memory/business/
├── README.md              ← 本文件（目录使用规范）
├── daily/                 ← 每日产出：晨会简报、日报
├── weekly/                ← 每周产出：周报、周复盘
├── monthly/               ← 每月产出：月报、月度复盘
├── drafts/                ← 草稿、临时调研
├── data/                  ← 业务静态数据（团队/目标/楼盘/客户）
│   ├── team.yaml              ← 销售团队名单与分工
│   ├── targets.yaml           ← 月度/季度业务目标
│   ├── properties.yaml        ← 在售楼盘/主推项目
│   ├── stuck_customers.yaml   ← 停滞客户名单
│   └── competitors.yaml       ← 竞品楼盘档案
└── integrations/          ← 外部系统对接配置
    ├── README.md
    ├── pocket_crm_config.yaml  ← 口袋助理 CRM 接入配置
    └── feishu_config.yaml      ← 飞书机器人配置
```

---

## 📅 文件命名规范

### 日报类（放 `daily/`）
```
销售早会简报-YYYY-MM-DD.md            # 销售早会
日报-业务线-YYYY-MM-DD.md             # 例：日报-别墅-2026-04-20.md
```

### 周报类（放 `weekly/`）
```
周报-业务线-YYYY-Www.md                # 例：周报-全业务-2026-W17.md
周复盘-业务线-YYYY-Www.md              # 例：周复盘-别墅-2026-W17.md
```

### 月报类（放 `monthly/`）
```
月报-业务线-YYYY-MM.md                 # 例：月报-全业务-2026-04.md
月度复盘-业务线-YYYY-MM.md
```

### 草稿类（放 `drafts/`）
```
草稿-主题-YYYY-MM-DD.md
调研-主题-YYYY-MM-DD.md
```

---

## 🔄 工作流约定

### 1. 每日早会简报（自动化最高）
- **生成时间**: 每天早上 07:00（自动触发）
- **数据来源**: 读取 `data/` 下的静态数据 + 口袋助理 API 的动态数据
- **输出位置**: `daily/销售早会简报-YYYY-MM-DD.md`
- **分发渠道**: 飞书群机器人自动推送
- **触发脚本**: `scripts/business/send_daily_intelligence.py`（已有，待升级）

### 2. 业务数据维护（人工+AI协作）
- **team.yaml / properties.yaml**: 有变动时人工更新，AI 不自动改
- **targets.yaml**: 每月月初更新一次
- **stuck_customers.yaml**: AI 每日从口袋助理自动同步，人工审核
- **competitors.yaml**: AI 每周抓取竞品更新，人工复核

### 3. 归档规则
- 当月文件留在当前目录
- 次月1号，AI 自动把上月日报打包到 `daily/archive/YYYY-MM/`
- 当年的月报留在 `monthly/`，次年1号归档到 `monthly/archive/YYYY/`

---

## 🎯 AI 协作规则

### 我（leo-assistant）在这个目录要做的事

| 场景 | 动作 |
|------|------|
| 你说"出份今天的简报" | 读 `data/` + 查 CRM → 写到 `daily/` |
| 你说"看下本周业务怎么样" | 读 `daily/` 本周文件 → 生成周报到 `weekly/` |
| 你给我新的团队成员 | 追加到 `data/team.yaml`，不新建文件 |
| 你告诉我有新楼盘要主推 | 追加到 `data/properties.yaml` 并打优先级标签 |
| 外部 API（口袋助理）数据变化 | 更新 `integrations/pocket_crm_config.yaml` 的同步时间戳 |

### 我不会做的事

- ❌ 删除 `data/` 下的任何数据（只追加/修改，不删除）
- ❌ 改动历史日报（只读，不改）
- ❌ 把敏感客户信息（手机号、身份证）写入明文文件

---

## 🔒 隐私与安全

### 不允许放入本目录的内容
- 客户身份证号
- 客户手机号的完整号码（只能记录后4位，如 `138****1234`）
- 银行卡号、支付信息
- 合同金额的精确数值（用区间或代号，如 `A段`=500万+）

### 允许放入的客户信息
- 姓名（或姓名+花名，如 "王总（投资客A）"）
- 需求画像（学区/投资/自住/面积偏好）
- 跟进阶段（意向/带看/洽谈/成交/流失）
- 接触历史（无具体内容，只记录次数+时间）

---

## 🔗 与 OpenClaw 系统的关系

本目录是 **AI 业务大脑的存储层**，被以下系统读写：

| 系统 | 读/写 | 具体作用 |
|------|------|---------|
| OpenClaw（飞书Agent） | 读 `data/` + 写 `daily/` | 响应飞书内的业务查询 |
| Claude Code VSCode | 读写全部 | 老板手动操作、AI协作 |
| `scripts/business/*.py` | 读 `data/` + 写 `daily/weekly/monthly/` | 定时任务执行 |
| 口袋助理 API | 只写 `data/stuck_customers.yaml` | 客户状态同步 |

---

## 📝 变更日志

| 日期 | 变更 | 操作人 |
|------|------|-------|
| 2026-04-19 | 初始化目录结构、创建 README | leo-assistant |

