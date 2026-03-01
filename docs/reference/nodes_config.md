# Nodes 设备节点配置

**创建时间**: 2026-02-27  
**状态**: ✅ 配置框架完成

---

## 一、Nodes 能力清单

### 核心功能

| 功能 | 说明 | 状态 |
|------|------|------|
| **Camera Snap** | 相机拍照 | ⏳ 待实施 |
| **Camera Clip** | 相机录像 | ⏳ 待实施 |
| **Screen Record** | 屏幕录制 | ⏳ 待实施 |
| **Location.get** | 获取位置 | ⏳ 待实施 |
| **Notifications** | 系统通知 | ⏳ 待实施 |

---

## 二、配置说明

### openclaw.json

```json
{
  "nodes": {
    "enabled": true,
    "camera": {
      "enabled": false,
      "defaultDevice": "back"
    },
    "screen": {
      "enabled": false,
      "fps": 30
    },
    "location": {
      "enabled": false,
      "accuracy": "balanced"
    },
    "notifications": {
      "enabled": true,
      "sound": true
    }
  }
}
```

---

## 三、实施步骤

1. 安装设备节点依赖
2. 配置各节点参数
3. 测试各节点功能
4. 集成到 Agent

---

## 四、验收标准

- [x] Nodes 配置文档已创建
- [ ] Camera Snap/Clip 可用
- [ ] Screen Record 可用
- [ ] Location.get 可用
- [ ] Notifications 可用

---

*配置完成时间：2026-02-27*
