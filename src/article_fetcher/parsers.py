"""HTML解析器 - 使用BeautifulSoup4和trafilatura提取文章内容"""
from typing import Optional, Dict, List, Tuple
from urllib.parse import urljoin, urlparse
from loguru import logger
from bs4 import BeautifulSoup
import trafilatura
import re
from datetime import datetime


class ArticleParser:
    """文章内容解析器"""

    def __init__(self):
        """初始化解析器"""
        self.fallback_parser = BeautifulSoupParser()
        self.trafilatura_parser = TrafilaturaParser()
        self.comment_parser = ForumCommentParser()

    async def parse(
        self,
        html: str,
        url: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str], List[str], List[Dict]]:
        """
        解析HTML，提取文章内容和评论

        Args:
            html: HTML内容
            url: 文章URL

        Returns:
            (标题, 内容, 作者, 图片URL列表, 评论列表) 的元组
        """
        # 首先尝试使用trafilatura
        title, content, author, images = await self.trafilatura_parser.parse(html, url)

        # 如果trafilatura失败，使用BeautifulSoup fallback
        if not title or not content:
            logger.info("Trafilatura解析失败，使用BeautifulSoup fallback")
            title, content, author, images = await self.fallback_parser.parse(html, url)

        # 提取评论（论坛类型网站）
        comments = await self.comment_parser.parse_comments(html, url)

        return title, content, author, images, comments


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
            extracted = trafilatura.extract(
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
            'div.post-body',  # Blogger specific
            'main',
        ]

        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # 首先尝试提取段落文本
                paragraphs = element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if paragraphs:
                    content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    if len(content) > 200:  # 至少200字符
                        return content

                # Fallback: 如果没有找到段落，直接提取所有文本
                # 这对某些使用 <br> 分隔的博客（如Blogger）很有用
                content = element.get_text(separator='\n', strip=True)
                if len(content) > 200:
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


async def parse_html(html: str, url: str) -> Tuple[Optional[str], Optional[str], Optional[str], List[str], List[Dict]]:
    """
    便捷函数：解析HTML内容

    Args:
        html: HTML内容
        url: 文章URL

    Returns:
        (标题, 内容, 作者, 图片URL列表, 评论列表) 的元组
    """
    parser = ArticleParser()
    return await parser.parse(html, url)


class ForumCommentParser:
    """论坛评论解析器"""

    async def parse_comments(self, html: str, url: str) -> List[Dict]:
        """
        解析HTML中的论坛评论

        Args:
            html: HTML内容
            url: 页面URL

        Returns:
            评论列表，每个评论包含author, content, publish_date, likes
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            comments = []

            # ThumperTalk论坛特定的评论选择器
            # 根据不同的论坛网站结构，这里需要适配
            if 'thumpertalk.com' in url:
                comments = self._parse_thumpertalk_comments(soup)
            elif 'reddit.com' in url:
                comments = self._parse_reddit_comments(soup)
            else:
                # 通用论坛评论解析
                comments = self._parse_generic_forum_comments(soup)

            if comments:
                logger.info(f"成功提取 {len(comments)} 条评论")

            return comments

        except Exception as e:
            logger.warning(f"评论解析失败: {e}")
            return []

    def _parse_thumpertalk_comments(self, soup: BeautifulSoup) -> List[Dict]:
        """解析ThumperTalk论坛的评论"""
        comments = []

        try:
            # ThumperTalk使用article标签，class包含ipsComment
            comment_elements = soup.find_all('article', class_='ipsComment')

            logger.debug(f"找到 {len(comment_elements)} 个评论元素")

            for element in comment_elements:
                try:
                    # 提取作者 - 尝试多个选择器
                    author = "Anonymous"
                    author_elem = (element.find('a', class_='ipsType_break') or
                                  element.select_one('.ipsComment_author .ipsType_break') or
                                  element.select_one('[data-ipsHover-data-target]'))
                    if author_elem:
                        author = author_elem.get_text().strip()

                    # 提取内容
                    content_elem = element.find('div', class_='ipsComment_content') or element.select_one('[data-commentid]')
                    if content_elem:
                        # 创建副本以避免修改原始soup
                        content_copy = content_elem

                        # 移除引用内容
                        for blockquote in content_copy.find_all('blockquote'):
                            blockquote.decompose()

                        # 移除签名
                        signature = content_copy.find('div', class_='ipsSignature')
                        if signature:
                            signature.decompose()

                        # 移除引用块
                        for quote in content_copy.find_all('div', class_='ipsQuote'):
                            quote.decompose()

                        content = content_copy.get_text(separator='\n', strip=True)
                    else:
                        continue

                    # 提取点赞数
                    likes = 0
                    likes_elem = element.find('span', class_='ipsRepNumber')
                    if likes_elem:
                        try:
                            likes_text = likes_elem.get_text().strip()
                            likes = int(likes_text)
                        except:
                            pass

                    # 提取时间
                    time_elem = element.find('time')
                    publish_date = None
                    if time_elem and time_elem.get('datetime'):
                        try:
                            publish_date = datetime.fromisoformat(time_elem['datetime'].replace('Z', '+00:00'))
                        except:
                            pass

                    # 过滤掉太短的和原作者的评论（通常是文章内容）
                    if content and len(content) > 100:  # 提高最小长度要求
                        comments.append({
                            'author': author,
                            'content': content,
                            'publish_date': publish_date,
                            'likes': likes
                        })

                except Exception as e:
                    logger.debug(f"解析单条评论失败: {e}")
                    continue

            logger.info(f"成功解析 {len(comments)} 条ThumperTalk评论")

        except Exception as e:
            logger.warning(f"ThumperTalk评论解析失败: {e}")

        return comments

    def _parse_reddit_comments(self, soup: BeautifulSoup) -> List[Dict]:
        """解析Reddit评论"""
        # Reddit评论解析逻辑（如果需要支持Reddit）
        return []

    def _parse_generic_forum_comments(self, soup: BeautifulSoup) -> List[Dict]:
        """通用论坛评论解析"""
        comments = []

        try:
            # 尝试常见的论坛评论结构
            comment_selectors = [
                '.comment',
                '.post',
                '.reply',
                '[itemprop="comment"]',
                '.forum-post',
                '.discussion-post',
            ]

            for selector in comment_selectors:
                comment_elements = soup.select(selector)

                if len(comment_elements) > 3:  # 至少找到3个以上才认为有效
                    for element in comment_elements:
                        author = self._extract_comment_author(element)
                        content = self._extract_comment_content(element)
                        likes = self._extract_comment_likes(element)

                        if content and len(content) > 20:
                            comments.append({
                                'author': author,
                                'content': content,
                                'publish_date': None,
                                'likes': likes
                            })

                    if comments:
                        break

        except Exception as e:
            logger.warning(f"通用论坛评论解析失败: {e}")

        return comments

    def _extract_comment_author(self, element) -> str:
        """提取评论作者"""
        selectors = [
            '.author',
            '.username',
            '.user-name',
            '[itemprop="author"]',
            '.comment-author',
        ]

        for selector in selectors:
            elem = element.select_one(selector)
            if elem:
                return elem.get_text().strip()

        return "Anonymous"

    def _extract_comment_content(self, element) -> Optional[str]:
        """提取评论内容"""
        # 移除子元素（如回复、引用等）
        for unwanted in element.find_all(['blockquote', 'code', 'pre']):
            unwanted.decompose()

        selectors = [
            '.content',
            '.comment-body',
            '.message',
            '.text',
            '[itemprop="text"]',
            'p',
        ]

        for selector in selectors:
            elem = element.select_one(selector)
            if elem:
                content = elem.get_text(separator='\n', strip=True)
                if len(content) > 20:
                    return content

        return None

    def _extract_comment_likes(self, element) -> int:
        """提取点赞数"""
        selectors = [
            '.likes',
            '.upvotes',
            '.vote-count',
            '[data-likes]',
        ]

        for selector in selectors:
            elem = element.select_one(selector)
            if elem:
                try:
                    return int(elem.get_text().strip())
                except:
                    pass

        return 0
