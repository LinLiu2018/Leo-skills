# 飞书应用创建指南

## 1. 创建飞书开放平台应用

### 步骤 1: 访问飞书开放平台
- 中国版: https://open.feishu.cn
- 国际版: https://open.larksuite.com
- 登录你的飞书账号

### 步骤 2: 创建企业自建应用
1. 点击「创建企业自建应用」
2. 输入应用名称: `LeoAI_Bot`
3. 上传应用图标（可选）
4. 点击「确定创建」

### 步骤 3: 获取凭证
在应用详情页的「凭证与权限」页面：
- **App ID (应用 ID)**: 记录下来
- **App Secret (应用密钥)**: 点击「获取 App Secret」并记录

### 步骤 4: 配置权限
在「凭证与权限」页面，添加以下权限：

| 权限名称 | 权限说明 |
|---------|---------|
| `contact:user.base:readonly` | 获取用户基本信息 |
| `im:message` | 发送和接收消息 |
| `im:message.p2p_msg:readonly` | 读取机器人私聊消息 |
| `im:message.group_at_msg:readonly` | 读取群聊中@机器人的消息 |
| `im:message:send_as_bot` | 以机器人身份发送消息 |
| `im:resource` | 上传和下载图片/文件 |

点击「申请权限」并确认。

### 步骤 5: 配置事件订阅
在「事件与回调」页面：

1. **事件配置方式**: 选择「使用长连接接收事件/回调」(WebSocket 模式)
2. **添加事件订阅**:

需要订阅的事件：
| 事件名称 | 说明 |
|---------|------|
| `im.message.receive_v1` | 接收消息（必选） |
| `im.message.message_read_v1` | 消息已读回执 |
| `im.chat.member.bot.added_v1` | 机器人加入群聊 |
| `im.chat.member.bot.deleted_v1` | 机器人被移出群聊 |

### 步骤 6: 发布应用
1. 在「版本管理与发布」页面点击「创建版本」
2. 填写版本号和更新说明
3. 点击「保存并发布」

---

## 2. 配置 OpenClaw

运行以下命令配置飞书凭证：

```bash
cd D:\moltbot

# 设置 App ID
node openclaw.mjs config set channels.feishu.appId "YOUR_APP_ID"

# 设置 App Secret
node openclaw.mjs config set channels.feishu.appSecret "YOUR_APP_SECRET"

# 设置域名 (中国版用 feishu，国际版用 lark)
node openclaw.mjs config set channels.feishu.domain "feishu"

# 设置连接模式 (websocket 推荐)
node openclaw.mjs config set channels.feishu.connectionMode "websocket"

# 设置私聊策略 (open: 开放, pairing: 需要配对, allowlist: 白名单)
node openclaw.mjs config set channels.feishu.dmPolicy "open"

# 设置群聊策略
node openclaw.mjs config set channels.feishu.groupPolicy "open"

# 启用飞书通道
node openclaw.mjs config set channels.feishu.enabled true
```

---

## 3. 验证配置

```bash
# 检查配置
node openclaw.mjs doctor

# 启动网关
node openclaw.mjs gateway --port 18789
```

---

## 4. 常见问题

### Q: 机器人无法接收消息
A: 检查事件订阅配置，确保选择了「使用长连接接收事件/回调」。

### Q: 机器人无法发送消息
A: 检查 `im:message:send_as_bot` 权限是否已开通。

### Q: WebSocket 连接失败
A: 运行 `node openclaw.mjs doctor --fix` 修复配置。
