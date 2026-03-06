# Claude Code 权限配置

## 权限模式

Claude Code 支持以下权限模式：

| 模式 | 说明 | 使用场景 |
|------|------|----------|
| `accept` | 自动接受所有操作 | 信任环境 |
| `plan` | 计划模式，列出操作但不执行 | 需要先查看计划 |
| `review` | 每次操作需要确认 | 需要人工审核 |
| `browse` | 浏览模式，只读操作 | 探索代码库 |

## 使用方式

```bash
# 使用特定权限模式启动
claude --permission-mode review
claude --permission-mode plan
```

## 权限规则语法

在 CLAUDE.md 中配置权限规则：

```markdown
<!-- 允许特定工具 -->
Allow: Bash(git *)

<!-- 拒绝特定命令 -->
Deny: Bash(rm *)
Deny: Bash(rm -rf *)

<!-- 拒绝所有删除操作 -->
Deny: Write
Deny: Edit

<!-- 允许特定技能 -->
Allow: Skill(commit)
Allow: Skill(review *)

<!-- 拒绝危险技能 -->
Deny: Skill(deploy *)
```

## 模式说明

### accept (默认)
所有操作自动执行，无需确认。

### plan
Claude 会先列出计划的操作，显示要修改的文件和具体变更，但不立即执行。需要用户确认才会执行。

### review
每次执行工具前都需要用户确认。适合需要人工审核关键操作的场景。

### browse
只读模式，限制使用 Write、Edit、Delete 等写入工具。适合探索代码库时使用。

## 危险操作警告

以下操作会被视为危险，需要特别注意：

- `Bash(rm *)` - 删除文件
- `Bash(rm -rf *)` - 递归删除
- `Bash(git push --force)` - 强制推送
- `Write` - 写入文件
- `Edit` - 编辑文件
- `Bash(chmod -R)` - 修改权限
- `Bash(kill *)` - 终止进程

## 最佳实践

1. **开发环境**: 使用默认 `accept` 模式
2. **代码审查**: 使用 `review` 模式
3. **探索代码**: 使用 `browse` 模式
4. **生产环境**: 使用 `plan` 模式 + 详细规则

## 相关文档

- 官方文档: https://code.claude.com/docs/en/permissions
- 配置文件: https://code.claude.com/docs/en/settings
