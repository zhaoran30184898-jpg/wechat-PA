"""HTML解析器 - 使用BeautifulSoup4和trafilatura提取文章内容"""
from typing import Optional, Dict, List, Tuple
from urllib.parse import urljoin, urlparse
from loguru import logger
from bs4 import BeautifulSoup
import trafilatura
import trafilatura.core
import re


class ArticleParser:
    """文章内容解析器"""

    def __init__(self):
        """初始化解析器"""
        self.fallback_parser = BeautifulSoupParser()
        self.trafilatura_parser = TrafilaturaParser()

    async def parse(
        self,
        html: str,
        url: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str], List[str]]:
        """
        解析HTML，提取文章内容

        Args:
            html: HTML内容
            url: 文章URL

        Returns:
            (标题, 内容, 作者, 图片URL列表) 的元组
        """
        # 首先尝试使用trafilatura
        title, content, author, images = await self.trafilatura_parser.parse(html, url)

        # 如果trafilatura失败，使用BeautifulSoup fallback
        if not title or not content:
            logger.info("Trafilatura解析失败，使用BeautifulSoup fallback")
            title, content, author, images = await self.fallback_parser.parse(html, url)

        return title, content, author, images


class TrafilaturaParser:
    """使用Trafilatura解析文章"""

    async def parse(
        self,
        html: str,
        url: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str], List[str]]:
        """
        使用Trafilatura解析文章

        Args:
            html: HTML内容
            url: 文章URL

        Returns:
            (标题, 内容, 作者, 图片URL列表) 的元组
        """
        try:
            # 使用trafilatura提取内容
            extracted = trafilatura.core.extract_html(
                html,
                include_comments=False,
                include_tables=True,
                no_fallback=False,
                output_format='json'
            )

            if not extracted:
                return None, None, None, []

            import json
            data = json.loads(extracted)

            # 提取字段
            title = data.get('title', '').strip()
            content = data.get('text', '').strip()
            author = data.get('author', '').strip()

            # 提取图片
            images = self._extract_images(html, url)

            if title and content:
                logger.debug(f"Trafilatura解析成功: {title[:50]}...")
                return title, content, author, images

            return None, None, None, []

        except Exception as e:
            logger.warning(f"Trafilatura解析失败: {e}")
            return None, None, None, []

    def _extract_images(self, html: str, base_url: str) -> List[str]:
        """从HTML中提取图片URL"""
        soup = BeautifulSoup(html, 'lxml')
        images = []

        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src:
                # 转换为绝对URL
                absolute_url = urljoin(base_url, src)
                # 过滤掉明显不是图片的URL
                if self._is_valid_image_url(absolute_url):
                    images.append(absolute_url)

        return list(set(images))  # 去重

    def _is_valid_image_url(self, url: str) -> bool:
        """检查是否是有效的图片URL"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'}
        parsed = urlparse(url)
        path = parsed.path.lower()

        # 检查扩展名或包含image关键词
        has_image_extension = any(path.endswith(ext) for ext in image_extensions)
        has_image_keyword = 'image' in url.lower() or 'img' in url.lower()

        return has_image_extension or has_image_keyword


class BeautifulSoupParser:
    """使用BeautifulSoup4解析文章（Fallback方案）"""

    async def parse(
        self,
        html: str,
        url: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str], List[str]]:
        """
        使用BeautifulSoup解析文章

        Args:
            html: HTML内容
            url: 文章URL

        Returns:
            (标题, 内容, 作者, 图片URL列表) 的元组
        """
        try:
            soup = BeautifulSoup(html, 'lxml')

            # 提取标题
            title = self._extract_title(soup)

            # 提取作者
            author = self._extract_author(soup)

            # 提取正文内容
            content = self._extract_content(soup)

            # 提取图片
            images = self._extract_images(soup, url)

            if title and content:
                logger.debug(f"BeautifulSoup解析成功: {title[:50]}...")
                return title, content, author, images

            return None, None, None, []

        except Exception as e:
            logger.error(f"BeautifulSoup解析失败: {e}")
            return None, None, None, []

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """提取标题"""
        # 尝试多种常见的选择器
        selectors = [
            'h1.title',
            'h1.article-title',
            'h1.post-title',
            'h1.entry-title',
            'title',
            'h1',
            '[itemprop="headline"]',
            '.post-title h1',
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text().strip()
                if title:
                    return title

        return None

    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """提取作者"""
        selectors = [
            '[itemprop="author"]',
            '.author',
            '.post-author',
            '.article-author',
            'meta[name="author"]',
            '.byline',
            '.author-name',
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    author = element.get('content', '').strip()
                else:
                    author = element.get_text().strip()

                if author:
                    return author

        return None

    def _extract_content(self, soup: BeautifulSoup) -> Optional[str]:
        """提取正文内容"""
        # 移除不需要的标签
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe']):
            element.decompose()

        # 尝试多种常见的内容选择器
        content_selectors = [
            'article',
            '[itemprop="articleBody"]',
            '.post-content',
            '.article-content',
            '.entry-content',
            '.content',
            '#content',
            '.post-body',
            'main',
        ]

        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # 提取段落文本
                paragraphs = element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if paragraphs:
                    content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    if len(content) > 200:  # 至少200字符
                        return content

        # Fallback: 获取所有段落
        all_paragraphs = soup.find_all('p')
        if all_paragraphs:
            content = '\n\n'.join([p.get_text().strip() for p in all_paragraphs if p.get_text().strip()])
            if len(content) > 200:
                return content

        return None

    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """从HTML中提取图片URL"""
        images = []

        for img in soup.find_all('img'):
            # 尝试多个属性
            src = (img.get('src') or
                   img.get('data-src') or
                   img.get('data-original') or
                   img.get('data-lazy-src'))

            if src:
                # 过滤掉小图标和装饰性图片
                width = img.get('width')
                height = img.get('height')

                # 如果有尺寸信息，跳过小图
                if width and int(width) < 100:
                    continue
                if height and int(height) < 100:
                    continue

                # 转换为绝对URL
                absolute_url = urljoin(base_url, src)

                # 检查是否是有效图片
                if self._is_valid_image_url(absolute_url):
                    images.append(absolute_url)

        return list(set(images))

    def _is_valid_image_url(self, url: str) -> bool:
        """检查是否是有效的图片URL"""
        # 过滤掉明显不是图片的URL
        exclude_patterns = [
            'avatar',
            'icon',
            'logo',
            'emoji',
            'spinner',
            'loading',
            'blank',
            'pixel.gif',
            '1x1',
            'tracking',
        ]

        url_lower = url.lower()
        for pattern in exclude_patterns:
            if pattern in url_lower:
                return False

        # 检查图片扩展名
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        parsed = urlparse(url)
        path = parsed.path.lower()

        return any(path.endswith(ext) for ext in image_extensions)


async def parse_html(html: str, url: str) -> Tuple[Optional[str], Optional[str], Optional[str], List[str]]:
    """
    便捷函数：解析HTML内容

    Args:
        html: HTML内容
        url: 文章URL

    Returns:
        (标题, 内容, 作者, 图片URL列表) 的元组
    """
    parser = ArticleParser()
    return await parser.parse(html, url)
