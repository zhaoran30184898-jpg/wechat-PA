# 公众号海外文章自动化搬运工 - 项目设计文档

## 项目目标

构建一个自动化工具，用于搬运海外越野摩托车器材与技术文章，通过AI改写翻译后发布到微信公众号。

**核心价值**:
- 节省手动翻译和改写时间（从小时级到分钟级）
- 保持技术准确性的同时提升可读性
- 自动化发布流程，支持批量处理

**目标用户**:
- 越野摩托车相关内容创作者
- 需要定期发布海外资讯的公众号运营者

## 技术选型

### 核心框架

#### 1. WeChat SDK: wechatpy (v1.8.18)
**选择理由**:
- Python生态中最成熟的微信公众号SDK
- 完整覆盖素材管理、草稿箱、发布API
- 活跃维护，文档完善
- 官方文档: http://docs.wechatpy.org

#### 2. HTTP客户端: httpx (v0.27.2)
**选择理由**:
- 现代化的HTTP客户端，支持同步/异步
- HTTP/2支持，性能优于requests
- 统一的API设计，易于使用
- 2025年Python项目的新标准

#### 3. AI集成: 多提供商支持
**设计理念**: 灵活支持多种AI提供商，用户可根据成本、质量和访问便利性选择

**支持的AI提供商**:

**1. Google Gemini（默认推荐）**
- **SDK**: `google-generativeai`
- **推荐模型**: `gemini-1.5-pro`
- **优势**:
  - 免费额度较大（适合开发测试）
  - 支持长文本（最多100万tokens）
  - 翻译质量高，技术文章理解好
  - API访问稳定
- **适用场景**: 开发测试、成本敏感项目

**2. 智谱GLM（国内稳定）**
- **SDK**: `zhipuai`
- **推荐模型**: `glm-4-plus`
- **优势**:
  - 国内访问无需翻墙
  - 对中文理解优秀
  - 价格相对便宜
  - 本土化支持好
- **适用场景**: 国内部署、中文为主的内容

**3. Anthropic Claude（质量最高）**
- **SDK**: `anthropic`
- **推荐模型**: `claude-sonnet-4-20250514`
- **优势**:
  - 内容质量最高
  - 技术文章理解能力最强
  - 输出稳定性最好
  - 提示词工程友好
- **适用场景**: 对质量要求极高的专业内容

**切换方式**:
通过环境变量 `AI_PROVIDER` 即可切换，无需修改代码：
```bash
AI_PROVIDER=gemini  # 或 glm, claude
```

**成本对比**（每1000 tokens）:
- Gemini: 免费 ~ $0.001
- GLM-4: ¥0.05 ~ ¥0.1
- Claude Sonnet 4: $0.003 ~ $0.015

#### 4. HTML解析: BeautifulSoup4 + trafilatura
- **BeautifulSoup4**: 灵活的HTML解析
- **Trafilatura**: 专门用于文章内容提取，准确率高

#### 5. 配置管理: Pydantic (v2.10.4)
- 类型安全的配置管理
- 运行时类型检查
- 清晰的错误提示
- IDE支持自动补全

#### 6. 日志: Loguru
- 比Python内置logging更简单强大
- 美观的彩色输出
- 自动日志轮转
- 零样板代码

### 技术栈总览

```
语言: Python 3.10+
异步框架: asyncio + httpx
AI模型: Gemini 1.5 Pro / GLM-4 Plus / Claude Sonnet 4（可切换）
微信公众号API: wechatpy
配置管理: Pydantic Settings
日志: Loguru
图片处理: Pillow
HTML解析: BeautifulSoup4 + trafilatura
测试框架: pytest
```

## 核心模块设计

### 模块1: 文章抓取器 (Article Fetcher)

**目录**: `src/article_fetcher/`

**功能**:
- 接受手动输入的URL
- 下载文章HTML内容
- 提取标题、作者、正文、图片、元数据
- 验证文章质量（字数、相关性）
- 下载并编目文章中的所有图片

**技术要点**:
- 异步抓取提升性能
- 使用trafilatura进行内容提取
- 实现User-Agent轮换避免封禁
- 错误处理和重试机制
- 缓存已抓取的文章

**关键文件**:
- `fetcher.py`: 主要抓取逻辑
- `parsers.py`: 不同来源的HTML解析器
- `validators.py`: 内容验证工具

### 模块2: 内容改写器 (Content Rewriter)

**目录**: `src/content_rewriter/`

**功能**:
- 调用AI API进行内容改写（支持Gemini/GLM/Claude）
- 英文到中文的翻译
- 适配微信公众号阅读风格（短段落、吸引人的语气）
- 质量检查确保改写内容一致性
- 生成吸引人的标题和摘要

**技术要点**:
- 多AI提供商统一接口，通过配置灵活切换
- 流式响应提升用户体验
- Token管理优化API成本
- 缓存避免重复处理
- 速率限制遵守API配额
- 专门的提示词工程

**提示词策略**:
```
角色: 你是越野摩托车领域的专业内容写作者
任务: 将这篇英文文章改写为适合中文读者的版本
要求:
- 保持技术准确性
- 使用通俗易懂的语言
- 适当保留英文技术术语
- 格式适配微信公众号（短段落、清晰的标题）
- 添加适当的emoji提升可读性
```

**关键文件**:
- `gemini_client.py`: Gemini API客户端封装
- `glm_client.py`: 智谱GLM API客户端封装
- `claude_client.py`: Claude API客户端封装（可选）
- `prompts.py`: 改写提示词模板
- `translator.py`: 翻译工具

**架构设计**:
采用策略模式（Strategy Pattern），通过 `AI_PROVIDER` 配置动态选择AI客户端：
```python
# 统一的AI客户端接口
class AIIClient(ABC):
    @abstractmethod
    async def rewrite(self, content: str) -> str:
        pass

# 根据配置动态创建客户端
def create_ai_client() -> AIIClient:
    if settings.ai_provider == "gemini":
        return GeminiClient()
    elif settings.ai_provider == "glm":
        return GLMClient()
    elif settings.ai_provider == "claude":
        return ClaudeClient()
    else:
        raise ValueError(f"Unsupported AI provider: {settings.ai_provider}")
```

### 模块3: 微信公众号发布器 (WeChat Publisher)

**目录**: `src/wechat_publisher/`

**功能**:
- 微信API认证和客户端封装
- 素材上传（图片、图文）
- 草稿箱管理
- 自动发布（立即或定时）
- Media ID追踪

**技术要点**:
- Access Token自动刷新
- API速率限制处理
- 图片尺寸优化（微信有严格限制）
- 优雅的错误处理
- 幂等操作避免重复发布

**API流程**:
```
1. 上传图片 → 获取media_ids
2. 创建草稿 → 获取draft_id
3. 预览草稿（可选）
4. 发布草稿 → 获取article_id和URL
5. 记录发布结果
```

**关键文件**:
- `client.py`: 微信API客户端封装
- `material_manager.py`: 素材上传管理
- `draft_manager.py`: 草稿箱操作
- `publisher.py`: 发布自动化

### 模块4: 图片处理器 (Image Processor)

**目录**: `src/image_processor/`

**功能**:
- 从文章源异步批量下载图片
- 压缩和调整尺寸以符合微信要求
- 格式转换（支持JPG/PNG）
- 上传优化后的图片到微信素材库
- 临时存储管理和清理

**技术要点**:
- 微信图片要求:
  - 永久素材最大5MB，临时素材最大2MB
  - 支持格式: JPG, PNG
  - 推荐尺寸: 根据用途变化
- 异步处理提升性能
- 保留或删除EXIF数据
- 处理防盗链

**优化策略**:
```python
目标: 在2MB内最大化质量
- 宽度超过1080px则调整（微信推荐）
- JPEG压缩质量85
- 删除元数据减少体积
- 降级策略: 如果仍然过大则降低质量
```

**关键文件**:
- `downloader.py`: 图片下载
- `optimizer.py`: 图片压缩和优化
- `uploader.py`: 微信图片上传

## 开发路线图

### 阶段1: 基础设施（第1周）
- [x] 项目结构搭建
- [ ] 配置管理实现
- [ ] 日志和错误处理
- [ ] 基础CLI界面

### 阶段2: 文章抓取（第2周）
- [ ] 模块1实现
- [ ] 手动URL输入支持
- [ ] 测试各种来源的内容提取
- [ ] 图片下载功能

### 阶段3: 内容改写（第3周）
- [ ] 模块2实现
- [ ] Claude API集成
- [ ] 提示词模板设计和测试
- [ ] 翻译管道

### 阶段4: 微信集成（第4周）
- [ ] 模块3实现
- [ ] API认证
- [ ] 素材上传
- [ ] 草稿管理和发布

### 阶段5: 图片处理（第5周）
- [ ] 模块4实现
- [ ] 图片优化
- [ ] 微信上传
- [ ] 批处理和性能优化

### 阶段6: 集成和测试（第6周）
- [ ] 端到端工作流测试
- [ ] 错误处理改进
- [ ] 用户文档
- [ ] 部署准备

## 风险缓解和最佳实践

### API速率限制
- 实现令牌桶算法进行速率限制
- 使用tenacity库自动重试（指数退避）
- 监控API使用量并在达到限制前警告

### 错误处理
- 带上下文的全面错误日志
- 优雅降级（一篇文章失败继续处理其他）
- 用户友好的错误消息和可操作建议

### 安全性
- 永不提交.env文件（使用pre-commit hooks强制执行）
- 所有敏感数据使用环境变量
- 实施API密钥轮换策略
- 验证所有用户输入

### 性能
- 对并发操作使用async/await
- 对重复操作实施缓存
- 尽可能批量API请求
- 分析和优化瓶颈

### 可维护性
- 整个代码库使用类型提示
- 全面的文档字符串
- 关键函数的单元测试
- 清晰的关注点分离

## 成功指标

### 功能要求
- 成功抓取和解析95%的目标文章
- 改写内容技术准确率>90%
- 发布到微信失败率<1%
- 完整处理文章时间<3分钟

### 质量要求
- 保留的技术术语准确性
- 吸引人的写作风格（通过完读率衡量）
- 正确的图片格式和优化
- 跨文章一致的品牌语气

### 运营要求
- 新用户设置时间<5分钟
- 清晰的错误消息和可操作的后续步骤
- 全面的日志记录用于调试
- 易于更新的配置

## 未来增强（MVP后）

1. **文章搜索自动化**: 集成Google Custom Search API自动发现相关文章
2. **调度系统**: 基于Cron的自动文章发现和发布
3. **分析仪表板**: 跟踪文章表现（浏览量、互动）
4. **多账号支持**: 管理多个微信公众号
5. **内容数据库**: 存储已处理文章用于参考和分析
6. **AI图片生成**: 使用DALL-E/Midjourney生成封面图
7. **翻译记忆**: 从之前的翻译中学习以保持一致性
8. **Web界面**: Flask/FastAPI Web UI简化操作
9. **浏览器扩展**: 从浏览器一键导入文章
10. **内容日历**: 提前规划和安排内容

## 关键文件列表

**优先实现（按顺序）**:
1. `config.py` - 配置管理（Pydantic），所有API集成的基础
2. `main.py` - 应用入口和CLI界面
3. `src/article_fetcher/fetcher.py` - 核心文章抓取逻辑
4. `src/content_rewriter/claude_client.py` - Claude API集成
5. `src/wechat_publisher/client.py` - 微信API客户端封装

## 参考资料

- [wechatpy文档](http://docs.wechatpy.org/zh-cn/v1/)
- [微信公众号API - 草稿箱](https://developers.weixin.qq.com/doc/subscription/guide/product/draft.html)
- [Claude API开发指南](https://www.anthropic.com/learn/build-with-claude)
- [Google Custom Search JSON API](https://developers.google.com/custom-search/v1/overview)
- [HTTPX vs Requests vs AIOHTTP](https://oxylabs.io/blog/httpx-vs-requests-vs-aiohttp)

---

**文档版本**: 1.0
**最后更新**: 2026-01-28
**项目状态**: 初始化阶段
