# OpenClaw 官方支持的模型列表 (2026)

**更新日期**: 2026-02-28  
**来源**: OpenClaw 官方文档

---

## 一、主要模型提供商

### 1. Anthropic (Claude 系列) ⭐ 推荐

| 模型 | 上下文 | 输入价格 | 输出价格 | 说明 |
|------|--------|---------|---------|------|
| **Claude 3.7 Sonnet** | 200K | $3/M | $15/M | 最新旗舰，性价比高 |
| **Claude 3.5 Sonnet** | 200K | $3/M | $15/M | 主力推荐 |
| **Claude 3 Opus** | 200K | $15/M | $75/M | 最强能力，长上下文 |
| **Claude 3 Haiku** | 200K | $0.25/M | $1.25/M | 快速便宜 |

**推荐配置**:
```json
{
  "provider": "anthropic",
  "apiKey": "sk-ant-xxx",
  "models": ["claude-3-7-sonnet", "claude-3-5-sonnet"]
}
```

---

### 2. OpenAI (GPT 系列)

| 模型 | 上下文 | 输入价格 | 输出价格 | 说明 |
|------|--------|---------|---------|------|
| **GPT-5.2** | 128K | $10/M | $30/M | 最新旗舰 |
| **GPT-4o** | 128K | $5/M | $15/M | 主力模型 |
| **GPT-4o-mini** | 128K | $0.15/M | $0.60/M | 经济实惠 |
| **GPT-4-Turbo** | 128K | $10/M | $30/M | 快速响应 |
| **o1** | 128K | $15/M | $60/M | 推理专用 |
| **o3-mini** | 128K | $1.10/M | $4.40/M | 轻量推理 |

**推荐配置**:
```json
{
  "provider": "openai",
  "apiKey": "sk-xxx",
  "models": ["gpt-4o", "gpt-4o-mini"]
}
```

---

### 3. Google (Gemini 系列)

| 模型 | 上下文 | 输入价格 | 输出价格 | 说明 |
|------|--------|---------|---------|------|
| **Gemini 3 Pro Preview** | 1M+ | $7/M | $21/M | 最强多模态 |
| **Gemini 3 Flash Preview** | 1M+ | $0.35/M | $1.05/M | 快速便宜 |
| **Gemini 2.5 Pro** | 1M+ | $3.50/M | $10.50/M | 主力模型 |
| **Gemini 2.0 Flash** | 1M+ | $0.10/M | $0.40/M | 经济实惠 |

**推荐配置**:
```json
{
  "provider": "google",
  "apiKey": "xxx",
  "models": ["gemini-3-pro-preview", "gemini-2.5-pro"]
}
```

---

### 4. 阿里云 (通义千问系列) 🇨🇳

| 模型 | 上下文 | 输入价格 | 输出价格 | 说明 |
|------|--------|---------|---------|------|
| **Qwen3.5-Plus** | 256K | ¥0.014/K | ¥0.042/K | 主力推荐 |
| **Qwen3.5-Turbo** | 256K | ¥0.002/K | ¥0.006/K | 经济实惠 |
| **Qwen-Max** | 256K | ¥0.04/K | ¥0.12/K | 最强能力 |
| **Qwen-Plus** | 256K | ¥0.004/K | ¥0.012/K | 性价比 |

**推荐配置**:
```json
{
  "provider": "bailian",
  "apiKey": "sk-xxx",
  "models": ["qwen3.5-plus", "qwen-max"]
}
```

---

### 5. DeepSeek (深度求索) 🇨🇳

| 模型 | 上下文 | 输入价格 | 输出价格 | 说明 |
|------|--------|---------|---------|------|
| **DeepSeek-V3** | 128K | ¥0.001/K | ¥0.004/K | 主力模型 |
| **DeepSeek-R1** | 128K | ¥0.004/K | ¥0.016/K | 推理专用 |
| **DeepSeek-Coder** | 128K | ¥0.001/K | ¥0.002/K | 代码专用 |

**推荐配置**:
```json
{
  "provider": "deepseek",
  "apiKey": "sk-xxx",
  "models": ["deepseek-chat", "deepseek-coder"]
}
```

---

### 6. MiniMax

| 模型 | 上下文 | 输入价格 | 输出价格 | 说明 |
|------|--------|---------|---------|------|
| **MiniMax M2.5** | 256K | ¥0.001/K | ¥0.001/K | 免费额度 |
| **MiniMax-01** | 256K | ¥0.005/K | ¥0.02/K | 主力模型 |

---

### 7. 智谱 AI (GLM 系列) 🇨🇳

| 模型 | 上下文 | 输入价格 | 输出价格 | 说明 |
|------|--------|---------|---------|------|
| **GLM-5 Free** | 128K | 免费 | 免费 | 免费额度 |
| **GLM-4-Plus** | 128K | ¥0.05/K | ¥0.05/K | 主力模型 |
| **GLM-4-Flash** | 128K | ¥0.001/K | ¥0.001/K | 快速便宜 |

---

### 8. 月之暗面 (Kimi 系列) 🇨🇳

| 模型 | 上下文 | 输入价格 | 输出价格 | 说明 |
|------|--------|---------|---------|------|
| **Kimi K2.5** | 200K+ | ¥0.024/K | ¥0.072/K | 主力模型 |
| **Kimi Plus** | 200K+ | ¥0.04/K | ¥0.12/K | 长上下文 |

---

### 9. xAI (Grok 系列)

| 模型 | 上下文 | 输入价格 | 输出价格 | 说明 |
|------|--------|---------|---------|------|
| **Grok-3** | 128K | $5/M | $15/M | 最新旗舰 |
| **Grok-2** | 128K | $2/M | $10/M | 主力模型 |
| **Grok Code Fast** | 128K | $0.5/M | $2/M | 代码专用 |

---

### 10. 其他提供商

| 提供商 | 模型 | 说明 |
|--------|------|------|
| **Meta** | Llama 3.1/3.2 | 开源模型 |
| **Mistral** | Mistral Large | 欧洲模型 |
| **Cohere** | Command R+ | 企业级 |
| **Databricks** | DBRX | 开源模型 |
| **Together AI** | 多模型 | 聚合平台 |
| **Groq** | LPU 推理 | 超快响应 |
| **Fireworks** | 多模型 | 聚合平台 |

---

## 二、聚合平台

### 1. OpenRouter

**支持模型**: 100+ 个模型聚合

**价格**: 按模型不同，从免费到$50/M

**推荐配置**:
```json
{
  "provider": "openrouter",
  "apiKey": "sk-or-xxx",
  "models": ["anthropic/claude-3.5-sonnet", "openai/gpt-4o"]
}
```

**优势**:
- ✅ 一个 API 访问所有模型
- ✅ 自动故障转移
- ✅ 统一计费

---

### 2. AIMLAPI

**支持模型**: OpenAI/Claude/Google 等

**推荐配置**:
```json
{
  "provider": "aimlapi",
  "apiKey": "xxx",
  "models": ["gpt-4o", "claude-3-5-sonnet"]
}
```

---

### 3. Hugging Face Inference

**支持模型**: 开源模型为主

**推荐配置**:
```json
{
  "provider": "huggingface",
  "apiKey": "hf_xxx",
  "models": ["deepseek-ai/DeepSeek-R1"]
}
```

---

## 三、本地模型

### 1. Ollama

**支持模型**: Llama/Mistral/Qwen 等开源模型

**推荐配置**:
```json
{
  "provider": "ollama",
  "baseUrl": "http://127.0.0.1:11434",
  "models": ["llama3.1", "qwen2.5"]
}
```

**优势**:
- ✅ 完全免费
- ✅ 本地运行，隐私保护
- ✅ 无 API 限制

---

### 2. vLLM

**支持模型**: 自定义开源模型

**推荐配置**:
```json
{
  "provider": "vllm",
  "baseUrl": "http://127.0.0.1:8000",
  "models": ["meta-llama/Llama-3.1-70B"]
}
```

---

### 3. LM Studio

**支持模型**: 本地 GGUF 模型

**推荐配置**:
```json
{
  "provider": "lmstudio",
  "baseUrl": "http://127.0.0.1:1234",
  "models": ["local-model"]
}
```

---

### 4. LiteLLM

**支持模型**: 统一接口代理

**推荐配置**:
```json
{
  "provider": "litellm",
  "baseUrl": "http://127.0.0.1:4000",
  "models": ["*"]
}
```

---

## 四、模型推荐

### 按任务类型推荐

| 任务类型 | 推荐模型 | 理由 |
|---------|---------|------|
| **日常助手** | Claude 3.5 Sonnet | 平衡性能和成本 |
| **代码开发** | Claude 3.5/Claude Code | 代码能力强 |
| **长文档分析** | Claude 3 Opus | 200K 上下文 |
| **快速响应** | GPT-4o-mini / Qwen-Turbo | 便宜快速 |
| **复杂推理** | o1 / DeepSeek-R1 | 推理专用 |
| **多模态** | Gemini 3 Pro | 图像/视频理解 |
| **中文任务** | Qwen3.5-Plus | 中文优化 |
| **免费方案** | GLM-5 Free / MiniMax M2.5 | 免费额度 |

---

### 按预算推荐

| 预算 | 推荐配置 | 月成本估算 |
|------|---------|-----------|
| **免费** | GLM-5 Free + MiniMax M2.5 | ¥0 |
| **低成本** | Qwen-Turbo + DeepSeek-V3 | ¥100-500 |
| **中等** | Claude 3.5 Sonnet | ¥500-2000 |
| **高端** | Claude 3 Opus + GPT-5.2 | ¥2000+ |

---

## 五、配置示例

### 完整配置 (openclaw.json)

```json
{
  "models": {
    "default": "qwen3.5-plus",
    "providers": {
      "anthropic": {
        "apiKey": "sk-ant-xxx",
        "models": ["claude-3-7-sonnet", "claude-3-5-sonnet"]
      },
      "openai": {
        "apiKey": "sk-xxx",
        "models": ["gpt-4o", "gpt-4o-mini"]
      },
      "bailian": {
        "apiKey": "sk-xxx",
        "models": ["qwen3.5-plus", "qwen-max"]
      },
      "deepseek": {
        "apiKey": "sk-xxx",
        "models": ["deepseek-chat", "deepseek-coder"]
      },
      "openrouter": {
        "apiKey": "sk-or-xxx",
        "models": ["anthropic/claude-3.5-sonnet"]
      },
      "ollama": {
        "baseUrl": "http://127.0.0.1:11434",
        "models": ["llama3.1", "qwen2.5"]
      }
    },
    "failover": {
      "enabled": true,
      "maxRetries": 3,
      "timeout": 30000,
      "fallbacks": ["qwen-plus", "qwen-turbo"]
    }
  }
}
```

---

## 六、价格对比

### 每百万 Token 价格 (人民币)

| 模型 | 输入 | 输出 | 性价比 |
|------|------|------|--------|
| GLM-5 Free | ¥0 | ¥0 | ⭐⭐⭐⭐⭐ |
| MiniMax M2.5 | ¥0 | ¥0 | ⭐⭐⭐⭐⭐ |
| DeepSeek-V3 | ¥1 | ¥4 | ⭐⭐⭐⭐ |
| Qwen-Turbo | ¥2 | ¥6 | ⭐⭐⭐⭐ |
| GPT-4o-mini | ¥1.05 | ¥4.2 | ⭐⭐⭐⭐ |
| Qwen-Plus | ¥4 | ¥12 | ⭐⭐⭐ |
| Claude 3.5 Sonnet | ¥21 | ¥105 | ⭐⭐⭐ |
| GPT-4o | ¥35 | ¥105 | ⭐⭐ |
| Qwen-Max | ¥40 | ¥120 | ⭐⭐ |
| Claude 3 Opus | ¥105 | ¥525 | ⭐ |

---

## 七、参考资料

- **官方文档**: https://docs.openclaw.ai/concepts/model-providers
- **模型配置指南**: https://docs.openclaw.ai/gateway/models
- **OpenRouter 集成**: https://openrouter.ai/docs/guides/openclaw-integration
- **最佳模型推荐**: https://haimaker.ai/blog/best-models-for-clawdbot/

---

**更新日期**: 2026-02-28  
**下次更新**: 2026-03-31 (或根据官方更新)
