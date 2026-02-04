# 任务计划: Claude Code + OpenClaw + 飞书 集成系统

> **官方仓库**: https://github.com/openclaw/openclaw
> **当前版本**: v2026.1.30

## 目标
构建一个通过飞书聊天机器人访问的AI智能体系统，实现Leo System的Skills/Agents/Workflows通过自然语言交互和定时任务自动运转，支撑"一人=10亿级公司"的终极愿景。

## 当前阶段
Phase 6: 生产部署 ✅ (本地已完成)

## 阶段列表

### Phase 1: 架构设计与技术选型 ✅
- [x] 研究 OpenClaw 架构和能力
- [x] 确定集成路径：Leo System → OpenClaw → 飞书
- [x] 克隆参考项目（planning-with-files）
- [x] 创建 planning_with_files_skill
- [x] 集成 ai_coding_project_base（28个技能）
- [x] 集成 obra/superpowers（12个专业开发技能）
- **状态:** complete

### Phase 2: 环境准备与基础设施 ✅
- [x] 安装 Node.js 22+ 环境 (v24.12.0 ✓)
- [x] 安装 OpenClaw (`npm install -g openclaw@latest`) (v2026.1.30 ✓)
- [x] 创建飞书开放平台应用
- [x] 配置飞书机器人权限
- [x] 配置 WebSocket 长连接模式
- **状态:** complete

### Phase 3: Leo System Skills注册 ✅
- [x] 创建 OpenClaw 技能包目录
- [x] 注册核心 Skills 到 OpenClaw
  - [x] 1-13分类技能 (61个)
  - [x] 14-17分类技能 (43个)
- [x] 配置 extraDirs 加载 Leo Skills 目录
- [x] 测试技能调用
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

## 关键问题
1. OpenClaw 在 Windows 环境下的兼容性如何？→ 直接支持，无需 WSL2
2. 飞书应用审核需要多长时间？→ 企业自建应用通常即时生效
3. Leo System 的 Python 调用如何与 OpenClaw 的 Node.js 环境集成？→ 通过命令行调用

## 已做决策
| 决策 | 理由 |
|------|------|
| 使用 OpenClaw 内置飞书支持 | 官方支持，稳定可靠 |
| 使用 WebSocket 长连接模式 | 无需公网 IP，更稳定 |
| 采用 planning_with_files 方法 | 解决上下文丢失问题，提升系统可靠性 |
| 使用守护进程脚本 | 自动重连，提高稳定性 |

## 遇到的错误
| 错误 | 尝试次数 | 解决方案 |
|------|----------|----------|
| gateway.local 配置无效 | 3 | 使用 `openclaw doctor --fix` 修复 |
| gateway.mode 配置问题 | 2 | 正确格式: `gateway.mode: "local"` |

## 备注
- 进度更新：pending → in_progress → complete
- 重大决策前重读此计划（注意力操控）
- 记录所有错误 - 它们帮助避免重复
- 此计划使用 planning_with_files_skill 方法论
