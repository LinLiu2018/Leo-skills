# 微信公众号API配置指南

## 配置步骤

### 1. 获取微信公众号凭证

访问 [微信公众平台](https://mp.weixin.qq.com/)

1. 登录微信公众号后台
2. 进入"开发" → "基本配置"
3. 获取以下信息:
   - AppID (应用ID)
   - AppSecret (应用密钥)

### 2. 配置到系统

编辑 `src/leo_config/settings/config.yaml`:

```yaml
# 微信公众号配置
wechat:
  appid: "YOUR_WECHAT_APPID"
  secret: "YOUR_WECHAT_SECRET"
  token: "YOUR_TOKEN"  # 可选，用于服务器验证
  encoding_aes_key: "YOUR_AES_KEY"  # 可选，用于消息加密
```

### 3. 配置环境变量（推荐）

为了安全，建议使用环境变量:

```bash
# Windows
set WECHAT_APPID=your_appid
set WECHAT_SECRET=your_secret

# Linux/Mac
export WECHAT_APPID=your_appid
export WECHAT_SECRET=your_secret
```

### 4. MiniMax AI配置

编辑 `src/leo_config/settings/config.yaml`:

```yaml
# MiniMax AI配置
minimax:
  api_key: "YOUR_MINIMAX_API_KEY"
  base_url: "https://api.minimax.chat/v1"
  model: "abab5.5-chat"
```

环境变量方式:

```bash
# Windows
set MINIMAX_API_KEY=your_api_key
set MINIMAX_BASE_URL=https://api.minimax.chat/v1

# Linux/Mac
export MINIMAX_API_KEY=your_api_key
export MINIMAX_BASE_URL=https://api.minimax.chat/v1
```

### 5. 验证配置

运行验证脚本:

```bash
python -c "
import os
from src.leo_config.settings import config

# 检查微信配置
wechat_appid = os.getenv('WECHAT_APPID') or config.get('wechat', {}).get('appid')
print(f'微信AppID: {wechat_appid[:10]}...' if wechat_appid else '未配置')

# 检查MiniMax配置
minimax_key = os.getenv('MINIMAX_API_KEY') or config.get('minimax', {}).get('api_key')
print(f'MiniMax Key: {minimax_key[:10]}...' if minimax_key else '未配置')
"
```

## 使用示例

### 发布文章到公众号

```python
from leo_skills.content_creation.realestate_news_publisher_skill import RealEstateNewsPublisher

publisher = RealEstateNewsPublisher()
result = publisher.execute(
    action="publish",
    title="2026年房地产市场展望",
    content="...",
    platform="wechat"
)
```

### 使用MiniMax生成文章

```python
result = publisher.execute(
    action="generate",
    topic="宁波房地产市场分析",
    style="professional"
)
```

## 注意事项

1. **安全性**: 不要将API密钥提交到Git仓库
2. **权限**: 确保公众号有发布文章的权限
3. **限流**: 注意API调用频率限制
4. **测试**: 先在测试环境验证配置

## 故障排查

### 问题1: 获取access_token失败

```
错误: invalid appid
解决: 检查WECHAT_APPID是否正确
```

### 问题2: MiniMax API调用失败

```
错误: invalid api key
解决: 检查MINIMAX_API_KEY是否正确配置
```

### 问题3: 文章发布失败

```
错误: no permission
解决: 检查公众号是否有发布权限
```

## 相关文档

- [微信公众平台开发文档](https://developers.weixin.qq.com/doc/)
- [MiniMax API文档](https://api.minimax.chat/document)
