"""智谱GLM AI客户端"""
from typing import Optional
from loguru import logger
from zhipuai import ZhipuAI

from .base_client import BaseAIClient
from .prompts import get_rewrite_prompt
from src.models.style import StyleProfile


class GLMClient(BaseAIClient):
    """智谱GLM AI客户端"""

    async def _create_client(self):
        """创建GLM客户端"""
        if not self._validate_api_key():
            raise ValueError("GLM API Key 无效，请检查配置")

        client = ZhipuAI(api_key=self.api_key)
        return client

    async def _close_client(self):
        """关闭客户端"""
        # GLM客户端不需要显式关闭
        pass

    async def rewrite_article(
        self,
        title: str,
        content: str,
        target_language: str = "zh-CN",
        comments: list = None,
        style: Optional[StyleProfile] = None
    ) -> tuple[str, str]:
        """
        使用GLM改写文章

        Args:
            title: 原标题
            content: 原内容
            target_language: 目标语言
            comments: 评论列表（可选）
            style: 风格配置（可选）

        Returns:
            (改写后的标题, 改写后的内容) 元组
        """
        # 验证输入
        is_valid, error_msg = self._validate_inputs(title, content)
        if not is_valid:
            raise ValueError(error_msg)

        if self._client is None:
            await self.start()

        try:
            # 获取改写提示词（包含评论和风格配置）
            prompt = get_rewrite_prompt(title, content, target_language, comments, style)

            style_name = style.name if style else "默认"
            logger.info(f"正在使用 GLM 改写文章 (风格: {style_name}): {title[:50]}...")

            # 调用GLM API
            response = await self._generate_content_async(prompt)

            if not response or not response.choices:
                raise Exception("GLM返回空响应")

            result = response.choices[0].message.content.strip()

            # 解析结果
            return self._parse_result(result)

        except Exception as e:
            logger.error(f"GLM改写失败: {e}")
            raise

    async def _generate_content_async(self, prompt: str):
        """异步生成内容"""
        import asyncio

        loop = asyncio.get_event_loop()
        # GLM的chat.completions.create是同步的，使用run_in_executor转为异步
        response = await loop.run_in_executor(
            None,
            lambda: self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
        )
        return response

    def _parse_result(self, result: str) -> tuple[str, str]:
        """
        解析AI返回的结果

        支持多种格式：
        1. 标题：xxx / 内容：xxx
        2. ## 标题改写 / ## 内容改写
        """
        lines = result.split('\n')

        new_title = ""
        new_content = []

        current_section = None

        for line in lines:
            line = line.strip()

            # 检测标题分隔符
            if line in ['## 标题改写', '## 标题', '标题改写', '标题']:
                current_section = 'title'
                continue

            # 检测内容分隔符
            if line in ['## 内容改写', '## 内容', '内容改写', '内容']:
                current_section = 'content'
                continue

            # 检测旧的标题行格式
            if line.startswith(('标题:', '标题：', 'Title:', 'TITLE:')):
                current_section = 'title'
                # 提取标题
                for marker in ['标题:', '标题：', 'Title:', 'TITLE:']:
                    if marker in line:
                        new_title = line.split(marker, 1)[1].strip()
                        break
                continue

            # 检测旧的内容行格式
            if line.startswith(('内容:', '内容：', 'Content:', 'CONTENT:')):
                current_section = 'content'
                # 提取内容开始部分
                for marker in ['内容:', '内容：', 'Content:', 'CONTENT:']:
                    if marker in line and len(line.split(marker, 1)[1].strip()) > 0:
                        content_part = line.split(marker, 1)[1].strip()
                        if content_part:
                            new_content.append(content_part)
                        break
                continue

            # 处理标题部分
            if current_section == 'title' and line and not new_title:
                # 第一行非空内容就是标题
                new_title = line
                # 标题可能包含markdown格式，清理一下
                new_title = new_title.replace('**', '').replace('*', '').strip()
                continue

            # 添加内容
            if current_section == 'content' and line:
                new_content.append(line)

        # 如果没有明确分隔，尝试其他解析方式
        if not new_title or not new_content:
            return self._parse_result_fallback(result)

        # 如果标题为空，使用原标题
        if not new_title:
            new_title = "【待补充标题】"

        new_content_text = '\n\n'.join(new_content).strip()

        return new_title, new_content_text

    def _parse_result_fallback(self, result: str) -> tuple[str, str]:
        """
        备用解析方法：如果AI返回格式不标准

        假设：第一段是标题，后面是内容
        """
        lines = result.split('\n')

        # 第一行作为标题
        new_title = lines[0].strip() if lines else "【待补充标题】"

        # 其余作为内容
        new_content = '\n\n'.join(lines[1:]).strip() if len(lines) > 1 else result

        return new_title, new_content

    async def translate_text(self, text: str, target_language: str = "zh-CN") -> str:
        """
        翻译文本

        Args:
            text: 原文本
            target_language: 目标语言

        Returns:
            翻译后的文本
        """
        if self._client is None:
            await self.start()

        try:
            # 构建翻译提示词
            if target_language == "zh-CN":
                prompt = f"请将以下文本翻译成中文，保持专业术语的准确性：\n\n{text}"
            else:
                prompt = f"请将以下文本翻译成{target_language}：\n\n{text}"

            logger.debug(f"正在使用 GLM 翻译文本 ({len(text)} 字符)")

            # 调用GLM API
            response = await self._generate_content_async(prompt)

            if not response or not response.choices:
                return text

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"GLM翻译失败: {e}")
            return text  # 失败时返回原文
