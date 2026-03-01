"""
nginx_config_generator_skill

Nginx 配置生成技能 - 生成 Nginx 站点配置、SSL 参数和通用配置。
支持反向代理、SSL/TLS、Gzip 压缩、静态资源缓存、WebSocket、速率限制等特性。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from leo_skills.core.base_executor import BaseExecutor


class NginxConfigGenerator(BaseExecutor):
    """Nginx 配置生成器。

    根据域名和上游服务器信息自动生成：
    - site_config: 站点配置（upstream + server 块）
    - ssl_params: SSL/TLS 安全参数（可选）
    - common_params: 通用 Nginx 参数
    """

    def __init__(self, output_dir: str = ".") -> None:
        self.name = "nginx_config_generator_skill"
        self.output_dir = Path(output_dir)

    # ------------------------------------------------------------------
    # BaseExecutor 接口
    # ------------------------------------------------------------------

    def execute(
        self,
        action: str = "generate",
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """执行技能主入口。

        context / kwargs 支持的参数：
            domain (str): 域名（必须）
            upstream_servers (list[dict]): 上游服务器列表，每项包含 host / port / weight
            ssl_enabled (bool): 是否启用 SSL（默认 False）
            features (list[str]): 额外特性 (gzip / cache / websocket / rate_limit)
            save (bool): 是否保存到磁盘（默认 False）
        """
        params: Dict[str, Any] = dict(context or {})
        params.update(kwargs)

        domain = params.get("domain", "example.com")
        upstream_servers = params.get("upstream_servers", [
            {"host": "localhost", "port": 5000},
        ])
        ssl_enabled = params.get("ssl_enabled", False)
        features = params.get("features", [])

        results = self.generate(
            domain=domain,
            upstream_servers=upstream_servers,
            ssl_enabled=ssl_enabled,
            features=features,
        )

        # 可选：保存到磁盘
        saved_paths: Dict[str, str] = {}
        if params.get("save", False):
            saved = self.save_files(domain, results)
            saved_paths = {k: str(v) for k, v in saved.items()}

        return {
            "status": "success",
            "action": action,
            "domain": domain,
            "ssl_enabled": ssl_enabled,
            "features": features,
            "files": list(results.keys()),
            "saved_paths": saved_paths,
            "data": results,
        }

    # ------------------------------------------------------------------
    # 核心生成方法
    # ------------------------------------------------------------------

    def generate(
        self,
        domain: str,
        upstream_servers: Optional[List[Dict[str, Any]]] = None,
        ssl_enabled: bool = False,
        features: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """生成 Nginx 配置文件集合。

        Args:
            domain: 域名
            upstream_servers: 上游服务器列表
            ssl_enabled: 是否启用 SSL
            features: 额外特性 (gzip / cache / websocket / rate_limit)

        Returns:
            配置名 -> 配置内容 的字典
        """
        upstream_servers = upstream_servers or [{"host": "localhost", "port": 5000}]
        features = features or []

        results: Dict[str, str] = {}

        # 主站点配置
        results["site_config"] = self._site_config(
            domain, upstream_servers, ssl_enabled, features,
        )

        # SSL 参数（仅在启用 SSL 时生成）
        if ssl_enabled:
            results["ssl_params"] = self._ssl_params()

        # 通用配置
        results["common_params"] = self._common_params(features)

        return results

    # ------------------------------------------------------------------
    # 站点配置
    # ------------------------------------------------------------------

    def _site_config(
        self,
        domain: str,
        upstream_servers: List[Dict[str, Any]],
        ssl_enabled: bool,
        features: List[str],
    ) -> str:
        """生成站点配置（upstream + server 块）。"""
        upstream_name = domain.replace(".", "_")

        # ---- upstream 块 ----
        upstream_lines = [f"upstream {upstream_name} {{"]
        for server in upstream_servers:
            host = server.get("host", "localhost")
            port = server.get("port", 5000)
            weight = server.get("weight", 1)
            upstream_lines.append(f"    server {host}:{port} weight={weight};")
        upstream_lines.append("    keepalive 32;")
        upstream_lines.append("}")
        upstream_block = "\n".join(upstream_lines)

        # ---- HTTP -> HTTPS 重定向（仅 SSL 模式）----
        http_redirect = ""
        if ssl_enabled:
            http_redirect = f"""
server {{
    listen 80;
    listen [::]:80;
    server_name {domain};

    # ACME challenge（Let's Encrypt 验证）
    location /.well-known/acme-challenge/ {{
        root /var/www/certbot;
    }}

    location / {{
        return 301 https://$host$request_uri;
    }}
}}
"""

        # ---- 监听指令 ----
        if ssl_enabled:
            listen = "listen 443 ssl http2;"
            listen_v6 = "listen [::]:443 ssl http2;"
        else:
            listen = "listen 80;"
            listen_v6 = "listen [::]:80;"

        # ---- SSL 指令 ----
        ssl_block = ""
        if ssl_enabled:
            ssl_block = f"""
    # SSL 证书配置
    ssl_certificate /etc/letsencrypt/live/{domain}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{domain}/privkey.pem;
    include /etc/nginx/snippets/ssl-params.conf;
"""

        # ---- Gzip 压缩 ----
        gzip_block = ""
        if "gzip" in features:
            gzip_block = """
    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
"""

        # ---- 静态资源缓存 ----
        cache_block = ""
        if "cache" in features:
            cache_block = r"""
    # 静态资源缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff2?)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
"""

        # ---- WebSocket 支持 ----
        websocket_block = ""
        if "websocket" in features:
            websocket_block = f"""
    # WebSocket 支持
    location /ws {{
        proxy_pass http://{upstream_name};
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }}
"""

        # ---- 安全响应头 ----
        security_headers = """
    # 安全响应头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
"""

        # ---- 组装 server 块 ----
        server_block = f"""
server {{
    {listen}
    {listen_v6}
    server_name {domain};
{ssl_block}
    root /var/www/{domain}/public;
    index index.html;

    # 日志
    access_log /var/log/nginx/{domain}.access.log;
    error_log /var/log/nginx/{domain}.error.log;
{security_headers}
{gzip_block}
{cache_block}
    # API 反向代理
    location /api {{
        proxy_pass http://{upstream_name};
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }}
{websocket_block}
    # 前端路由（SPA history 模式）
    location / {{
        try_files $uri $uri/ /index.html;
    }}

    # 健康检查端点
    location /health {{
        access_log off;
        return 200 "OK";
    }}
}}
"""

        return f"""# Nginx 配置 - {domain}
# Generated by Leo Nginx Config Generator

{upstream_block}
{http_redirect}
{server_block}
"""

    # ------------------------------------------------------------------
    # SSL 参数
    # ------------------------------------------------------------------

    def _ssl_params(self) -> str:
        """生成 SSL/TLS 安全参数配置。"""
        return """# SSL 参数配置
# /etc/nginx/snippets/ssl-params.conf

ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers off;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;

ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;
ssl_session_tickets off;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;

# HSTS
add_header Strict-Transport-Security "max-age=63072000" always;
"""

    # ------------------------------------------------------------------
    # 通用参数
    # ------------------------------------------------------------------

    def _common_params(self, features: List[str]) -> str:
        """生成通用 Nginx 参数配置。"""
        config = """# 通用 Nginx 配置
# /etc/nginx/conf.d/common.conf

# 客户端配置
client_max_body_size 50M;
client_body_buffer_size 128k;

# 代理缓冲
proxy_buffer_size 128k;
proxy_buffers 4 256k;
proxy_busy_buffers_size 256k;

# 连接超时
keepalive_timeout 65;
send_timeout 60;

# 文件传输优化
sendfile on;
tcp_nopush on;
tcp_nodelay on;
"""

        if "rate_limit" in features:
            config += """
# 速率限制
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_conn_zone $binary_remote_addr zone=conn_limit:10m;
"""

        return config

    # ------------------------------------------------------------------
    # 文件保存
    # ------------------------------------------------------------------

    def save_files(
        self, domain: str, results: Dict[str, str]
    ) -> Dict[str, Path]:
        """将生成的配置保存到 nginx/ 目录。"""
        nginx_dir = self.output_dir / "nginx"
        nginx_dir.mkdir(parents=True, exist_ok=True)

        saved: Dict[str, Path] = {}

        # 站点配置
        site_path = nginx_dir / f"{domain}.conf"
        site_path.write_text(results["site_config"], encoding="utf-8")
        saved["site_config"] = site_path

        # SSL 参数
        if "ssl_params" in results:
            ssl_path = nginx_dir / "ssl-params.conf"
            ssl_path.write_text(results["ssl_params"], encoding="utf-8")
            saved["ssl_params"] = ssl_path

        # 通用配置
        common_path = nginx_dir / "common.conf"
        common_path.write_text(results["common_params"], encoding="utf-8")
        saved["common_params"] = common_path

        return saved


__all__ = ["NginxConfigGenerator"]
