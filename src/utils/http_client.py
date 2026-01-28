"""HTTP客户端工具 - 使用httpx实现异步HTTP请求"""
import asyncio
from typing import Optional, Dict, Any
from loguru import logger
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from config import settings


class HTTPClient:
    """异步HTTP客户端封装"""

    # 常用User-Agent列表
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    ]

    def __init__(self):
        """初始化HTTP客户端"""
        self._client: Optional[httpx.AsyncClient] = None
        self._rate_limit_semaphore = asyncio.Semaphore(settings.api_rate_limit)

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()

    async def start(self):
        """启动客户端"""
        if self._client is None or self._client.is_closed:
            timeout = httpx.Timeout(30.0, connect=10.0)
            limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)

            self._client = httpx.AsyncClient(
                timeout=timeout,
                limits=limits,
                verify=True,  # SSL验证
                follow_redirects=True,  # 跟随重定向
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                }
            )
            logger.debug("HTTP客户端已启动")

    async def close(self):
        """关闭客户端"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            logger.debug("HTTP客户端已关闭")

    def _get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        import random
        return random.choice(self.USER_AGENTS)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
    )
    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        follow_redirects: bool = True
    ) -> httpx.Response:
        """
        发送GET请求

        Args:
            url: 请求URL
            headers: 请求头
            params: 查询参数
            timeout: 超时时间
            follow_redirects: 是否跟随重定向

        Returns:
            httpx.Response对象

        Raises:
            httpx.RequestError: 请求错误
            httpx.HTTPStatusError: HTTP状态错误
        """
        if self._client is None:
            await self.start()

        # 合并请求头
        request_headers = {}
        if headers:
            request_headers.update(headers)

        # 添加随机User-Agent
        if "User-Agent" not in request_headers:
            request_headers["User-Agent"] = self._get_random_user_agent()

        # 速率限制
        async with self._rate_limit_semaphore:
            logger.debug(f"GET请求: {url}")
            response = await self._client.get(
                url,
                headers=request_headers,
                params=params,
                timeout=timeout,
                follow_redirects=follow_redirects
            )

            # 记录响应状态
            logger.debug(f"响应状态: {response.status_code} - {url}")

            # 如果状态码不是2xx，抛出异常
            response.raise_for_status()

            return response

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
    )
    async def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> httpx.Response:
        """
        发送POST请求

        Args:
            url: 请求URL
            data: 表单数据
            json: JSON数据
            headers: 请求头
            timeout: 超时时间

        Returns:
            httpx.Response对象
        """
        if self._client is None:
            await self.start()

        # 合并请求头
        request_headers = {
            "Content-Type": "application/json",
        }
        if headers:
            request_headers.update(headers)

        # 添加随机User-Agent
        if "User-Agent" not in request_headers:
            request_headers["User-Agent"] = self._get_random_user_agent()

        # 速率限制
        async with self._rate_limit_semaphore:
            logger.debug(f"POST请求: {url}")
            response = await self._client.post(
                url,
                data=data,
                json=json,
                headers=request_headers,
                timeout=timeout
            )

            logger.debug(f"响应状态: {response.status_code} - {url}")
            response.raise_for_status()

            return response

    async def download_file(
        self,
        url: str,
        save_path: str,
        headers: Optional[Dict[str, str]] = None
    ) -> str:
        """
        下载文件

        Args:
            url: 文件URL
            save_path: 保存路径
            headers: 请求头

        Returns:
            保存的文件路径
        """
        if self._client is None:
            await self.start()

        request_headers = {}
        if headers:
            request_headers.update(headers)

        if "User-Agent" not in request_headers:
            request_headers["User-Agent"] = self._get_random_user_agent()

        async with self._rate_limit_semaphore:
            logger.debug(f"下载文件: {url} -> {save_path}")

            async with self._client.stream("GET", url, headers=request_headers) as response:
                response.raise_for_status()

                # 确保目录存在
                import os
                os.makedirs(os.path.dirname(save_path), exist_ok=True)

                # 写入文件
                with open(save_path, 'wb') as f:
                    async for chunk in response.aiter_bytes(8192):
                        f.write(chunk)

            logger.debug(f"文件下载完成: {save_path}")
            return save_path


# 全局HTTP客户端实例
_http_client: Optional[HTTPClient] = None


async def get_http_client() -> HTTPClient:
    """获取全局HTTP客户端实例"""
    global _http_client
    if _http_client is None:
        _http_client = HTTPClient()
        await _http_client.start()
    return _http_client


async def close_http_client():
    """关闭全局HTTP客户端"""
    global _http_client
    if _http_client is not None:
        await _http_client.close()
        _http_client = None
