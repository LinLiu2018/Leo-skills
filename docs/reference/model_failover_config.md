# Model Failover 配置指南

**创建时间**: 2026-02-27  
**状态**: ✅ 已配置

---

## 一、配置说明

### 主备模型配置

| 优先级 | 模型 | 用途 | 状态 |
|--------|------|------|------|
| **主模型** | qwen3.5-plus | 日常任务 | ✅ 已配置 |
| **备用 1** | qwen-plus | 主模型失败时切换 | ⏳ 待配置 |
| **备用 2** | qwen-turbo | 快速响应任务 | ⏳ 待配置 |

---

## 二、配置步骤

### 1. 编辑 openclaw.json

```json
{
  "models": {
    "default": "qwen3.5-plus",
    "failover": {
      "enabled": true,
      "maxRetries": 3,
      "timeout": 30000,
      "fallbacks": [
        "qwen-plus",
        "qwen-turbo"
      ]
    }
  }
}
```

### 2. 配置模型 API

```bash
# 编辑 ~/.openclaw/providers.json
{
  "bailian": {
    "apiKey": "YOUR_API_KEY",
    "models": ["qwen3.5-plus", "qwen-plus", "qwen-turbo"]
  }
}
```

### 3. 测试故障转移

```bash
# 测试主模型
openclaw agent --model qwen3.5-plus --message "test"

# 测试备用模型
openclaw agent --model qwen-plus --message "test"
```

---

## 三、故障转移逻辑

```
用户请求
    │
    ▼
┌─────────────┐
│ 主模型      │ ──失败──┐
│ qwen3.5-plus│          │
└─────────────┘          │
                         ▼
                   ┌─────────────┐
                   │ 备用模型 1   │ ──失败──┐
                   │ qwen-plus   │          │
                   └─────────────┘          │
                                            ▼
                                      ┌─────────────┐
                                      │ 备用模型 2   │
                                      │ qwen-turbo  │
                                      └─────────────┘
```

---

## 四、验收标准

- [x] 配置文档已创建
- [ ] 主备模型 API Key 已配置
- [ ] 故障转移测试通过
- [ ] 切换时间 <5 秒

---

*配置完成时间：待实施*
