"""内容验证器 - 验证文章质量和相关性"""
from typing import List, Tuple
from loguru import logger
import re

from config import settings
from src.models.article import Article


class ArticleValidator:
    """文章内容验证器"""

    # 越野摩托车相关关键词
    OFFROAD_KEYWORDS = {
        # 器材相关
        'motorcycle', 'dirt bike', 'off-road', 'atv', 'quad', 'mx', 'enduro',
        'motocross', 'supercross', 'trail', 'adventure', 'dual-sport',
        'helm', 'gear', 'protective', 'suspension', 'exhaust', 'engine',
        'tire', 'wheel', 'brake', 'frame', 'handlebar', 'footpeg',

        # 技术相关
        'maintenance', 'repair', 'upgrade', 'performance', 'modification',
        'setup', 'tuning', 'horsepower', 'torque', 'compression', 'carburetor',
        'fuel injection', 'clutch', 'transmission', 'chain', 'sprocket',

        # 品牌相关
        'kawasaki', 'yamaha', 'honda', 'suzuki', 'ktm', 'husqvarna', 'gasgas',
        'beta', 'sherco', 'tm', 'husaberg', 'aprilia', 'husqvarna',
    }

    def __init__(self):
        """初始化验证器"""
        self.min_length = settings.article_min_length
        self.max_length = settings.article_max_length

    def validate(self, article: Article) -> Tuple[bool, List[str]]:
        """
        验证文章质量

        Args:
            article: 文章对象

        Returns:
            (是否通过验证, 错误消息列表) 的元组
        """
        errors = []

        # 1. 检查必填字段
        if not article.title:
            errors.append("标题为空")

        if not article.content:
            errors.append("内容为空")

        # 2. 检查内容长度
        if article.content:
            word_count = len(article.content)
            if word_count < self.min_length:
                errors.append(f"内容过短：{word_count} 字符（最少 {self.min_length} 字符）")

            if word_count > self.max_length:
                errors.append(f"内容过长：{word_count} 字符（最多 {self.max_length} 字符）")

        # 3. 检查相关性（越野摩托车主题）
        if not self._is_relevant(article):
            errors.append("文章内容与越野摩托车主题不相关")

        # 4. 检查标题质量
        if article.title and not self._validate_title(article.title):
            errors.append("标题质量不佳（过短或包含广告关键词）")

        # 5. 检查是否包含垃圾内容
        if article.content and self._is_spam(article.content):
            errors.append("文章包含垃圾或广告内容")

        is_valid = len(errors) == 0

        if not is_valid:
            logger.warning(f"文章验证失败: {article.url}")
            for error in errors:
                logger.warning(f"  - {error}")

        return is_valid, errors

    def _is_relevant(self, article: Article) -> bool:
        """
        检查文章是否与越野摩托车相关

        Args:
            article: 文章对象

        Returns:
            是否相关
        """
        # 检查标题中的关键词
        title_keywords = 0
        if article.title:
            title_lower = article.title.lower()
            title_keywords = sum(1 for kw in self.OFFROAD_KEYWORDS if kw in title_lower)

        # 检查正文中的关键词
        content_keywords = 0
        if article.content:
            content_lower = article.content.lower()
            content_keywords = sum(1 for kw in self.OFFROAD_KEYWORDS if kw in content_lower)

        # 如果标题或正文包含足够的越野摩托车关键词，则认为相关
        # 标题权重更高
        total_score = title_keywords * 3 + content_keywords

        # 至少需要3分才认为是相关文章
        # 例如：标题1个关键词(3分) 或 正文3个关键词(3分)
        return total_score >= 3

    def _validate_title(self, title: str) -> bool:
        """
        验证标题质量

        Args:
            title: 标题

        Returns:
            是否有效
        """
        # 标题不能太短
        if len(title) < 10:
            return False

        # 标题不能太长
        if len(title) > 200:
            return False

        # 检查是否包含垃圾关键词
        spam_keywords = [
            'click here',
            'buy now',
            'free download',
            'click this',
            'subscribe',
            'advertisement',
            'sponsored',
            'promo',
        ]

        title_lower = title.lower()
        for spam_kw in spam_keywords:
            if spam_kw in title_lower:
                return False

        return True

    def _is_spam(self, content: str) -> bool:
        """
        检查内容是否是垃圾内容

        Args:
            content: 文章内容

        Returns:
            是否是垃圾内容
        """
        # 检查重复字符（例如 "aaa..." 或 "!!!!"）
        if re.search(r'(.)\1{10,}', content):
            return True

        # 检查过多的链接
        link_count = len(re.findall(r'https?://', content))
        if link_count > 10:  # 超过10个链接可能是垃圾
            return True

        # 检查垃圾关键词
        spam_patterns = [
            r'click here',
            r'buy now',
            r'free download',
            r'limited time',
            r'act now',
            r'don\'t miss',
            r'exclusive offer',
        ]

        content_lower = content.lower()
        spam_count = sum(1 for pattern in spam_patterns if re.search(pattern, content_lower))

        if spam_count >= 3:  # 包含3个以上垃圾模式
            return True

        return False

    def validate_url(self, url: str) -> Tuple[bool, str]:
        """
        验证URL格式

        Args:
            url: 文章URL

        Returns:
            (是否有效, 错误消息) 的元组
        """
        # 基本URL格式验证
        if not url.startswith(('http://', 'https://')):
            return False, "URL必须以http://或https://开头"

        # 检查是否包含域名
        from urllib.parse import urlparse
        parsed = urlparse(url)
        if not parsed.netloc:
            return False, "URL格式无效，缺少域名"

        # 检查是否被排除的域名
        excluded_domains = [
            'facebook.com',
            'twitter.com',
            'instagram.com',
            'youtube.com',
            'tiktok.com',
        ]

        if any(domain in parsed.netloc.lower() for domain in excluded_domains):
            return False, f"不支持从 {parsed.netloc} 抓取内容"

        return True, ""


# 全局验证器实例
_validator = None


def get_validator() -> ArticleValidator:
    """获取全局验证器实例"""
    global _validator
    if _validator is None:
        _validator = ArticleValidator()
    return _validator
