"""文章抓取器 - 核心抓取逻辑"""
import time
from typing import Optional
from urllib.parse import urlparse
from loguru import logger

from src.models.article import Article, ArticleFetchResult, ArticleStatus
from src.article_fetcher.parsers import ArticleParser
from src.article_fetcher.validators import ArticleValidator
from src.utils.http_client import HTTPClient


class ArticleFetcher:
    """文章抓取器 - 负责从URL抓取文章内容"""

    def __init__(self):
        """初始化抓取器"""
        self.parser = ArticleParser()
        self.validator = ArticleValidator()
        self.http_client: Optional[HTTPClient] = None

    async def start(self):
        """启动抓取器"""
        if self.http_client is None:
            self.http_client = HTTPClient()
            await self.http_client.start()
            logger.debug("文章抓取器已启动")

    async def close(self):
        """关闭抓取器"""
        if self.http_client:
            await self.http_client.close()
            logger.debug("文章抓取器已关闭")

    async def fetch(self, url: str) -> ArticleFetchResult:
        """
        抓取单篇文章

        Args:
            url: 文章URL

        Returns:
            ArticleFetchResult对象
        """
        start_time = time.time()

        try:
            # 1. 验证URL
            is_valid, error_msg = self.validator.validate_url(url)
            if not is_valid:
                return ArticleFetchResult(
                    success=False,
                    article=None,
                    error_message=f"URL验证失败: {error_msg}",
                    fetch_time=time.time() - start_time
                )

            logger.info(f"开始抓取文章: {url}")

            # 2. 下载HTML内容
            html = await self._download_html(url)
            if not html:
                return ArticleFetchResult(
                    success=False,
                    article=None,
                    error_message="无法下载HTML内容",
                    fetch_time=time.time() - start_time
                )

            # 3. 解析文章内容和评论
            title, content, author, images, comments_data = await self.parser.parse(html, url)

            if not title or not content:
                return ArticleFetchResult(
                    success=False,
                    article=None,
                    error_message="无法解析文章内容（标题或正文为空）",
                    fetch_time=time.time() - start_time
                )

            # 4. 创建文章对象
            article = Article(
                url=url,
                title=title,
                author=author,
                content=content,
                source_domain=urlparse(url).netloc,
                language='en'  # 默认英文，后续可以添加自动检测
            )

            # 添加图片
            for img_url in images:
                article.add_image(url=img_url)

            # 添加评论
            for comment_data in comments_data:
                article.add_comment(
                    author=comment_data.get('author', 'Anonymous'),
                    content=comment_data.get('content', ''),
                    publish_date=comment_data.get('publish_date'),
                    likes=comment_data.get('likes', 0)
                )

            # 5. 验证文章质量
            is_valid, errors = self.validator.validate(article)
            if not is_valid:
                article.status = ArticleStatus.FAILED
                article.error_message = "; ".join(errors)

                return ArticleFetchResult(
                    success=False,
                    article=article,
                    error_message=f"文章验证失败: {'; '.join(errors)}",
                    fetch_time=time.time() - start_time
                )

            # 6. 标记为已抓取
            article.status = ArticleStatus.FETCHED

            fetch_time = time.time() - start_time
            logger.info(
                f"文章抓取成功: {title[:50]}... "
                f"({article.word_count} 字, {len(images)} 图, {article.comment_count} 评论, {fetch_time:.2f}秒)"
            )

            return ArticleFetchResult(
                success=True,
                article=article,
                error_message=None,
                fetch_time=fetch_time
            )

        except Exception as e:
            logger.exception(f"抓取文章时发生异常: {url}")
            return ArticleFetchResult(
                success=False,
                article=None,
                error_message=f"抓取异常: {str(e)}",
                fetch_time=time.time() - start_time
            )

    async def _download_html(self, url: str) -> Optional[str]:
        """
        下载HTML内容

        Args:
            url: 文章URL

        Returns:
            HTML内容字符串，失败返回None
        """
        try:
            if self.http_client is None:
                await self.start()

            response = await self.http_client.get(url, timeout=30.0)
            html = response.text

            # 检查内容长度
            if len(html) < 100:
                logger.warning(f"HTML内容过短: {len(html)} 字符")
                return None

            logger.debug(f"成功下载HTML: {len(html)} 字符")
            return html

        except Exception as e:
            logger.error(f"下载HTML失败: {e}")
            return None

    async def fetch_batch(self, urls: list[str]) -> list[ArticleFetchResult]:
        """
        批量抓取文章

        Args:
            urls: 文章URL列表

        Returns:
            ArticleFetchResult列表
        """
        logger.info(f"开始批量抓取 {len(urls)} 篇文章")

        results = []
        for i, url in enumerate(urls, 1):
            logger.info(f"正在抓取 [{i}/{len(urls)}]: {url}")
            result = await self.fetch(url)
            results.append(result)

            # 短暂延迟，避免请求过快
            if i < len(urls):
                await self._delay(1)

        success_count = sum(1 for r in results if r.success)
        logger.info(f"批量抓取完成: 成功 {success_count}/{len(urls)}")

        return results

    async def _delay(self, seconds: float):
        """延迟执行"""
        import asyncio
        await asyncio.sleep(seconds)


# 全局抓取器实例
_fetcher: Optional[ArticleFetcher] = None


async def get_fetcher() -> ArticleFetcher:
    """获取全局抓取器实例"""
    global _fetcher
    if _fetcher is None:
        _fetcher = ArticleFetcher()
        await _fetcher.start()
    return _fetcher


async def close_fetcher():
    """关闭全局抓取器"""
    global _fetcher
    if _fetcher is not None:
        await _fetcher.close()
        _fetcher = None
