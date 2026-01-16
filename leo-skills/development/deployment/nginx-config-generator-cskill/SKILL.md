# Nginx配置生成器 Skill

## 技能描述

生成Nginx配置文件，支持反向代理、SSL、负载均衡、WebSocket等。

## 激活词

- "生成Nginx配置"
- "创建Nginx配置"
- "配置反向代理"

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| domain | string | 是 | 域名 |
| upstream_servers | list | 否 | 上游服务器列表 |
| ssl_enabled | bool | 否 | 是否启用SSL |
| features | list | 否 | 特性（gzip/cache/websocket/rate_limit） |

## 输出

- `domain.conf` - 站点配置
- `ssl-params.conf` - SSL参数（如启用）
- `common.conf` - 通用配置

## 使用示例

### 示例1：基础配置

```
生成Nginx配置
域名：api.example.com
上游服务器：localhost:5000
```

### 示例2：生产环境配置

```
生成Nginx配置
域名：www.example.com
上游服务器：
  - app1:5000 (权重2)
  - app2:5000 (权重1)
启用SSL：是
特性：gzip, cache, websocket
```

## 版本

- 版本: 1.0.0
- 作者: Leo Liu
- 更新: 2026-01-14
