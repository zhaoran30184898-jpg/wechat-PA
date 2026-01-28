# 工作流程与规则

> **最后更新：** 2026-01-28
> **当前版本：** v2.0

---

## 🚀 快速开始（每次启动项目必读）

### 第1步：同步最新代码
```bash
cd C:\Users\dbaa\Desktop\wechat-PA
git pull origin main
```

### 第2步：检查当前进度
```bash
# 查看项目进度文档
type PROGRESS.md

# 或用编辑器打开
code PROGRESS.md
```

### 第3步：验证系统状态
```bash
# 检查Python环境
python --version

# 检查依赖包
pip list | findstr aiohttp
pip list | findstr zhipuai

# 测试风格系统
python main.py --list-styles
```

**预期输出：**
```
预定义风格:
  - moto_mechanic - 摩托车老司机风格 - 专业且接地气

总计: 1 个风格
```

### 第4步：开始工作
根据 PROGRESS.md 中的"待完成功能"选择任务。

---

## 📋 当前状态速览

### ✅ 已完成（2026-01-28）
- [x] 文章抓取模块（支持论坛评论）
- [x] AI改写模块（GLM + Gemini）
- [x] 风格学习系统 MVP
- [x] moto_mechanic 预定义风格
- [x] CLI命令：--list-styles, --style
- [x] 端到端测试通过

### ⭕ 进行中
- 无

### 📅 计划中（Phase 3）
- [ ] 风格分析器（从URL/文件学习风格）
- [ ] --learn-style 命令
- [ ] --config-style 交互式配置
- [ ] 更多预定义风格模板

---

## 🛠️ 常用命令

### 开发命令
```bash
# 列出所有风格
python main.py --list-styles

# 抓取文章（测试）
python main.py --fetch <URL>

# 改写文章（默认风格）
python main.py --rewrite <URL>

# 改写文章（指定风格）
python main.py --rewrite <URL> --style moto_mechanic
```

### Git命令
```bash
# 查看状态
git status

# 提交更改
git add -A
git commit -m "描述更改内容"
git push origin main

# 查看提交历史
git log --oneline -10
```

### 测试命令
```bash
# 完整测试流程
python main.py --rewrite https://www.thumpertalk.com/forums/topic/1277693-jetting-fundamentals/ --style moto_mechanic

# 查看输出文件
dir logs\article_rewritten_*.json
```

---

## 📝 工作规则

### 规则1：每次开始工作前
1. ✅ 运行 `git pull` 同步最新代码
2. ✅ 阅读 PROGRESS.md 了解当前进度
3. ✅ 运行 `python main.py --list-styles` 验证系统
4. ✅ 确认本次工作任务

### 规则2：完成功能后
1. ✅ 运行完整测试
2. ✅ 更新 PROGRESS.md
3. ✅ 提交代码到 Git
4. ✅ 推送到 GitHub

### 规则3：遇到问题时
1. ✅ 查看 PROGRESS.md 的"已知问题"章节
2. ✅ 查看 logs/app_*.log 日志文件
3. ✅ 搜索错误信息
4. ✅ 记录问题和解决方案到 PROGRESS.md

### 规则4：切换电脑时
1. ✅ 克隆/拉取最新代码
2. ✅ 安装依赖 `pip install -r requirements.txt`
3. ✅ 复制 .env 文件（不要提交到Git）
4. ✅ 运行测试命令验证环境

---

## 🎯 优先级任务

### 高优先级（立即可做）
- [ ] 使用 moto_mechanic 风格改写多篇文章，验证稳定性
- [ ] 根据实际效果微调风格配置
- [ ] 创建更多用户自定义风格

### 中优先级（计划中）
- [ ] 实现风格分析器（StyleAnalyzer）
- [ ] 添加 --learn-style 命令
- [ ] 添加 --config-style 命令

### 低优先级（未来）
- [ ] 更多预定义风格
- [ ] 风格对比测试功能
- [ ] Web界面（可选）

---

## 📂 关键文件位置

### 必读文件
- `PROGRESS.md` - 项目进度详细文档（每次必读）
- `WORKFLOW.md` - 本文件，工作流程指南
- `.env` - 环境配置（API Key）

### 配置文件
- `config.py` - 全局配置
- `styles/predefined/moto_mechanic.json` - 风格配置
- `styles/user_custom/` - 用户自定义风格目录

### 核心代码
- `main.py` - CLI入口
- `src/content_rewriter/rewriter.py` - 改写流程
- `src/content_rewriter/style_learning/style_manager.py` - 风格管理

### 日志和输出
- `logs/app_*.log` - 运行日志
- `logs/article_rewritten_*.json` - 改写结果

---

## 🔧 快速故障排除

### 问题1：命令无响应
**检查：**
```bash
# 检查Python是否正常
python --version

# 检查依赖是否安装
pip list | findstr zhipuai

# 检查API Key
type .env
```

### 问题2：风格加载失败
**检查：**
```bash
# 验证风格文件存在
dir styles\predefined\moto_mechanic.json

# 测试风格列表
python main.py --list-styles
```

### 问题3：改写失败
**检查：**
```bash
# 查看日志
type logs\app_2026-01-28.log

# 测试API连接
python test_glm.py  # 如果存在
```

---

## 📊 进度追踪

### 版本历史
- **v2.0** (2026-01-28) - 风格学习系统 MVP
- **v1.0** (之前) - 基础抓取和改写功能

### 下个版本计划
- **v2.1** - 风格分析器
- **v2.2** - 交互式风格配置
- **v3.0** - 多风格管理工具

---

## ✅ 离开工作前检查清单

- [ ] 提交所有代码更改
- [ ] 推送到 GitHub
- [ ] 更新 PROGRESS.md（如有重要进展）
- [ ] 关闭所有编辑器和终端
- [ ] 记录下次继续的工作内容

---

**最后更新：** 2026-01-28
**下次更新：** 完成下一个功能后
