# -*- coding: utf-8 -*-
"""
oauth_login_skill - OAuth 登录技能

完成 OAuth 登录流程并存储令牌，用于浏览器验证的认证会话。
支持 Google 和 GitHub OAuth 2.0。
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Optional
import secrets
import urllib.parse


class OAuthProvider(Enum):
    """OAuth 提供商"""
    GOOGLE = "google"
    GITHUB = "github"


class OAuthStatus(Enum):
    """OAuth 状态"""
    PENDING = "pending"
    AUTHORIZING = "authorizing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFRESHED = "refreshed"


@dataclass
class OAuthToken:
    """OAuth 令牌"""
    provider: str
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[str] = None
    scope: str = ""


@dataclass
class OAuthConfig:
    """OAuth 配置"""
    provider: OAuthProvider
    client_id: str
    client_secret: str
    redirect_uri: str = "http://localhost:3847/oauth/callback"
    scopes: str = ""
    auth_url: str = ""
    token_url: str = ""


@dataclass
class OAuthResult:
    """OAuth 结果"""
    status: OAuthStatus
    provider: str
    token: Optional[OAuthToken] = None
    error: str = ""
    message: str = ""


class OauthLoginSkill:
    """
    OAuth 登录技能

    完成 OAuth 登录流程，获取并存储访问令牌用于浏览器验证。
    支持 Google 和 GitHub OAuth 2.0。
    """

    PROVIDER_CONFIGS = {
        OAuthProvider.GOOGLE: {
            "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "default_scopes": "openid email profile",
            "refreshable": True
        },
        OAuthProvider.GITHUB: {
            "auth_url": "https://github.com/login/oauth/authorize",
            "token_url": "https://github.com/login/oauth/access_token",
            "default_scopes": "read:user user:email",
            "refreshable": False
        }
    }

    def __init__(self):
        self.name = "oauth_login_skill"
        self.version = "1.0.0"
        self.description = "OAuth 登录流程，获取和刷新访问令牌"
        self.category = "security"
        self.callback_port = 3847

    def execute(
        self,
        provider: str,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        mode: str = "login",  # login or refresh
        refresh_token: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行 OAuth 登录

        Args:
            provider: 提供商 (google/github)
            client_id: 客户端ID
            client_secret: 客户端密钥
            mode: 模式 (login/refresh)
            refresh_token: 刷新令牌（用于刷新模式）

        Returns:
            OAuth 结果
        """
        try:
            provider_enum = OAuthProvider(provider.lower())
            config = self.PROVIDER_CONFIGS[provider_enum]

            if mode == "refresh" and config["refreshable"]:
                if not refresh_token:
                    return {
                        "status": "error",
                        "error": "刷新模式需要 refresh_token",
                        "skill": self.name
                    }
                return self._refresh_token(
                    provider_enum, refresh_token, client_id, client_secret
                )

            # 检查必要参数
            if not client_id or not client_secret:
                return {
                    "status": "error",
                    "error": f"需要提供 {provider} 的 client_id 和 client_secret",
                    "skill": self.name
                }

            # 生成授权 URL
            auth_url = self._build_auth_url(
                provider_enum, client_id, config["default_scopes"]
            )

            # 创建结果（实际流程需要浏览器交互）
            result = OAuthResult(
                status=OAuthStatus.AUTHORIZING,
                provider=provider,
                message=f"请在浏览器中访问: {auth_url}"
            )

            return {
                "status": "pending",
                "result": result,
                "auth_url": auth_url,
                "instructions": [
                    f"1. 访问授权 URL: {auth_url}",
                    f"2. 完成 {provider} 授权",
                    f"3. 授权码将被发送到: http://localhost:{self.callback_port}/oauth/callback",
                    f"4. 使用授权码交换访问令牌"
                ],
                "env_vars": {
                    f"OAUTH_{provider.upper()}_CLIENT_ID": client_id,
                    f"OAUTH_{provider.upper()}_CLIENT_SECRET": client_secret
                }
            }

        except ValueError:
            return {
                "status": "error",
                "error": f"不支持的提供商: {provider}。支持: google, github",
                "skill": self.name
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "skill": self.name
            }

    def _build_auth_url(
        self,
        provider: OAuthProvider,
        client_id: str,
        scopes: str
    ) -> str:
        """构建授权 URL"""
        config = self.PROVIDER_CONFIGS[provider]
        state = secrets.token_urlsafe(16)

        params = {
            "client_id": client_id,
            "redirect_uri": f"http://localhost:{self.callback_port}/oauth/callback",
            "response_type": "code",
            "scope": scopes,
            "state": state
        }

        # Google 特有参数
        if provider == OAuthProvider.GOOGLE:
            params["access_type"] = "offline"
            params["prompt"] = "consent"

        return f"{config['auth_url']}?{urllib.parse.urlencode(params)}"

    def _refresh_token(
        self,
        provider: OAuthProvider,
        refresh_token: str,
        client_id: Optional[str],
        client_secret: Optional[str]
    ) -> Dict[str, Any]:
        """刷新令牌"""
        config = self.PROVIDER_CONFIGS[provider]

        if not config["refreshable"]:
            return {
                "status": "success",
                "message": f"{provider.value} 令牌不需要刷新",
                "refresh_supported": False
            }

        return {
            "status": "pending",
            "message": "令牌刷新需要调用提供商 API",
            "token_url": config["token_url"],
            "refresh_token": refresh_token,
            "instructions": [
                f"POST {config['token_url']}",
                "Content-Type: application/x-www-form-urlencoded",
                "",
                f"refresh_token={refresh_token}",
                f"client_id={client_id or '$CLIENT_ID'}",
                f"client_secret={client_secret or '$CLIENT_SECRET'}",
                "grant_type=refresh_token"
            ]
        }

    def generate_env_template(self, provider: str) -> str:
        """生成环境变量模板"""
        prefix = provider.upper()
        return f"""
# {provider.title()} OAuth 配置
OAUTH_{prefix}_CLIENT_ID=your_client_id_here
OAUTH_{prefix}_CLIENT_SECRET=your_client_secret_here
OAUTH_{prefix}_ACCESS_TOKEN=
OAUTH_{prefix}_REFRESH_TOKEN=
OAUTH_{prefix}_TOKEN_EXPIRY=
""".strip()

    def verify_token_validity(self, token: OAuthToken) -> Dict[str, Any]:
        """验证令牌有效性"""
        if not token.expires_at:
            return {"valid": True, "expires_soon": False}

        try:
            expiry = datetime.fromisoformat(token.expires_at)
            now = datetime.now()
            five_minutes = timedelta(minutes=5)

            if expiry < now:
                return {"valid": False, "reason": "令牌已过期"}
            elif expiry - now < five_minutes:
                return {"valid": True, "expires_soon": True, "message": "令牌即将过期，建议刷新"}
            else:
                return {"valid": True, "expires_soon": False}
        except Exception as e:
            return {"valid": False, "reason": f"无法解析过期时间: {e}"}


def main():
    """入口函数"""
    return OauthLoginSkill()


if __name__ == "__main__":
    skill = main()
