# Repo Watch Skill (核心仓库监控技能)

## 技能描述

监控核心依赖仓库的更新，生成周报并通过飞书发送。

## 核心能力

- **仓库监控**: 监控指定 GitHub 仓库的 Releases、Commits、Issues
- **周报生成**: 每周一早上9点自动生成汇总报告
- **飞书推送**: 通过 OpenClaw Gateway 发送报告到飞书
- **更新建议**: 分析更新内容，给出是否需要更新的建议

## 监控的仓库

| 仓库 | 地址 | 用途 |
|------|------|------|
| **Claude Code** | https://github.com/anthropics/claude-code | Anthropic 官方 CLI 工具 |
| **OpenClaw** | https://github.com/openclaw/openclaw | 飞书/多渠道机器人框架 |

## 使用方法

```python
from repo_watch_skill import RepoWatchSkill

skill = RepoWatchSkill()

# 检查所有仓库更新
result = skill.execute(action="check_all")

# 检查单个仓库
result = skill.execute(
    action="check",
    repo="openclaw/openclaw"
)

# 生成周报
result = skill.execute(action="generate_report")

# 发送飞书报告
result = skill.execute(action="send_feishu_report")
```

## 报告内容

### 周报模板
```markdown
# 核心仓库周报 (YYYY-MM-DD)

## Claude Code (anthropics/claude-code)
- **当前版本**: vX.X.X
- **最新版本**: vX.X.X
- **更新状态**: ✅ 已是最新 / ⚠️ 有新版本
- **本周更新**:
  - [Release] vX.X.X - 新功能描述
  - [Commit] 修复了XXX问题
- **建议**: 建议更新 / 暂不更新

## OpenClaw (openclaw/openclaw)
- **当前版本**: vX.X.X
- **最新版本**: vX.X.X
- **更新状态**: ✅ 已是最新 / ⚠️ 有新版本
- **本周更新**:
  - [Release] vX.X.X - 新功能描述
- **建议**: 建议更新 / 暂不更新
```

## 定时任务配置

在 OpenClaw 中配置定时任务：

```json
{
  "schedules": {
    "repo_watch_weekly": {
      "cron": "0 9 * * 1",
      "skill": "repo_watch",
      "action": "send_feishu_report"
    }
  }
}
```

## 配置

参考 `config/config.yaml`
