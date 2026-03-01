# Sandboxing 技能沙箱配置

**创建时间**: 2026-02-27  
**状态**: ✅ 配置完成

---

## 一、沙箱隔离机制

### 隔离级别

| 级别 | 说明 | 适用场景 |
|------|------|----------|
| **Level 1** | 文件系统隔离 | 普通技能 |
| **Level 2** | 网络访问限制 | 网络技能 |
| **Level 3** | 完整沙箱 (Docker) | 高风险技能 |

---

## 二、配置说明

### openclaw.json

```json
{
  "sandbox": {
    "enabled": true,
    "level": 2,
    "allowed_paths": [
      "~/.openclaw/workspace",
      "/tmp/openclaw"
    ],
    "blocked_commands": [
      "rm -rf",
      "sudo",
      "chmod 777"
    ],
    "network": {
      "enabled": true,
      "allowed_hosts": [
        "api.openclaw.ai",
        "github.com"
      ]
    }
  }
}
```

---

## 三、技能沙箱标记

### SKILL.md

```yaml
---
name: example_skill
sandbox:
  required: true
  level: 2
  permissions:
    - filesystem:read
    - network:external
---
```

---

## 四、验收标准

- [x] 沙箱配置文档已创建
- [ ] 技能执行沙箱隔离
- [ ] 危险命令被阻止
- [ ] 网络访问受限制

---

*配置完成时间：2026-02-27*
