# 任务计划: Leo System → OpenClaw 集成

> **官方仓库**: https://github.com/openclaw/openclaw
> **当前版本**: v2026.1.30

## 目标
将 Leo AI System 的 Skills/Agents/Workflows 接入 OpenClaw，实现飞书自然语言调用。

## 当前阶段
Phase 6: 生产部署 ✅ (本地已完成)

## 阶段列表

### Phase 3: Leo System Skills 注册 ✅
- [x] **3.1 评估现有 Skills 接口兼容性**
  - [x] 检查核心 Skills 的输入输出格式
  - [x] 识别需要适配的接口
- [x] **3.2 创建 OpenClaw Skills 包装器**
  - [x] leo-content-layout
  - [x] leo-research
  - [x] leo-realestate
- [x] **3.3 创建 manifest 注册文件**
  - [x] skills manifest
  - [x] agents manifest
  - [x] workflows manifest
- [x] **3.4 更新 OpenClaw 配置**
  - [x] 添加 skills directories 配置
  - [x] 添加 manifest 路径
- [x] **3.5 测试验证**
  - [x] Skills 调用测试
  - [x] Agents 调用测试
  - [x] Workflows 调用测试
- **状态:** complete

### Phase 4: 定时任务配置
- [ ] 配置每日市场情报任务（8:00）
- [ ] 配置每日内容生成任务（9:00）
- [ ] 配置竞品监控任务（每4小时）
- [ ] 配置周报生成任务（周五18:00）
- [ ] 测试定时任务执行
- **状态:** pending

### Phase 5: 集成测试与优化 ✅
- [x] 测试飞书私聊交互
- [x] 测试飞书群聊@触发
- [ ] 测试定时任务推送
- [x] 优化响应速度和稳定性
- [x] 文档完善
- **状态:** mostly complete

### Phase 6: 生产部署 ✅ (本地)
- [x] 配置本地环境
- [x] 部署 OpenClaw Gateway
- [x] 配置守护进程自动重启
- [x] 本地运行稳定
- **状态:** complete (本地)

## 已创建的文件

### Skills (3个)
D:\moltbot\skills\leo-content-layout\
├── SKILL.md                    # 技能文档
└── scripts\
    └── wrapper.py              # Python 包装器

D:\moltbot\skills\leo-research\
├── SKILL.md                    # 技能文档
└── scripts\
    └── wrapper.py              # Python 包装器

D:\moltbot\skills\leo-realestate\
├── SKILL.md                    # 技能文档
└── scripts\
    └── wrapper.py              # Python 包装器

### 配置文件
D:\moltbot\skills\manifest.json          # Skills/Agents/Workflows 注册表
C:\Users\刘方林\.openclaw\openclaw.json  # OpenClaw 配置

## 注册的 Skills 触发词

| Skill | 触发词 |
|-------|--------|
| leo-content-layout | 排版、公众号、小红书、智能排版、format、layout |
| leo-research | 研究、调研、市场分析、竞品、research、分析 |
| leo-realestate | 房地产、房产、营销文案、项目推广、real estate |

## 注册的 Agents
| Agent | 类型 |
|-------|------|
| leo-task-agent | executor |
| leo-research-agent | researcher |
| leo-analysis-agent | analyzer |
| leo-creative-agent | creator |
| leo-realestate-agent | realestate |

## 注册的 Workflows
| Workflow | 说明 |
|----------|------|
| leo-content-pipeline | 研究→创作→发布 |
| leo-research-pipeline | 收集→分析 |
| leo-analysis-pipeline | 分析→报告 |

## 下一步
1. 配置定时任务
2. 云端部署 (Hostinger/Vultr)
3. 补充更多 Skills (agent_skill_creator, skill_evolution_assistant)
