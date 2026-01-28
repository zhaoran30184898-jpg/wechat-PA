"""配置管理模块 - 使用Pydantic进行类型安全的配置"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""

    # 微信公众号配置
    wechat_app_id: str = Field(..., env="WECHAT_APP_ID")
    wechat_app_secret: str = Field(..., env="WECHAT_APP_SECRET")
    wechat_token: str = Field(default="", env="WECHAT_TOKEN")
    wechat_encoding_aes_key: str = Field(default="", env="WECHAT_ENCODING_AES_KEY")

    # AI提供商配置
    ai_provider: str = Field(default="gemini", env="AI_PROVIDER")  # claude, gemini, glm

    # Claude AI配置 (可选)
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-sonnet-4-20250514", env="ANTHROPIC_MODEL")
    anthropic_max_tokens: int = Field(default=4096, env="ANTHROPIC_MAX_TOKENS")
    anthropic_temperature: float = Field(default=0.7, env="ANTHROPIC_TEMPERATURE")

    # Google Gemini配置
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-pro", env="GEMINI_MODEL")
    gemini_max_tokens: int = Field(default=4096, env="GEMINI_MAX_TOKENS")
    gemini_temperature: float = Field(default=0.7, env="GEMINI_TEMPERATURE")

    # 智谱GLM配置
    glm_api_key: str = Field(default="", env="GLM_API_KEY")
    glm_model: str = Field(default="glm-4-plus", env="GLM_MODEL")
    glm_max_tokens: int = Field(default=4096, env="GLM_MAX_TOKENS")
    glm_temperature: float = Field(default=0.7, env="GLM_TEMPERATURE")

    # Google Search API配置
    google_api_key: str = Field(default="", env="GOOGLE_API_KEY")
    google_search_engine_id: str = Field(default="", env="GOOGLE_SEARCH_ENGINE_ID")
    google_search_num_results: int = Field(default=10, env="GOOGLE_SEARCH_NUM_RESULTS")

    # 应用配置
    app_env: str = Field(default="development", env="APP_ENV")
    app_log_level: str = Field(default="INFO", env="APP_LOG_LEVEL")
    app_timezone: str = Field(default="Asia/Shanghai", env="APP_TIMEZONE")

    # 文章处理配置
    article_language: str = Field(default="en", env="ARTICLE_LANGUAGE")
    target_language: str = Field(default="zh-CN", env="TARGET_LANGUAGE")
    article_min_length: int = Field(default=500, env="ARTICLE_MIN_LENGTH")
    article_max_length: int = Field(default=10000, env="ARTICLE_MAX_LENGTH")

    # 图片处理配置
    image_max_width: int = Field(default=1080, env="IMAGE_MAX_WIDTH")
    image_quality: int = Field(default=85, env="IMAGE_QUALITY")
    image_max_size_mb: int = Field(default=5, env="IMAGE_MAX_SIZE_MB")

    # 发布配置
    publish_auto_draft: bool = Field(default=True, env="PUBLISH_AUTO_DRAFT")
    publish_auto_publish: bool = Field(default=False, env="PUBLISH_AUTO_PUBLISH")

    # 重试配置
    http_max_retries: int = Field(default=3, env="HTTP_MAX_RETRIES")
    http_retry_delay: int = Field(default=1, env="HTTP_RETRY_DELAY")
    api_rate_limit: int = Field(default=10, env="API_RATE_LIMIT")

    # 存储配置
    temp_image_dir: str = Field(default="./temp", env="TEMP_IMAGE_DIR")
    temp_image_retention_hours: int = Field(default=24, env="TEMP_IMAGE_RETENTION_HOURS")
    log_dir: str = Field(default="./logs", env="LOG_DIR")
    log_retention_days: int = Field(default=30, env="LOG_RETENTION_DAYS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# 全局配置实例
settings = Settings()
