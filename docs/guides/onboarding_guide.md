# Leo AI Onboarding 向导指南

**创建时间**: 2026-02-27  
**状态**: ✅ 配置框架完成

---

## 一、快速开始

### 步骤 1: 检查环境

```bash
# 检查 Node.js 版本 (需要 >=22)
node --version

# 检查 OpenClaw 版本
openclaw --version
```

### 步骤 2: 运行 onboard 向导

```bash
# 启动 onboarding
cd D:\桌面\leo_ai_system
python scripts\onboard\wizard.py
```

### 步骤 3: 配置向导

向导会引导您完成：
1. 选择模型 Provider
2. 配置 API Keys
3. 选择消息渠道
4. 安装初始 Skills
5. 启动 Gateway

---

## 二、配置检查清单

### 必需配置

- [ ] Node.js >= 22
- [ ] Python >= 3.11
- [ ] OpenClaw 已安装
- [ ] 模型 API Key 已配置

### 可选配置

- [ ] 消息渠道 (Feishu/WhatsApp/Telegram)
- [ ] Browser 工具 (Playwright)
- [ ] TTS 服务 (Edge TTS)

---

## 三、故障排查

### 问题 1: Node.js 版本过低

**解决**:
```bash
# 升级到 Node.js 22+
# Windows: 下载 https://nodejs.org/
# macOS: brew install node@22
```

### 问题 2: OpenClaw 未安装

**解决**:
```bash
npm install -g openclaw@latest
```

---

## 四、验收标准

- [x] Onboarding 文档已创建
- [ ] onboard 脚本可执行
- [ ] 配置向导可运行
- [ ] Gateway 可启动

---

*配置完成时间：2026-02-27*
