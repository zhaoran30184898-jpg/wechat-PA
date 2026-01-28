"""AI客户端抽象基类"""
from abc import ABC, abstractmethod
from typing import Optional
from loguru import logger


class BaseAIClient(ABC):
    """AI客户端抽象基类"""

    def __init__(self, api_key: str, model: str, max_tokens: int = 4096, temperature: float = 0.7):
        """
        初始化AI客户端

        Args:
            api_key: API密钥
            model: 模型名称
            max_tokens: 最大token数
            temperature: 温度参数
        """
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._client = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()

    async def start(self):
        """启动客户端"""
        if self._client is None:
            self._client = await self._create_client()
            logger.debug(f"{self.__class__.__name__} 客户端已启动")

    async def close(self):
        """关闭客户端"""
        if self._client:
            await self._close_client()
            self._client = None
            logger.debug(f"{self.__class__.__name__} 客户端已关闭")

    @abstractmethod
    async def _create_client(self):
        """创建客户端（子类实现）"""
        pass

    @abstractmethod
    async def _close_client(self):
        """关闭客户端（子类实现）"""
        pass

    @abstractmethod
    async def rewrite_article(
        self,
        title: str,
        content: str,
        target_language: str = "zh-CN"
    ) -> tuple[str, str]:
        """
        改写文章

        Args:
            title: 原标题
            content: 原内容
            target_language: 目标语言

        Returns:
            (改写后的标题, 改写后的内容) 元组
        """
        pass

    @abstractmethod
    async def translate_text(self, text: str, target_language: str = "zh-CN") -> str:
        """
        翻译文本

        Args:
            text: 原文本
            target_language: 目标语言

        Returns:
            翻译后的文本
        """
        pass

    def _validate_api_key(self) -> bool:
        """验证API密钥是否有效"""
        if not self.api_key or self.api_key.startswith("your_"):
            return False
        return True

    def _validate_inputs(self, title: str, content: str) -> tuple[bool, Optional[str]]:
        """验证输入参数"""
        if not title or not title.strip():
            return False, "标题不能为空"

        if not content or not content.strip():
            return False, "内容不能为空"

        if len(content) < 100:
            return False, f"内容过短（{len(content)} 字符），最少100字符"

        if len(content) > 50000:
            return False, f"内容过长（{len(content)} 字符），最多50000字符"

        return True, None
