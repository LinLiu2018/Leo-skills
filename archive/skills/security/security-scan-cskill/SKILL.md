# 安全扫描技能 Skill

## 技能描述

代码安全检查和漏洞扫描，检测常见安全问题。

## 激活词

- "安全扫描"
- "代码安全检查"
- "漏洞扫描"

## 检测的安全问题

| 类型 | 严重程度 | 说明 |
|------|----------|------|
| hardcoded_secret | 高 | 硬编码的密钥或密码 |
| sql_injection | 严重 | SQL注入漏洞 |
| xss | 高 | 跨站脚本攻击 |
| command_injection | 严重 | 命令注入漏洞 |
| insecure_random | 中 | 不安全的随机数 |
| debug_enabled | 低 | 调试模式启用 |
| insecure_http | 中 | 不安全的HTTP |

## 输出

- `security_report.md` - Markdown格式报告
- 包含问题概览、详细发现、修复建议

## 版本

- 版本: 1.0.0
- 作者: Leo Liu
