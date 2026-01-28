"""图片搜索相关数据模型"""

from pydantic import BaseModel, Field
from typing import List, Optional


class SearchResult(BaseModel):
    """单个图片搜索结果"""
    title: str = Field(..., description="图片标题")
    link: str = Field(..., description="图片链接URL")
    thumbnail: Optional[str] = Field(None, description="缩略图链接")
    context_url: Optional[str] = Field(None, description="图片来源页面URL")
    width: Optional[int] = Field(None, description="图片宽度")
    height: Optional[int] = Field(None, description="图片高度")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Motorcycle Jetting Guide",
                "link": "https://example.com/image.jpg",
                "thumbnail": "https://example.com/thumb.jpg",
                "context_url": "https://example.com/page",
                "width": 800,
                "height": 600
            }
        }


class ImageSearchResponse(BaseModel):
    """图片搜索API响应"""
    items: List[SearchResult] = Field(default_factory=list, description="搜索结果列表")
    total_results: str = Field(..., description="总结果数")
    search_time: float = Field(..., description="搜索耗时（秒）")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "title": "Motorcycle Jetting Guide",
                        "link": "https://example.com/image.jpg",
                        "thumbnail": "https://example.com/thumb.jpg",
                        "context_url": "https://example.com/page",
                        "width": 800,
                        "height": 600
                    }
                ],
                "total_results": "1000",
                "search_time": 0.25
            }
        }
