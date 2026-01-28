"""AI提示词模板"""


def get_rewrite_prompt(title: str, content: str, target_language: str = "zh-CN") -> str:
    """
    获取文章改写提示词

    Args:
        title: 原标题
        content: 原内容
        target_language: 目标语言

    Returns:
        完整的提示词
    """
    if target_language == "zh-CN":
        return get_chinese_rewrite_prompt(title, content)
    else:
        return get_general_rewrite_prompt(title, content, target_language)


def get_chinese_rewrite_prompt(title: str, content: str) -> str:
    """
    中文改写提示词（针对越野摩托车技术文章）

    Args:
        title: 原标题
        content: 原内容

    Returns:
        中文改写提示词
    """
    prompt = f"""你是一位专业的越野摩托车内容创作者，擅长将英文技术文章改写成适合中文读者的优质内容。

# 任务
将以下英文文章改写为中文版本，保持专业性和可读性。

# 原文章信息
标题：{title}

内容：
{content}

# 改写要求

## 1. 标题改写
- 将标题翻译成中文
- 使其吸引人且符合微信公众号风格
- 可以添加适当的emoji表情
- 保留核心关键词
- 长度控制在30字以内

## 2. 内容改写
- **翻译准确性**：准确翻译技术内容，保持专业性
- **术语处理**：重要的英文技术术语（如 jetting, carburetor, stroke 等）可以保留英文并在括号中加中文注释
- **风格适配**：
  - 使用通俗易懂的语言
  - 适当添加emoji提升可读性
  - 使用短段落，每段2-4句话
  - 重要信息用加粗或列表突出
- **结构调整**：
  - 开头可以用简短的引语吸引读者
  - 保留文章的核心技术要点
  - 可以添加小结或要点
- **语气要求**：
  - 专业但友好
  - 避免过于生硬的直译
  - 符合中文读者的阅读习惯

## 3. 特殊说明
- 这是一篇关于越野摩托车技术的文章，需要保持技术准确性
- 目标读者是摩托车爱好者和从业者
- 发布平台是微信公众号

# 输出格式

请严格按照以下格式输出：

标题：【改写后的标题】

内容：【改写后的正文内容】

---

现在请开始改写："""

    return prompt


def get_general_rewrite_prompt(title: str, content: str, target_language: str) -> str:
    """
    通用改写提示词

    Args:
        title: 原标题
        content: 原内容
        target_language: 目标语言

    Returns:
        通用改写提示词
    """
    prompt = f"""You are a professional content writer specializing in motorcycle technology articles.

# Task
Rewrite the following article into {target_language} while maintaining technical accuracy and readability.

# Original Article
Title: {title}

Content:
{content}

# Requirements

## 1. Title Rewrite
- Translate and adapt the title for {target_language} readers
- Make it engaging and suitable for social media
- Keep core keywords
- Length: under 30 words

## 2. Content Rewrite
- **Accuracy**: Maintain technical precision
- **Terminology**: Keep important English technical terms with {target_language} explanations in parentheses
- **Style**:
  - Use accessible language
  - Add appropriate emojis
  - Use short paragraphs (2-4 sentences each)
  - Highlight key information
- **Structure**:
  - Add engaging introduction
  - Preserve core technical points
  - Include summary or key takeaways

# Output Format

Please follow this exact format:

Title: [Rewritten Title]

Content: [Rewritten Content]

---

Begin rewriting now:"""

    return prompt


def get_translation_prompt(text: str, target_language: str = "zh-CN") -> str:
    """
    获取翻译提示词

    Args:
        text: 原文本
        target_language: 目标语言

    Returns:
        翻译提示词
    """
    if target_language == "zh-CN":
        return f"""请将以下文本翻译成中文。

要求：
1. 保持专业术语的准确性
2. 符合中文表达习惯
3. 重要的英文术语可以保留并在括号中加中文注释
4. 技术名词要准确翻译

待翻译文本：
{text}"""
    else:
        return f"""Please translate the following text into {target_language}.

Requirements:
1. Maintain technical accuracy
2. Follow natural language conventions
3. Keep important English terms with {target_language} explanations in parentheses
4. Accurately translate technical terms

Text to translate:
{text}"""


def get_summary_prompt(content: str, max_length: int = 200) -> str:
    """
    获取摘要生成提示词

    Args:
        content: 原内容
        max_length: 最大长度

    Returns:
        摘要提示词
    """
    return f"""请为以下文章生成一个简短的摘要（不超过{max_length}字）：

文章内容：
{content}

要求：
1. 突出文章的核心观点
2. 简洁明了
3. 吸引读者继续阅读"""
