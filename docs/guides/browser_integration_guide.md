# Browser 完整集成指南

**目标**: 实现 OpenClaw 官方 Browser 工具完整功能

---

## 一、OpenClaw Browser 能力

### 官方功能清单

| 功能 | 说明 | 状态 |
|------|------|------|
| **snapshot** | 网页快照 (ARIA/AI) | ⏳ 待实现 |
| **actions** | 点击/输入/导航 | ⏳ 待实现 |
| **upload** | 文件上传 | ⏳ 待实现 |
| **profiles** | 浏览器配置 | ⏳ 待实现 |
| **console** | 控制台日志 | ⏳ 待实现 |
| **pdf** | PDF 导出 | ⏳ 待实现 |

---

## 二、实施方案

### 方案 1: 集成 OpenClaw Browser (推荐)

**步骤**:

```bash
# 1. 确认 OpenClaw 已安装
openclaw --version

# 2. 配置 Browser
openclaw browser install

# 3. 测试 Browser
openclaw browser snapshot https://example.com
```

**配置** (`~/.openclaw/openclaw.json`):

```json
{
  "browser": {
    "provider": "openclaw",
    "headless": false,
    "timeout": 30000,
    "viewport": {
      "width": 1280,
      "height": 720
    }
  }
}
```

### 方案 2: Playwright 集成

**步骤**:

```bash
# 1. 安装 Playwright
pip install playwright
playwright install

# 2. 创建 Browser Skill
mkdir -p src/leo_skills/tools/browser_skill
```

---

## 三、验收测试

### 测试用例

```python
def test_browser_snapshot():
    """测试网页快照"""
    result = browser.snapshot("https://example.com")
    assert result["status"] == "success"
    assert "html" in result

def test_browser_actions():
    """测试浏览器操作"""
    browser.navigate("https://example.com")
    browser.click("#button")
    browser.type("#input", "test")
```

---

*创建时间：2026-02-27*
