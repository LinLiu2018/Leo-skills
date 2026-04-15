# Security Scan Skill

## 简介

`security_scan_skill` - AI Agent安全扫描工具

参考 ECC 的 `/security-scan` 和 AgentShield 设计，为Leo AI系统提供代码安全扫描能力。

## 功能

- 敏感信息检测（API Keys, Passwords, Tokens）
- 命令注入风险检测
- 路径遍历漏洞检测
- SQL注入风险检测
- XSS漏洞检测
- 文件权限检查
- 依赖包安全扫描

## 使用方式

```
/security-scan              # 扫描整个项目
/security-scan --path src/   # 指定路径
/security-scan --quick       # 快速扫描
/security-scan --json        # JSON格式输出
/security-scan --fix         # 自动修复
```

## 触发关键词

- security-scan
- 安全扫描
- 漏洞检测
- 安全检查

## 分类

core