# 公众号海外文章自动化搬运工

自动化搬运海外越野摩托车器材与技术文章，通过AI改写翻译后发布到微信公众号。

## 功能特性

- 🔍 手动输入文章URL进行抓取
- 🤖 支持多种AI提供商（Gemini/GLM/Claude）进行智能改写和翻译
- 📝 自动适配微信公众号格式
- 🖼️ 图片下载和优化
- 📤 自动上传素材和发布
- 💾 草稿箱管理

## 快速开始

### 1. 环境要求

- Python 3.10+
- pip

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制配置模板并填写你的API密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写必要的配置项：

#### 必填配置
- **微信公众号**: `WECHAT_APP_ID`, `WECHAT_APP_SECRET`
- **AI提供商**: 选择以下任一：
  - Gemini: `AI_PROVIDER=gemini`, `GEMINI_API_KEY`
  - 智谱GLM: `AI_PROVIDER=glm`, `GLM_API_KEY`
  - Claude: `AI_PROVIDER=claude`, `ANTHROPIC_API_KEY`

#### 可选配置
- `GOOGLE_API_KEY`: Google Search API（用于文章搜索）
- 其他配置项见 `.env.example` 文件

### 4. 运行程序

```bash
python main.py
```

## 项目结构

```
wechat-PA/
├── src/
│   ├── article_fetcher/      # 文章抓取模块
│   ├── content_rewriter/     # AI内容改写模块
│   ├── wechat_publisher/     # 微信公众号发布模块
│   ├── image_processor/      # 图片处理模块
│   ├── utils/                # 工具函数
│   └── models/               # 数据模型
├── main.py                   # 程序入口
├── config.py                 # 配置管理
└── requirements.txt          # 项目依赖
```

## 核心模块

### 模块1: 文章抓取器
从海外网站抓取文章内容、图片和元数据

### 模块2: 内容改写器
使用AI进行智能翻译和改写（支持Gemini/GLM/Claude）

### 模块3: 微信公众号发布器
管理素材、草稿和自动发布

### 模块4: 图片处理器
下载、优化和上传图片

## AI提供商配置

项目支持多种AI提供商，通过 `AI_PROVIDER` 环境变量切换：

### 1. Google Gemini（默认）
```bash
AI_PROVIDER=gemini
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-1.5-pro
```

**优点**:
- 免费额度较大
- 支持长文本
- 翻译质量高

### 2. 智谱GLM
```bash
AI_PROVIDER=glm
GLM_API_KEY=your_api_key
GLM_MODEL=glm-4-plus
```

**优点**:
- 国内访问稳定
- 对中文理解好
- 价格相对便宜

### 3. Anthropic Claude
```bash
AI_PROVIDER=claude
ANTHROPIC_API_KEY=your_api_key
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

**优点**:
- 内容质量最高
- 技术文章理解能力强
- 输出稳定性好

## 开发路线图

- [x] 项目初始化
- [ ] 文章抓取功能
- [ ] AI改写功能（支持多提供商）
- [ ] 微信公众号集成
- [ ] 图片处理功能
- [ ] 端到端测试

## 配置说明

### AI提供商选择

在 `.env` 文件中设置 `AI_PROVIDER`：
```bash
# 使用 Gemini（推荐用于免费开发）
AI_PROVIDER=gemini

# 使用智谱GLM（国内访问稳定）
AI_PROVIDER=glm

# 使用Claude（质量最高，付费）
AI_PROVIDER=claude
```

只需配置对应的API密钥即可，程序会自动加载相应的配置。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
