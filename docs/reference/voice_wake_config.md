# Voice Wake 语音唤醒配置

**创建时间**: 2026-02-27  
**状态**: ✅ 配置框架完成

---

## 一、语音唤醒功能

### 核心功能

| 功能 | 说明 | 状态 |
|------|------|------|
| **语音唤醒** | 说"Hey Leo"唤醒 | ⏳ 待实施 |
| **Talk Mode** | 持续对话模式 | ⏳ 待实施 |
| **语音命令** | 语音控制操作 | ⏳ 待实施 |

---

## 二、配置说明

### openclaw.json

```json
{
  "voice": {
    "wake": {
      "enabled": false,
      "keyword": "Hey Leo",
      "sensitivity": 0.7
    },
    "talk": {
      "enabled": false,
      "timeout": 30
    },
    "tts": {
      "provider": "edge",
      "voice": "zh-CN-XiaoxiaoNeural"
    }
  }
}
```

---

## 三、实施步骤

1. 安装语音识别依赖 (Porcupine/Snowboy)
2. 配置唤醒词
3. 测试语音唤醒
4. 配置 Talk Mode

---

## 四、验收标准

- [x] Voice Wake 配置文档已创建
- [ ] 语音唤醒可用
- [ ] Talk Mode 可用
- [ ] 语音命令可用

---

*配置完成时间：2026-02-27*
