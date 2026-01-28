# HTTP Client Module
# HTTP 客户端模块

import time
import random
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .logger import get_logger

logger = get_logger(__name__)


class HTTPClient:
    """HTTP 客户端，支持重试和速率限制"""

    def __init__(self,
                 timeout: int = 30,
                 max_retries: int = 3,
                 retry_delay: int = 5,
                 user_agent: str = None,
                 rate_limit_delay: float = 2.0):
        """
        初始化 HTTP 客户端

        Args:
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
            user_agent: User-Agent 字符串
            rate_limit_delay: 请求间延迟（秒）
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0

        # 配置重试策略
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )

        # 创建会话
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # 设置默认请求头
        self.headers = {
            'User-Agent': user_agent or (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

    def _rate_limit(self):
        """实施速率限制"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_request
            # 添加随机性以避免检测
            sleep_time += random.uniform(0, 0.5)
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def get(self,
            url: str,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            **kwargs) -> Optional[requests.Response]:
        """
        发送 GET 请求

        Args:
            url: 请求 URL
            params: 查询参数
            headers: 额外的请求头
            **kwargs: 其他请求参数

        Returns:
            响应对象，失败时返回 None
        """
        self._rate_limit()

        # 合并请求头
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        try:
            response = self.session.get(
                url,
                params=params,
                headers=request_headers,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response

        except requests.exceptions.Timeout:
            logger.error(f"请求超时: {url}")
        except requests.exceptions.TooManyRedirects:
            logger.error(f"重定向过多: {url}")
        except requests.exceptions.SSLError:
            logger.error(f"SSL 错误: {url}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP 错误: {url} - {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {url} - {e}")

        return None

    def post(self,
             url: str,
             data: Optional[Dict[str, Any]] = None,
             json: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, str]] = None,
             **kwargs) -> Optional[requests.Response]:
        """
        发送 POST 请求

        Args:
            url: 请求 URL
            data: 表单数据
            json: JSON 数据
            headers: 额外的请求头
            **kwargs: 其他请求参数

        Returns:
            响应对象，失败时返回 None
        """
        self._rate_limit()

        # 合并请求头
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        try:
            response = self.session.post(
                url,
                data=data,
                json=json,
                headers=request_headers,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            logger.error(f"POST 请求失败: {url} - {e}")
            return None

    def close(self):
        """关闭会话"""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
