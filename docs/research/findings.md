# 发现与决策: Claude Code + OpenClaw + 飞书 集成

> **官方仓库**: https://github.com/openclaw/openclaw

## 需求
- 通过飞书聊天机器人访问Leo AI System
- 支持自然语言交互调用Skills/Agents/Workflows
- 支持定时任务自动运转
- 实现7x24小时自动化运营

## 研究发现

### OpenClaw 核心能力
- **Gateway控制平面**: WebSocket网络，统一管理所有渠道
- **多渠道支持**: 12+平台（包含飞书原生支持）
- **技能平台**: 支持bundled、managed、workspace三种技能类型
- **定时任务**: 内置Cron作业支持
- **安全模型**: DM配对策略、沙箱隔离

### 飞书集成
- **连接方式**: WebSocket长连接（推荐）
- **消息支持**: 私聊、群聊、@mention触发
- **媒体处理**: 图片、文件、PDF（入站+出站）
- **渲染模式**: auto/raw/card三种
- **配置方式**: `channels.feishu` 内置支持

### Planning-with-files方法论
- **核心理念**: Context Window = RAM, Filesystem = Disk
- **三文件模式**: task_plan.md + findings.md + progress.md
- **关键规则**: 2-动作规则、3-Strike错误协议、5问题重启测试
- **价值**: 解决AI代理的上下文丢失、目标漂移问题

## 技术决策
| 决策 | 理由 |
|------|------|
| 采用 OpenClaw 作为中间层 | 统一多渠道、内置定时任务、技能管理 |
| 使用内置飞书支持 | 官方支持，稳定可靠 |
| 命令行方式集成Leo System | 快速验证，Python与Node.js解耦 |
| 将planning_with_files升级为核心技能 | 提升整个系统的上下文工程能力 |

## 架构发现

### 三层架构
```
用户层: 飞书/微信/Telegram → 自然语言交互
编排层: OpenClaw Gateway → 技能管理、定时任务、多渠道路由
能力层: Leo System → Skills/Agents/Workflows
```

### 数据流
```
用户消息 → 飞书 → OpenClaw Gateway
    → 解析意图 → 调用Leo System → 返回结果 → 飞书
```

## 遇到的问题
| 问题 | 解决方案 |
|------|----------|
| OpenClaw原生支持飞书 | 使用内置飞书插件 (channels.feishu) |
| Windows环境兼容性 | 直接运行，Node.js ≥22 |

## 资源
- OpenClaw官网: https://www.openclaw.dev/
- OpenClaw GitHub: https://github.com/openclaw/openclaw
- Clawdbot-feishu: https://github.com/m1heng/Clawdbot-feishu (已弃用，OpenClaw内置支持)
- Planning-with-files: https://github.com/OthmanAdi/planning-with-files
- 飞书开放平台: https://open.feishu.cn/
- obra/superpowers: https://github.com/obra/superpowers (TDD/调试/协作技能库)

## 视觉/浏览器发现
- OpenClaw 2026.1.30 内置飞书支持
- Clawdbot-feishu README显示完整的权限配置和使用方法
- Planning-with-files项目有13+ IDE适配版本

## 项目架构优化相关发现（2026-01-29 新增）

### 发现的优质项目

| 项目 | 用途 | 价值 |
|------|------|------|
| **AI Coding Project Toolkit** | 结构化开发工作流 | 三阶段工作流（Specify→Plan→Execute） |
| **Repomix Explorer Skill** | 代码库分析 | 自然语言分析代码库结构 |
| **awesome-claude-skills** | 技能集合 | 6.2k stars，包含多种架构相关技能 |
| **obra/superpowers** | 20+核心技能库 | TDD、调试、协作模式 |

### AI Coding Project Toolkit 核心文档结构
```
project/
├── PRODUCT_SPEC.md        # 产品规格说明
├── TECHNICAL_SPEC.md      # 技术架构设计
├── EXECUTION_PLAN.md      # 带验收标准的任务清单
├── AGENTS.md              # AI代理工作流规则
├── LEARNINGS.md           # 项目特定模式和经验
├── DEFERRED.md            # 延期需求记录
└── .claude/
    └── skills/            # 执行技能
```

### 与Leo System的对比
| 维度 | AI Coding Project Toolkit | Leo System |
|------|---------------------------|------------|
| 规划文件 | PRODUCT_SPEC + TECHNICAL_SPEC | task_plan.md |
| 发现记录 | LEARNINGS.md | findings.md |
| 进度跟踪 | EXECUTION_PLAN.md | progress.md |
| 技能管理 | .claude/skills/ | src/leo_skills/ |

### 建议整合方向
1. 保留Leo System的三文件模式（更简洁）
2. 借鉴TECHNICAL_SPEC.md的架构设计思路
3. 引入AGENTS.md的工作流规则概念
4. 考虑添加DEFERRED.md延期需求管理

---
*每2次查看/浏览/搜索操作后更新此文件*

---

## ϵͳ�������Ż����� (2026-01-30)

### ������Χ
- **��Ŀ·��**: D:\����\leo_ai_system
- **����ʱ��**: 2026-01-30 16:10

### ϵͳ��ģ����

| ָ�� | ��ֵ | ���� |
|------|------|------|
| ���ܷ���Ŀ¼ | 23�� | ? �ṹ���� |
| ������Ŀ¼ | 352�� | ?? ���ܴ������� |
| ����ģ���� | 8�� | ? �ܹ����� |
| ��Ŀ�ļ����� | 200+ | ?? ��Ҫ���� |

### ����ģ��ṹ����

`
src/
������ leo_orchestrator/  ? ����������
������ leo_skills/        ?? ��Ҫ��֤��Ч��
������ leo_subagents/     ?? ��agents (capability_index��ʾ)
������ leo_workflows/     ?? ��workflows (capability_index��ʾ)
������ leo_system/        ? ϵͳ����
������ leo_config/        ? ���ù���
������ leo_knowledge/     ? ֪ʶ��
������ leo_interface/     ? �ӿڲ�
`

### ���ֵ�����

1. **Skills vs Subagentsʧ��**
   - Skills: 287+ (��Ч)
   - Subagents: 0 (capability_index��ʾ)
   - ����: ȱ��Agentʵ�֣��ܹ�������

2. **Workflowsȱʧ**
   - Ԥ���幤����δע��
   - �޷�ʹ��Ԥ�õ� analysis/content/research pipeline

3. **����Ŀ¼����**
   - 352����Ŀ¼���ܰ���:
     - �������ܣ���SKILL.md��
     - �ظ�����
     - �������ܣ���Ҫ�鵵��archive/��

4. **�ɰ�Skillsδ����**
   - leo-skills-old/ Ŀ¼����
   - ����Ӱ��ϵͳ����

5. **֪ʶ�ⲻ����**
   - system_architecture.md ȱʧ
   - user_profile.md ȱʧ
   - development_guide.md ȱʧ

6. **���Ը��ǲ���**
   - tests/ Ŀ¼����Ϊ�ջ�ϡ��

### �Ż��������ȼ�

#### P0 (�����޸�)
1. ����ȱʧ��֪ʶ���ļ�
2. ��֤Skills��Ч��
3. ��������/��������

#### P1 (�������)
4. ʵ�ֻ���Subagents
5. ע��Ԥ��Workflows
6. ���䵥Ԫ����

#### P2 (�¸�����)
7. �鵵leo-skills-old
8. �Ż���Ŀ�ṹ
9. �����ĵ�

### ��Դռ�÷���
- ��Ŀ��Ŀ¼: 200+ �ļ�
- docs/: 50+ �ĵ��ļ�
- examples/: 3 ��ʾ����Ŀ
- archive/: ���ֹ鵵����

### ��ȷ������
1. Subagents�Ƿ�ƻ��ں���Phaseʵ�֣�
2. Workflows��ע�᷽ʽ�Ƿ���ȷ����
3. Skills��ά����׼��ʲô��
