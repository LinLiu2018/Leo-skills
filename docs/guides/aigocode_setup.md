# AIgocode 第三方中转接入指南

**创建日期**: 2026-02-28  
**状态**: ✅ 支持接入

---

## 一、AIgocode 简介

**AIgocode** 是第三方 API 中转服务，提供：
- ✅ 多模型聚合 (OpenAI/Claude/国产模型等)
- ✅ 统一 API 接口 (OpenAI 兼容)
- ✅ 价格优惠 (通常比官方低)
- ✅ 国内访问速度快
- ✅ 支持中文支付

---

## 二、接入步骤

### 步骤 1: 获取 API Key

1. 访问 AIgocode 官网：https://api.aigocode.cn
2. 注册/登录账号
3. 进入控制台 → API 管理
4. 创建新的 API Key
5. 复制保存 API Key

---

### 步骤 2: 配置 OpenClaw

**方法 A: 修改 openclaw.json**

编辑 `~/.openclaw/openclaw.json`：

```json
{
  "models": {
    "default": "aigocode/gpt-4o",
    "providers": {
      "aigocode": {
        "baseUrl": "https://api.aigocode.cn/v1",
        "apiKey": "你的 AIgocode API Key",
        "apiType": "openai-completions",
        "models": [
          "gpt-4o",
          "gpt-4o-mini",
          "gpt-4-turbo",
          "claude-3-5-sonnet",
          "qwen-plus",
          "deepseek-chat"
        ]
      }
    },
    "failover": {
      "enabled": true,
      "maxRetries": 3,
      "timeout": 30000,
      "fallbacks": ["aigocode/gpt-4o-mini", "aigocode/qwen-plus"]
    }
  }
}
```

**方法 B: 使用配置文件**

将 `config/models/aigocode_provider.json` 复制到：
```
~/.openclaw/models.providers/aigocode.json
```

然后修改 API Key。

---

### 步骤 3: 测试连接

**命令行测试**:

```bash
# 测试 AIgocode 连接
curl -X POST https://api.aigocode.cn/v1/chat/completions \
  -H "Authorization: Bearer 你的 API Key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

**OpenClaw 测试**:

```bash
# 使用 AIgocode 模型对话
openclaw agent --model aigocode/gpt-4o --message "测试"
```

---

### 步骤 4: 重启 Gateway

```bash
cd D:\openclaw
node openclaw.mjs gateway restart
```

---

## 三、可用模型列表

### OpenAI 系列

| 模型 ID | 名称 | 上下文 | 价格 (输入/输出) |
|--------|------|--------|----------------|
| gpt-4o | GPT-4o | 128K | $0.005/$0.015 per K |
| gpt-4o-mini | GPT-4o Mini | 128K | $0.00015/$0.0006 per K |
| gpt-4-turbo | GPT-4 Turbo | 128K | $0.01/$0.03 per K |
| gpt-3.5-turbo | GPT-3.5 Turbo | 16K | $0.0005/$0.0015 per K |

### Claude 系列

| 模型 ID | 名称 | 上下文 | 价格 (输入/输出) |
|--------|------|--------|----------------|
| claude-3-5-sonnet | Claude 3.5 Sonnet | 200K | $0.003/$0.015 per K |
| claude-3-opus | Claude 3 Opus | 200K | $0.015/$0.075 per K |

### 国产模型

| 模型 ID | 名称 | 上下文 | 价格 (输入/输出) |
|--------|------|--------|----------------|
| qwen-plus | 通义千问 Plus | 256K | ¥0.004/¥0.012 per K |
| qwen-max | 通义千问 Max | 256K | ¥0.04/¥0.12 per K |
| deepseek-chat | DeepSeek Chat | 128K | ¥0.001/¥0.004 per K |
| deepseek-coder | DeepSeek Coder | 128K | ¥0.001/¥0.002 per K |
| glm-4-plus | 智谱 GLM-4 Plus | 128K | ¥0.05/¥0.05 per K |
| kimi-plus | Kimi Plus | 200K | ¥0.04/¥0.12 per K |

---

## 四、推荐配置

### 日常使用

```json
{
  "models": {
    "default": "aigocode/gpt-4o-mini",
    "providers": {
      "aigocode": {
        "baseUrl": "https://api.aigocode.cn/v1",
        "apiKey": "你的 API Key"
      }
    }
  }
}
```

**说明**: GPT-4o Mini 性价比高，适合日常任务

---

### 高质量任务

```json
{
  "models": {
    "default": "aigocode/claude-3-5-sonnet",
    "providers": {
      "aigocode": {
        "baseUrl": "https://api.aigocode.cn/v1",
        "apiKey": "你的 API Key"
      }
    }
  }
}
```

**说明**: Claude 3.5 Sonnet 能力强，适合复杂任务

---

### 代码开发

```json
{
  "models": {
    "default": "aigocode/deepseek-coder",
    "providers": {
      "aigocode": {
        "baseUrl": "https://api.aigocode.cn/v1",
        "apiKey": "你的 API Key"
      }
    }
  }
}
```

**说明**: DeepSeek Coder 代码能力强，价格便宜

---

### 多模型故障转移

```json
{
  "models": {
    "default": "aigocode/gpt-4o",
    "providers": {
      "aigocode": {
        "baseUrl": "https://api.aigocode.cn/v1",
        "apiKey": "你的 API Key"
      }
    },
    "failover": {
      "enabled": true,
      "maxRetries": 3,
      "timeout": 30000,
      "fallbacks": [
        "aigocode/gpt-4o-mini",
        "aigocode/qwen-plus",
        "aigocode/deepseek-chat"
      ]
    }
  }
}
```

**说明**: 主模型失败时自动切换到备用模型

---

## 五、价格对比

### AIgocode vs 官方

| 模型 | 官方价格 | AIgocode 价格 | 节省 |
|------|---------|-------------|------|
| GPT-4o | $0.005/$0.015 | $0.004/$0.012 | 约 20% |
| Claude 3.5 | $0.003/$0.015 | $0.0025/$0.012 | 约 17% |
| Qwen-Plus | ¥0.004/¥0.012 | ¥0.003/¥0.010 | 约 25% |
| DeepSeek | ¥0.001/¥0.004 | ¥0.0008/¥0.003 | 约 20% |

**注**: 价格为参考，实际以 AIgocode 官网为准

---

## 六、常见问题

### Q1: API Key 在哪里获取？

**A**: 登录 AIgocode 控制台 → API 管理 → 创建 API Key

---

### Q2: 如何查看余额？

**A**: 登录 AIgocode 控制台 → 账户管理 → 余额查询

---

### Q3: 支持哪些支付方式？

**A**: 通常支持支付宝、微信、银行卡等（以官网为准）

---

### Q4: 国内访问速度慢怎么办？

**A**: 
1. 检查网络连接
2. 联系 AIgocode 客服
3. 考虑使用本地模型作为备用

---

### Q5: 如何设置模型切换？

**A**: 在 openclaw.json 中修改 `models.default` 字段

---

### Q6: 故障转移如何配置？

**A**: 在 openclaw.json 中配置 `models.failover` 字段

---

## 七、监控与告警

### 使用量监控

```bash
# 查看 AIgocode 使用量
curl https://api.aigocode.cn/v1/usage \
  -H "Authorization: Bearer 你的 API Key"
```

### 余额告警

建议设置余额告警：
- 余额 < 100 元：邮件通知
- 余额 < 50 元：短信通知
- 余额 < 10 元：紧急通知

---

## 八、安全建议

1. **保护 API Key**
   - 不要提交到 Git
   - 使用环境变量
   - 定期轮换

2. **设置使用限制**
   - 配置 RPM/TPM 限制
   - 设置月度预算
   - 启用异常检测

3. **监控异常使用**
   - 定期检查使用日志
   - 设置异常告警
   - 及时发现盗用

---

## 九、参考资料

- **AIgocode 官网**: https://api.aigocode.cn
- **AIgocode 文档**: https://docs.aigocode.cn
- **OpenClaw 模型配置**: https://docs.openclaw.ai/gateway/models
- **OpenClaw 故障转移**: https://docs.openclaw.ai/gateway/model-failover

---

## 十、快速开始

```bash
# 1. 获取 AIgocode API Key
# 访问 https://api.aigocode.cn 注册获取

# 2. 编辑 openclaw.json
nano ~/.openclaw/openclaw.json

# 3. 添加 AIgocode 配置
# 参考上面配置示例

# 4. 测试连接
openclaw agent --model aigocode/gpt-4o-mini --message "测试"

# 5. 重启 Gateway
cd D:\openclaw
node openclaw.mjs gateway restart
```

---

**配置完成时间**: 2026-02-28  
**配置状态**: 等待用户填入 API Key

需要我帮你修改 openclaw.json 配置文件吗？👍
