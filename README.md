# 微信公众号海外文章自动化搬运工

> **版本：** v2.0 - Style Learning System
> **最后更新：** 2026-01-28

自动抓取英文摩托车技术文章 → AI智能改写为中文 → 发布到微信公众号

## ⚡ 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/zhaoran30184898-jpg/wechat-PA.git
cd wechat-PA
```

### 2. 安装依赖
```bash
pip install aiohttp httpx beautifulsoup4 lxml trafilatura zhipuai loguru python-dotenv pydantic
```

### 3. 配置环境变量
复制 `.env.example` 到 `.env`，填入你的 API Key：
```bash
AI_PROVIDER=glm
GLM_API_KEY=your_api_key_here
```

### 4. 测试运行
```bash
# 列出可用风格
python main.py --list-styles

# 抓取并改写文章
python main.py --rewrite https://www.thumpertalk.com/forums/topic/1277693-jetting-fundamentals/ --style moto_mechanic
```

## 🎯 核心功能

### ✅ 已实现（v2.0）
- **文章抓取** - 支持论坛评论提取（ThumperTalk）
- **AI改写** - 使用 GLM/Gemini API
- **风格系统** ⭐ - 多种文风，动态切换
- **评论整合** - 自然融入文章内容
- **CLI工具** - 简单易用的命令行接口

### 🎨 风格支持
- **moto_mechanic** - 摩托车老司机风格（专业且接地气）
- 支持自定义风格（JSON配置）

## 📖 使用文档

### 基本命令
```bash
# 列出所有可用风格
python main.py --list-styles

# 抓取文章（不改写）
python main.py --fetch <URL>

# 改写文章（默认风格）
python main.py --rewrite <URL>

# 改写文章（指定风格）⭐
python main.py --rewrite <URL> --style <风格名>
```

### 风格配置
风格配置位于 `styles/predefined/` 和 `styles/user_custom/`，格式为 JSON：

```json
{
  "name": "moto_mechanic",
  "description": "摩托车老司机风格",
  "role_definition": "你是专业的摩托车爱好者...",
  "rewrite_instructions": {
    "tone": "轻松幽默但不夸张",
    "structure": "保持原文结构"
  },
  "formatting_rules": [
    "不用emoji",
    "不用编号列表"
  ]
}
```

## 📚 详细文档

- **[PROGRESS.md](PROGRESS.md)** - 完整的项目进度和技术文档
- **[WORKFLOW.md](WORKFLOW.md)** - 工作流程和快速指南

## 🛠️ 技术栈

- **Python 3.8+** - 核心语言
- **aiohttp/httpx** - 异步HTTP请求
- **BeautifulSoup4/Trafilatura** - HTML解析
- **ZhipuAI GLM** - AI改写引擎
- **Pydantic** - 数据验证
- **Loguru** - 日志系统

## 📂 项目结构

```
wechat-PA/
├── src/
│   ├── article_fetcher/        # 文章抓取
│   ├── content_rewriter/       # AI改写
│   │   └── style_learning/     # 风格系统 ⭐
│   └── models/                 # 数据模型
├── styles/                     # 风格配置 ⭐
│   ├── predefined/             # 预定义风格
│   └── user_custom/            # 用户自定义
├── logs/                       # 日志和输出
├── PROGRESS.md                 # 项目进度文档
├── WORKFLOW.md                 # 工作流程指南
└── main.py                     # CLI入口
```

## 🎯 效果展示

### 旧版本（v1）
```markdown
🚀 越野摩托车爱好者们，你是否对燃油喷射感到困惑？

## 核心要点
1. **燃油与空气比例**：14:1

**读者经验分享**：
- ss-racing66：分享了如何...
```

### 新版本（v2 - moto_mechanic）⭐
```markdown
咱们先来聊聊这个神秘的jetting，其实啊，原理简单得很。想象一下，咱们把空气和汽油混合起来...

说到这儿，有位叫ss-racing66的车友就分享了自己的经验。
热心网友ss-racing66表示：化油器调校这事儿，其实没那么复杂...
```

## 🔜 开发路线图

### Phase 3（计划中）
- [ ] 风格分析器（从URL/文件自动学习）
- [ ] `--learn-style` 命令
- [ ] `--config-style` 交互式配置
- [ ] 更多预定义风格模板

## 🔧 环境要求

- Python 3.8+
- pip

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**快速链接：**
- 📖 [完整进度文档](PROGRESS.md)
- 🚀 [工作流程指南](WORKFLOW.md)
- 💻 [GitHub仓库](https://github.com/zhaoran30184898-jpg/wechat-PA)
