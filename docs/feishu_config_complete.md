# 飞书应用配置完成

## 已完成的配置

**OpenClaw 配置**: `C:\Users\刘方林\.openclaw\openclaw.json`

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "cli_a9f18849edbb9cb1",
      "appSecret": "UUNNVCiRRheoPkdnKPeVycYTTlVQ8emS",
      "domain": "feishu",
      "connectionMode": "websocket",
      "dmPolicy": "open",
      "groupPolicy": "open",
      "requireMention": false
    }
  }
}
```

## 待完成：飞书开放平台配置

### 1. 登录飞书开放平台
访问: https://open.feishu.cn

### 2. 配置事件订阅

在应用管理页面，点击「事件与回调」:

#### 添加事件订阅（必选）
| 事件 | 说明 |
|-----|------|
| `im.message.receive_v1` | 接收消息（必须） |
| `im.chat.member.bot.added_v1` | 机器人加入群聊 |
| `im.chat.member.bot.deleted_v1` | 机器人被移出群聊 |

#### 配置事件接收方式
- **方式**: 选择「使用长连接接收事件/回调」
- **回调 URL**: 可留空（WebSocket 模式自动连接）

### 3. 发布应用
在「版本管理与发布」页面创建版本并发布。

### 4. 添加机器人到群聊
在飞书中搜索机器人并添加到群聊。

---

## 测试命令

```bash
# 查看状态
cd D:\moltbot && node openclaw.mjs status

# 查看通道详情
node openclaw.mjs channels list

# 查看日志
node openclaw.mjs logs
```

## 当前状态
- OpenClaw Gateway: 运行中
- 飞书通道: 已配置，WebSocket 连接正常
