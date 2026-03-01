# Usage Tracking 使用追踪配置

**创建时间**: 2026-02-27  
**状态**: ✅ 配置完成

---

## 一、追踪指标

### Token 使用

| 指标 | 说明 |
|------|------|
| **总 Token** | 累计使用 Token 数 |
| **输入 Token** | Prompt 消耗 Token |
| **输出 Token** | Completion 消耗 Token |
| **成本估算** | 按模型价格计算 |

### 会话统计

| 指标 | 说明 |
|------|------|
| **总会话数** | 创建的会话总数 |
| **活跃会话** | 当前活跃会话 |
| **平均时长** | 会话平均持续时间 |

### 技能使用

| 指标 | 说明 |
|------|------|
| **技能调用次数** | 每个技能的调用次数 |
| **技能成功率** | 执行成功比例 |
| **技能平均耗时** | 平均执行时间 |

---

## 二、配置说明

### openclaw.json

```json
{
  "usage": {
    "tracking": {
      "enabled": true,
      "interval": "1h",
      "export": {
        "enabled": true,
        "format": "json",
        "path": "~/.openclaw/usage"
      }
    },
    "limits": {
      "dailyTokens": 1000000,
      "dailyCost": 10.0,
      "notifyThreshold": 0.8
    }
  }
}
```

---

## 三、查看使用统计

```bash
# 查看今日使用
openclaw usage --today

# 查看本周使用
openclaw usage --week

# 查看本月使用
openclaw usage --month

# 导出使用报告
openclaw usage --export --format json
```

---

## 四、验收标准

- [x] 使用追踪配置文档已创建
- [ ] Token 使用追踪可用
- [ ] 会话统计可用
- [ ] 技能使用统计可用

---

*配置完成时间：2026-02-27*
