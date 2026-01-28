"""内容改写器 - 主逻辑"""
from typing import Optional
from loguru import logger

from config import settings
from src.models.article import Article
from .base_client import BaseAIClient
from .gemini_client import GeminiClient
from .glm_client import GLMClient
from .claude_client import ClaudeClient


class ContentRewriter:
    """内容改写器 - 统一的AI改写接口"""

    def __init__(self):
        """初始化改写器"""
        self.ai_client: Optional[BaseAIClient] = None
        self.ai_provider = settings.ai_provider

    async def start(self):
        """启动改写器"""
        if self.ai_client is None:
            self.ai_client = self._create_ai_client()
            await self.ai_client.start()
            logger.info(f"内容改写器已启动 - AI提供商: {self.ai_provider}")

    async def close(self):
        """关闭改写器"""
        if self.ai_client:
            await self.ai_client.close()
            logger.info("内容改写器已关闭")

    def _create_ai_client(self) -> BaseAIClient:
        """
        根据配置创建AI客户端

        Returns:
            AI客户端实例
        """
        provider = self.ai_provider.lower()

        if provider == "gemini":
            logger.info("使用 Google Gemini AI")
            return GeminiClient(
                api_key=settings.gemini_api_key,
                model=settings.gemini_model,
                max_tokens=settings.gemini_max_tokens,
                temperature=settings.gemini_temperature
            )

        elif provider == "glm":
            logger.info("使用智谱 GLM AI")
            return GLMClient(
                api_key=settings.glm_api_key,
                model=settings.glm_model,
                max_tokens=settings.glm_max_tokens,
                temperature=settings.glm_temperature
            )

        elif provider == "claude":
            logger.info("使用 Anthropic Claude AI")
            return ClaudeClient(
                api_key=settings.anthropic_api_key,
                model=settings.anthropic_model,
                max_tokens=settings.anthropic_max_tokens,
                temperature=settings.anthropic_temperature
            )

        else:
            raise ValueError(f"不支持的AI提供商: {self.ai_provider}。支持的提供商: gemini, glm, claude")

    async def rewrite_article(
        self,
        article: Article,
        target_language: str = "zh-CN"
    ) -> Article:
        """
        改写文章

        Args:
            article: 原文章对象
            target_language: 目标语言

        Returns:
            改写后的文章对象（会修改原对象）
        """
        if self.ai_client is None:
            await self.start()

        try:
            logger.info(f"开始改写文章: {article.title}")

            # 更新状态
            article.status = "rewriting"

            # 调用AI改写
            new_title, new_content = await self.ai_client.rewrite_article(
                title=article.title,
                content=article.content,
                target_language=target_language
            )

            # 更新文章对象
            article.rewritten_title = new_title
            article.rewritten_content = new_content
            article.status = "rewritten"

            logger.info(f"文章改写成功: {new_title}")

            return article

        except Exception as e:
            logger.error(f"文章改写失败: {e}")
            article.status = "failed"
            article.error_message = str(e)
            raise

    async def translate_text(self, text: str, target_language: str = "zh-CN") -> str:
        """
        翻译文本

        Args:
            text: 原文本
            target_language: 目标语言

        Returns:
            翻译后的文本
        """
        if self.ai_client is None:
            await self.start()

        try:
            return await self.ai_client.translate_text(text, target_language)
        except Exception as e:
            logger.error(f"文本翻译失败: {e}")
            return text  # 失败时返回原文


# 全局改写器实例
_rewriter: Optional[ContentRewriter] = None


async def get_rewriter() -> ContentRewriter:
    """获取全局改写器实例"""
    global _rewriter
    if _rewriter is None:
        _rewriter = ContentRewriter()
        await _rewriter.start()
    return _rewriter


async def close_rewriter():
    """关闭全局改写器"""
    global _rewriter
    if _rewriter is not None:
        await _rewriter.close()
        _rewriter = None
