"""文章数据模型"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field, field_validator
from enum import Enum


class ArticleStatus(str, Enum):
    """文章状态枚举"""
    PENDING = "pending"          # 待处理
    FETCHING = "fetching"        # 抓取中
    FETCHED = "fetched"          # 已抓取
    REWRITING = "rewriting"      # 改写中
    REWRITTEN = "rewritten"      # 已改写
    PUBLISHING = "publishing"    # 发布中
    PUBLISHED = "published"      # 已发布
    FAILED = "failed"            # 失败


class ImageInfo(BaseModel):
    """图片信息"""
    url: HttpUrl = Field(..., description="原始图片URL")
    local_path: Optional[str] = Field(None, description="本地保存路径")
    wechat_media_id: Optional[str] = Field(None, description="微信素材库media_id")
    width: Optional[int] = Field(None, description="图片宽度")
    height: Optional[int] = Field(None, description="图片高度")
    size_bytes: Optional[int] = Field(None, description="图片大小（字节）")
    downloaded: bool = Field(default=False, description="是否已下载")

    class Config:
        str_strip_whitespace = True


class Comment(BaseModel):
    """评论信息"""
    author: str = Field(..., description="评论作者")
    content: str = Field(..., description="评论内容")
    publish_date: Optional[datetime] = Field(None, description="评论时间")
    likes: int = Field(default=0, description="点赞数")

    class Config:
        str_strip_whitespace = True


class Article(BaseModel):
    """文章模型"""
    # 基本信息
    url: HttpUrl = Field(..., description="文章URL")
    title: str = Field(..., min_length=1, description="文章标题")
    author: Optional[str] = Field(None, description="作者")
    content: str = Field(..., min_length=1, description="文章正文内容")
    summary: Optional[str] = Field(None, description="文章摘要")

    # 元数据
    publish_date: Optional[datetime] = Field(None, description="发布时间")
    fetch_date: datetime = Field(default_factory=datetime.now, description="抓取时间")
    source_domain: str = Field(..., description="来源域名")
    language: str = Field(default="en", description="文章语言")

    # 图片列表
    images: List[ImageInfo] = Field(default_factory=list, description="文章中的图片")

    # 评论列表（论坛类型网站）
    comments: List[Comment] = Field(default_factory=list, description="文章评论")

    # 状态信息
    status: ArticleStatus = Field(default=ArticleStatus.PENDING, description="处理状态")
    error_message: Optional[str] = Field(None, description="错误信息")

    # 统计信息
    word_count: int = Field(default=0, description="字数统计")
    image_count: int = Field(default=0, description="图片数量")
    comment_count: int = Field(default=0, description="评论数量")

    # 改写相关
    rewritten_title: Optional[str] = Field(None, description="改写后的标题")
    rewritten_content: Optional[str] = Field(None, description="改写后的内容")

    # 发布相关
    wechat_draft_id: Optional[str] = Field(None, description="微信草稿ID")
    wechat_article_id: Optional[str] = Field(None, description="微信文章ID")
    wechat_publish_url: Optional[str] = Field(None, description="微信发布URL")

    @field_validator('word_count')
    @classmethod
    def calculate_word_count(cls, v: int, info) -> int:
        """自动计算字数"""
        if v == 0 and 'content' in info.data:
            # 简单的英文/中文统计
            content = info.data['content']
            # 统计英文单词 + 中文字符
            import re
            english_words = len(re.findall(r'\b[a-zA-Z]+\b', content))
            chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
            return english_words + chinese_chars
        return v

    @field_validator('image_count')
    @classmethod
    def calculate_image_count(cls, v: int, info) -> int:
        """自动计算图片数量"""
        if v == 0 and 'images' in info.data:
            return len(info.data['images'])
        return v

    @field_validator('comment_count')
    @classmethod
    def calculate_comment_count(cls, v: int, info) -> int:
        """自动计算评论数量"""
        if v == 0 and 'comments' in info.data:
            return len(info.data['comments'])
        return v

    @field_validator('source_domain')
    @classmethod
    def extract_domain(cls, v: str, info) -> str:
        """从URL提取域名"""
        if 'url' in info.data:
            from urllib.parse import urlparse
            return urlparse(str(info.data['url'])).netloc
        return v

    def get_image_count(self) -> int:
        """获取图片数量"""
        return len(self.images)

    def get_downloaded_images(self) -> List[ImageInfo]:
        """获取已下载的图片"""
        return [img for img in self.images if img.downloaded]

    def add_image(self, url: str, **kwargs) -> ImageInfo:
        """添加图片"""
        image = ImageInfo(url=url, **kwargs)
        self.images.append(image)
        self.image_count = len(self.images)
        return image

    def add_comment(self, author: str, content: str, **kwargs) -> 'Comment':
        """添加评论"""
        comment = Comment(author=author, content=content, **kwargs)
        self.comments.append(comment)
        self.comment_count = len(self.comments)
        return comment

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        str_strip_whitespace = True


class ArticleFetchResult(BaseModel):
    """文章抓取结果"""
    success: bool = Field(..., description="是否成功")
    article: Optional[Article] = Field(None, description="文章对象")
    error_message: Optional[str] = Field(None, description="错误信息")
    fetch_time: float = Field(..., description="抓取耗时（秒）")

    class Config:
        str_strip_whitespace = True
