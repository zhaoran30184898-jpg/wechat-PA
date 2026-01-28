"""风格配置数据模型"""
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class StyleProfile(BaseModel):
    """风格配置文件

    用于定义文章改写的风格、角色、格式规则等
    """
    name: str = Field(..., description="风格名称（唯一标识）")
    description: str = Field(..., description="风格描述")
    role_definition: str = Field(..., description="AI角色定义")
    rewrite_instructions: Dict = Field(default_factory=dict, description="改写指令")
    comment_style: str = Field(default="", description="评论处理方式")
    formatting_rules: List[str] = Field(default_factory=list, description="格式规则")
    examples: List[str] = Field(default_factory=list, description="示例文本")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    is_predefined: bool = Field(default=False, description="是否为预定义风格")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "name": "moto_mechanic",
                "description": "摩托车老司机风格 - 专业且接地气",
                "role_definition": "你是一位专业的越野摩托车爱好者...",
                "rewrite_instructions": {
                    "tone": "轻松幽默但不夸张",
                    "structure": "保持原文结构"
                },
                "comment_style": "对话式引入，保留原用户名",
                "formatting_rules": [
                    "不用emoji",
                    "不用编号列表"
                ],
                "examples": [
                    "说到化油器调校，很多车友都觉得这玩意儿挺玄乎。"
                ]
            }
    }

    def get_full_prompt(self, title: str, content: str, comments: Optional[List[Dict]] = None) -> str:
        """根据风格配置生成完整的改写提示词

        Args:
            title: 文章标题
            content: 文章内容
            comments: 评论列表（可选）

        Returns:
            完整的提示词字符串
        """
        # 构建评论文本
        comments_section = ""
        if comments and len(comments) > 0:
            # 筛选高质量评论
            valuable_comments = [c for c in comments if len(c.get('content', '')) > 50][:10]

            if valuable_comments:
                comments_section = "\n\n# 论坛评论（请用对话方式自然融入正文）\n\n"
                for comment in valuable_comments:
                    author = comment.get('author', 'Anonymous')
                    content_text = comment.get('content', '')
                    comments_section += f"- {author}: {content_text}\n\n"

        # 构建改写指令文本
        instructions_text = ""
        if isinstance(self.rewrite_instructions, dict):
            for key, value in self.rewrite_instructions.items():
                instructions_text += f"- **{key}**: {value}\n"
        elif isinstance(self.rewrite_instructions, str):
            instructions_text = self.rewrite_instructions

        # 构建格式规则文本
        formatting_text = "\n".join(f"- {rule}" for rule in self.formatting_rules)

        # 构建示例文本
        examples_text = "\n".join(f"- {ex}" for ex in self.examples[:3])

        # 组装完整提示词
        prompt = f"""{self.role_definition}

# 任务
将以下英文技术文章改写为中文版本。

# 原文章信息
标题：{title}

内容：
{content}
{comments_section}
# 改写要求

{instructions_text}

# 格式规则

{formatting_text}

# 风格示例

{examples_text}

# 输出格式

标题：[改写后的标题]

内容：[改写后的正文内容]

---

现在开始改写："""

        return prompt
