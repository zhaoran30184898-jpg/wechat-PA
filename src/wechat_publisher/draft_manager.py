"""微信公众号草稿管理器"""
from typing import Optional
from loguru import logger
from src.models.article import Article
from .client import WeChatClient


class DraftManager:
    """草稿管理器"""

    def __init__(self):
        """初始化草稿管理器"""
        self.client = WeChatClient()

    def _truncate_title(self, title: str, max_bytes: int = 40) -> str:
        """
        截断标题以符合微信字节数限制

        Args:
            title: 原始标题
            max_bytes: 最大字节数（微信限制为64字节）

        Returns:
            截断后的标题
        """
        if not title:
            return title

        # 移除emoji和特殊字符，因为可能导致计算偏差
        import re
        # 保留中英文、数字、常见标点
        title = re.sub(r'[^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a\u3002\uff0c\u3001\uff1f\uff01\u002c\u002e\u003f\u0021\u0020\u0028\u0029\u3010\u3011\u300a\u300b\uff08\uff09\u201c\u201d\u2018\u2019]', '', title)

        # 编码为UTF-8并检查长度
        title_bytes = title.encode('utf-8')

        if len(title_bytes) <= max_bytes:
            return title

        # 如果超过限制，需要截断
        # 逐个字符添加，直到达到限制
        truncated = ''
        truncated_bytes = 0

        for char in title:
            char_bytes = len(char.encode('utf-8'))
            if truncated_bytes + char_bytes > max_bytes:
                # 添加省略号（3字节）
                if truncated_bytes + 3 <= max_bytes:
                    truncated += '...'
                break
            truncated += char
            truncated_bytes += char_bytes

        logger.warning(f"标题过长（{len(title_bytes)}字节），已截断为: {truncated}")
        return truncated

    def _truncate_text(self, text: str, max_bytes: int) -> str:
        """
        通用文本截断函数

        Args:
            text: 原始文本
            max_bytes: 最大字节数

        Returns:
            截断后的文本
        """
        if not text:
            return text

        # 编码为UTF-8并检查长度
        text_bytes = text.encode('utf-8')

        if len(text_bytes) <= max_bytes:
            return text

        # 如果超过限制，需要截断
        truncated = ''
        truncated_bytes = 0

        for char in text:
            char_bytes = len(char.encode('utf-8'))
            if truncated_bytes + char_bytes > max_bytes:
                # 添加省略号（3字节）
                if truncated_bytes + 3 <= max_bytes:
                    truncated += '...'
                break
            truncated += char
            truncated_bytes += char_bytes

        return truncated

    def publish_to_draft(self, article: Article) -> str:
        """
        将文章发布为草稿

        Args:
            article: 文章对象

        Returns:
            草稿的media_id
        """
        # 使用改写后的内容（如果有），否则使用原文
        title = article.rewritten_title or article.title
        content = article.rewritten_content or article.content

        # 截断标题以符合微信限制
        # 注意：由于微信对中文计数有特殊处理，限制为约10个中文字符
        title = self._truncate_title(title, max_bytes=35)  # 限制约11-12个中文字符
        logger.info(f"最终标题字节长度: {len(title.encode('utf-8'))} / 64")

        # 转换换行符为HTML
        html_content = self._convert_to_html(content)

        # 提取摘要（前200字）
        digest = self._extract_digest(content)

        # 截断摘要以符合微信限制（使用54字节以留出余量）
        digest = self._truncate_text(digest, max_bytes=54)

        # 上传封面图（如果有图片的话）
        thumb_media_id = None
        if article.images and len(article.images) > 0:
            thumb_media_id = self._upload_cover_image(str(article.images[0].url))

        try:
            logger.info(f"开始发布草稿: {title}")

            # 创建草稿
            result = self.client.create_draft(
                title=title,
                content=html_content,
                author=article.author or "",
                digest=digest,
                thumb_media_id=thumb_media_id,
                need_open_comment=1,  # 打开评论
                only_fans_can_comment=0  # 所有人可以评论
            )

            media_id = result.get("media_id", "")
            logger.success(f"草稿发布成功! media_id: {media_id}")

            return media_id

        except Exception as e:
            logger.error(f"发布草稿失败: {e}")
            raise

    def _upload_cover_image(self, image_url: str) -> str:
        """
        上传封面图到微信公众号素材库

        Args:
            image_url: 图片URL

        Returns:
            素材的media_id
        """
        import httpx
        import tempfile
        import os

        try:
            logger.info(f"下载封面图: {image_url}")

            # 下载图片
            response = httpx.get(image_url, timeout=30.0)
            if response.status_code != 200:
                logger.error(f"下载图片失败: HTTP {response.status_code}")
                return None

            # 保存到临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                tmp_file.write(response.content)
                tmp_file_path = tmp_file.name

            try:
                # 上传到微信公众号素材库
                logger.info(f"上传图片到微信素材库...")
                result = self.client.upload_permanent_media("image", tmp_file_path)
                media_id = result.get("media_id", "")
                logger.success(f"图片上传成功! media_id: {media_id}")
                return media_id

            finally:
                # 删除临时文件
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)

        except Exception as e:
            logger.error(f"上传封面图失败: {e}")
            return None

    def _convert_to_html(self, content: str) -> str:
        """
        将纯文本内容转换为HTML格式

        Args:
            content: 纯文本内容

        Returns:
            HTML格式的内容
        """
        if not content:
            return ""

        # 替换换行符为段落标签
        paragraphs = content.split('\n\n')

        html_parts = []
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # 处理标题（以**开头的内容）
            if para.startswith('**') and para.endswith('**'):
                heading = para.strip('*').strip()
                html_parts.append(f'<h3>{heading}</h3>')
            # 处理普通段落
            else:
                # 保留段落内的换行
                para_html = para.replace('\n', '<br>')
                html_parts.append(f'<p>{para_html}</p>')

        html_content = ''.join(html_parts)
        return html_content

    def _extract_digest(self, content: str, max_length: int = 200) -> str:
        """
        提取摘要

        Args:
            content: 内容
            max_length: 最大长度

        Returns:
            摘要文本
        """
        if not content:
            return ""

        # 移除多余的空白和换行
        cleaned = ' '.join(content.split())

        # 截取指定长度
        if len(cleaned) > max_length:
            digest = cleaned[:max_length].rstrip()
            # 确保在完整单词处截断（中文不需要，但英文需要）
            if ' ' in digest:
                digest = digest.rsplit(' ', 1)[0]
            return digest + "..."
        else:
            return cleaned

    def close(self):
        """关闭管理器"""
        if self.client:
            self.client.close()
