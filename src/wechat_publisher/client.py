"""微信公众号API客户端"""
import httpx
from typing import Optional, Dict, Any
from loguru import logger
from config import settings


class WeChatClient:
    """微信公众号API客户端"""

    def __init__(self):
        """初始化客户端"""
        self.app_id = settings.wechat_app_id
        self.app_secret = settings.wechat_app_secret
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[float] = None

        # API 基础地址
        self.api_base = "https://api.weixin.qq.com/cgi-bin"

        # HTTP客户端
        self.http_client = httpx.Client(timeout=30.0)

    def get_access_token(self) -> str:
        """
        获取access_token

        Returns:
            access_token字符串
        """
        # 检查token是否还有效
        if self.access_token and self.token_expires_at:
            import time
            if time.time() < self.token_expires_at - 300:  # 提前5分钟刷新
                logger.debug("使用缓存的access_token")
                return self.access_token

        # 获取新的token
        url = f"{self.api_base}/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }

        try:
            logger.info("获取微信access_token...")
            response = self.http_client.get(url, params=params)
            data = response.json()

            if "access_token" in data:
                self.access_token = data["access_token"]
                expires_in = data.get("expires_in", 7200)

                import time
                self.token_expires_at = time.time() + expires_in

                logger.success(f"成功获取access_token, 有效期: {expires_in}秒")
                return self.access_token
            else:
                error_msg = data.get("errmsg", "未知错误")
                error_code = data.get("errcode", "N/A")
                raise Exception(f"获取access_token失败: {error_code} - {error_msg}")

        except Exception as e:
            logger.error(f"获取access_token异常: {e}")
            raise

    def create_draft(
        self,
        title: str,
        content: str,
        author: str = "",
        digest: str = "",
        need_open_comment: int = 0,
        only_fans_can_comment: int = 0,
        thumb_media_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建草稿

        Args:
            title: 文章标题
            content: 文章内容（HTML格式）
            author: 作者
            digest: 摘要
            need_open_comment: 是否打开评论 (0=不打开, 1=打开)
            only_fans_can_comment: 是否只有粉丝可以评论 (0=所有人, 1=粉丝)
            thumb_media_id: 封面图片素材id (可选)

        Returns:
            API响应数据
        """
        token = self.get_access_token()
        url = f"{self.api_base}/draft/add?access_token={token}"

        # 构建文章数据
        article_data = {
            "title": title,
            "author": author,
            "digest": digest,
            "content": content,
            "content_source_url": "",
            "need_open_comment": need_open_comment,
            "only_fans_can_comment": only_fans_can_comment,
        }

        # 只有在有封面图时才添加该字段
        if thumb_media_id:
            article_data["thumb_media_id"] = thumb_media_id
        else:
            # 如果没有封面图，使用占位符
            article_data["thumb_media_id"] = "0"

        articles = [article_data]

        payload = {
            "articles": articles
        }

        try:
            logger.info(f"创建草稿: {title}")
            title_bytes = len(title.encode('utf-8'))
            logger.info(f"标题字节长度: {title_bytes} / 64")

            digest_bytes = len(digest.encode('utf-8')) if digest else 0
            logger.info(f"摘要字节长度: {digest_bytes} / 120")

            if title_bytes > 64:
                logger.error(f"标题超过64字节限制! 当前: {title_bytes}字节")
                raise Exception(f"标题过长: {title_bytes}字节，超过64字节限制")

            if digest_bytes > 120:
                logger.error(f"摘要超过120字节限制! 当前: {digest_bytes}字节")
                raise Exception(f"摘要过长: {digest_bytes}字节，超过120字节限制")

            # 手动序列化 JSON，确保中文不被转义
            import json
            json_data = json.dumps(payload, ensure_ascii=False)

            response = self.http_client.post(
                url,
                content=json_data.encode('utf-8'),
                headers={'Content-Type': 'application/json; charset=utf-8'}
            )
            data = response.json()

            logger.debug(f"API响应: {data}")

            # 检查响应状态
            # WeChat API在成功时可能不返回errcode，或者返回errcode=0
            error_code = data.get("errcode")

            if error_code is None or error_code == 0:
                # 成功：检查是否有media_id
                media_id = data.get("media_id", "")
                if media_id:
                    logger.success(f"草稿创建成功! media_id: {media_id}")
                    return data
                else:
                    logger.error(f"创建失败: 响应中没有media_id")
                    logger.error(f"完整响应: {data}")
                    raise Exception("创建草稿失败: 响应中没有media_id")
            else:
                error_msg = data.get("errmsg", "未知错误")
                logger.error(f"创建草稿失败: {error_code} - {error_msg}")
                logger.error(f"完整响应: {data}")
                raise Exception(f"创建草稿失败: {error_code} - {error_msg}")

        except Exception as e:
            logger.error(f"创建草稿异常: {e}")
            raise

    def upload_permanent_media(self, media_type: str, file_path: str) -> Dict[str, Any]:
        """
        上传永久素材（图片）

        Args:
            media_type: 媒体类型 (image)
            file_path: 文件路径

        Returns:
            API响应数据，包含media_id和URL
        """
        token = self.get_access_token()
        url = f"{self.api_base}/material/add_material?access_token={token}&type={media_type}"

        try:
            logger.info(f"上传永久素材: {file_path}")

            # 检查文件是否存在
            import os
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                raise Exception(f"文件不存在: {file_path}")

            # 获取文件大小
            file_size = os.path.getsize(file_path)
            logger.info(f"文件大小: {file_size} bytes ({file_size / 1024:.2f} KB)")

            # 微信要求图片文件不超过2MB
            if file_size > 2 * 1024 * 1024:
                logger.error(f"文件过大: {file_size / 1024 / 1024:.2f} MB，超过微信2MB限制")
                raise Exception(f"图片文件过大，超过2MB限制")

            with open(file_path, "rb") as f:
                files = {
                    "media": f
                }
                logger.info(f"开始上传到: {url}")
                logger.debug(f"请求参数 - type: {media_type}")

                response = self.http_client.post(url, files=files)

                logger.debug(f"响应状态码: {response.status_code}")
                logger.debug(f"响应内容: {response.text}")

                data = response.json()

            logger.debug(f"解析后的JSON: {data}")

            # 检查响应状态
            # WeChat API在成功时可能不返回errcode，或者返回errcode=0
            error_code = data.get("errcode")

            if error_code is None or error_code == 0:
                # 成功：检查是否有media_id
                media_id = data.get("media_id", "")
                url_str = data.get("url", "")
                if media_id:
                    logger.success(f"素材上传成功! media_id: {media_id}, url: {url_str}")
                    return data
                else:
                    logger.error(f"上传失败: 响应中没有media_id")
                    logger.error(f"完整响应: {data}")
                    raise Exception("上传素材失败: 响应中没有media_id")
            else:
                error_msg = data.get("errmsg", "未知错误")
                logger.error(f"上传素材失败: {error_code} - {error_msg}")
                logger.error(f"完整响应: {data}")
                raise Exception(f"上传素材失败: {error_code} - {error_msg}")

        except Exception as e:
            logger.error(f"上传素材异常: {e}")
            raise

    def close(self):
        """关闭客户端"""
        if self.http_client:
            self.http_client.close()
