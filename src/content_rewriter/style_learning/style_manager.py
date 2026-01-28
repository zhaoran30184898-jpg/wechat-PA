"""风格管理器

负责风格的加载、保存、列表和删除等操作
"""
import json
from pathlib import Path
from typing import List, Optional, Dict
from loguru import logger

from src.models.style import StyleProfile


class StyleManager:
    """风格配置管理器"""

    def __init__(self, styles_dir: str = "./styles"):
        """初始化风格管理器

        Args:
            styles_dir: 风格配置文件根目录
        """
        self.styles_dir = Path(styles_dir)
        self.predefined_dir = self.styles_dir / "predefined"
        self.user_custom_dir = self.styles_dir / "user_custom"

        # 确保目录存在
        self.predefined_dir.mkdir(parents=True, exist_ok=True)
        self.user_custom_dir.mkdir(parents=True, exist_ok=True)

    def list_styles(self) -> List[StyleProfile]:
        """列出所有可用的风格

        Returns:
            风格配置列表
        """
        styles = []

        # 加载预定义风格
        for json_file in self.predefined_dir.glob("*.json"):
            try:
                style = self._load_style_from_file(json_file)
                if style:
                    styles.append(style)
            except Exception as e:
                logger.warning(f"加载预定义风格失败 {json_file}: {e}")

        # 加载用户自定义风格
        for json_file in self.user_custom_dir.glob("*.json"):
            try:
                style = self._load_style_from_file(json_file)
                if style:
                    styles.append(style)
            except Exception as e:
                logger.warning(f"加载用户风格失败 {json_file}: {e}")

        return styles

    def load_style(self, style_name: str) -> Optional[StyleProfile]:
        """加载指定风格

        Args:
            style_name: 风格名称

        Returns:
            风格配置对象，如果不存在则返回None
        """
        # 先在预定义目录中查找
        predefined_file = self.predefined_dir / f"{style_name}.json"
        if predefined_file.exists():
            return self._load_style_from_file(predefined_file)

        # 再在用户自定义目录中查找
        user_file = self.user_custom_dir / f"{style_name}.json"
        if user_file.exists():
            return self._load_style_from_file(user_file)

        logger.error(f"未找到风格配置: {style_name}")
        return None

    def save_style(self, style: StyleProfile, is_predefined: bool = False) -> bool:
        """保存风格配置

        Args:
            style: 风格配置对象
            is_predefined: 是否为预定义风格

        Returns:
            是否保存成功
        """
        try:
            # 确定保存目录
            if is_predefined:
                save_dir = self.predefined_dir
            else:
                save_dir = self.user_custom_dir

            # 确保目录存在
            save_dir.mkdir(parents=True, exist_ok=True)

            # 保存到文件
            file_path = save_dir / f"{style.name}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(
                    style.dict(),
                    f,
                    ensure_ascii=False,
                    indent=2
                )

            logger.info(f"风格配置已保存: {file_path}")
            return True

        except Exception as e:
            logger.error(f"保存风格配置失败: {e}")
            return False

    def delete_style(self, style_name: str) -> bool:
        """删除风格配置

        Args:
            style_name: 风格名称

        Returns:
            是否删除成功
        """
        # 只允许删除用户自定义风格
        user_file = self.user_custom_dir / f"{style_name}.json"
        if user_file.exists():
            try:
                user_file.unlink()
                logger.info(f"已删除风格配置: {style_name}")
                return True
            except Exception as e:
                logger.error(f"删除风格配置失败: {e}")
                return False

        logger.error(f"无法删除预定义风格或风格不存在: {style_name}")
        return False

    def _load_style_from_file(self, file_path: Path) -> Optional[StyleProfile]:
        """从文件加载风格配置

        Args:
            file_path: 风格配置文件路径

        Returns:
            风格配置对象
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return StyleProfile(**data)

        except Exception as e:
            logger.error(f"加载风格配置文件失败 {file_path}: {e}")
            return None

    def get_style_names(self) -> Dict[str, str]:
        """获取所有风格的名称和描述

        Returns:
            风格名称到描述的映射
        """
        styles = self.list_styles()
        return {style.name: style.description for style in styles}
