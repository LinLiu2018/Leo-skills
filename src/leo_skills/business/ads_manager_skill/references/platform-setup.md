# 广告平台设置指南

## Facebook Ads

### 账户准备
1. 创建 Business Manager
2. 添加广告账户
3. 设置像素追踪

### API 认证
```python
from facebook_business.api import FacebookAdsApi
FacebookAdsApi.init(
    app_id='YOUR_APP_ID',
    app_secret='YOUR_APP_SECRET',
    access_token='YOUR_ACCESS_TOKEN'
)
```

## Google Ads

### 账户准备
1. 创建 Google Ads 账户
2. 关联 Google Analytics
3. 设置转化追踪

### API 认证
```python
from google.ads.googleads.client import GoogleAdsClient
client = GoogleAdsClient.load_from_storage(
    "googleads_config.yaml"
)
```

## 预算分配建议

| 渠道 | 新手 | 进阶 | 成熟 |
|------|------|------|------|
| Facebook | 3000 元/天 | 10000 元/天 | 50000+ 元/天 |
| Google | 2000 元/天 | 8000 元/天 | 30000+ 元/天 |
| 小红书 | 1000 元/天 | 5000 元/天 | 20000+ 元/天 |
