# OpenClaw (大龙虾) 集成配置指南

> **官方仓库**: https://github.com/openclaw/openclaw
> **当前版本**: v2026.1.30

## 架构说明

```
飞书用户
    ↓
飞书开放平台 (WebSocket 长连接)
    ↓
OpenClaw Gateway (D:\moltbot)
    ↓
Leo AI System (本系统)
    ↓
返回结果给 OpenClaw
    ↓
飞书聊天窗口
```

## 配置步骤

### 1. Leo 系统启动服务

创建启动脚本供 OpenClaw 调用：

**scripts/start_leo_service.bat**
```batch
@echo off
cd /d "d:\桌面\leo_ai_system"
python src\leo_interface\web\app.py
```

### 2. OpenClaw 配置

在 `C:\Users\刘方林\.openclaw\openclaw.json` 中添加 Leo 系统通道：

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "app_id": "cli_xxx",
      "app_secret": "xxx"
    },
    "leo_system": {
      "enabled": true,
      "type": "local",
      "base_url": "http://localhost:5000",
      "skills_endpoint": "/api/skills",
      "agents_endpoint": "/api/agents",
      "workflows_endpoint": "/api/workflows"
    }
  },
  "routing": {
    "default": "leo_system",
    "rules": [
      {
        "keywords": ["研究", "调研", "分析"],
        "target": "leo_system",
        "agent": "research_agent"
      },
      {
        "keywords": ["房产", "楼盘", "营销"],
        "target": "leo_system",
        "agent": "realestate_agent"
      },
      {
        "keywords": ["创作", "写作", "文案"],
        "target": "leo_system",
        "agent": "creative_agent"
      }
    ]
  }
}
```

### 3. 飞书快捷指令配置

在飞书开放平台配置机器人菜单：

| 命令 | 功能 | 对应Agent |
|------|------|-----------|
| `/研究 <主题>` | 调研分析 | research_agent |
| `/房产 <项目>` | 房产报告 | realestate_agent |
| `/创作 <需求>` | 内容创作 | creative_agent |
| `/分析 <数据>` | 数据分析 | analysis_agent |

### 4. Leo 系统接口

确保 `src/leo_interface/web/app.py` 提供以下接口：

```python
@app.route('/api/agents/<agent_name>', methods=['POST'])
def call_agent(agent_name):
    """调用指定Agent"""
    data = request.json
    task = data.get('task', '')
    # 调用对应Agent
    return jsonify({"status": "completed", "result": "..."})

@app.route('/api/skills/<skill_name>', methods=['POST'])
def call_skill(skill_name):
    """调用指定Skill"""
    data = request.json
    # 调用对应Skill
    return jsonify({"status": "completed", "result": "..."})

@app.route('/api/workflows/<workflow_name>', methods=['POST'])
def call_workflow(workflow_name):
    """调用指定Workflow"""
    data = request.json
    # 调用对应Workflow
    return jsonify({"status": "completed", "result": "..."})
```

### 5. 启动顺序

1. 启动 Leo 系统服务
   ```batch
   scripts/start_leo_service.bat
   ```

2. 启动 OpenClaw Gateway
   ```batch
   cd D:\moltbot
   node openclaw.mjs gateway --port 18789
   ```

   或使用守护进程：
   ```batch
   scripts\一键启动大龙虾_带守护.bat
   ```

3. 在飞书中测试
   ```
   @机器人 /研究 宁波房地产市场
   ```

## 故障排查

### 检查服务状态

```batch
# 检查 Leo 服务
curl http://localhost:5000/health

# 检查 OpenClaw 状态
cd D:\moltbot
node openclaw.mjs channels status
```

### 常见问题

1. **飞书收不到回复**
   - 检查 OpenClaw Gateway 是否运行
   - 检查飞书机器人 Webhook 配置

2. **Leo 系统无响应**
   - 检查 `app.py` 是否在运行
   - 检查端口 5000 是否被占用

3. **代理选择错误**
   - 检查 `openclaw.json` 中的 routing 规则
   - 检查关键词匹配是否正确

## 测试命令

```
/研究 宁波房地产市场
/房产 淮安建华官园项目
/创作 写一篇房产营销软文
/分析 最近3个月销售数据
```
