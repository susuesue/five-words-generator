# 📝 三段式文案生成器

基于 DeepSeek API 的智能三段式营销文案生成工具，支持多种文档格式，自动生成两个版本的专业文案。

## ✨ 功能特点

- 🚀 **自动生成两个版本** - 一键生成官方推荐版本 A 和 B
- 📄 **多格式支持** - 支持 PDF、Word、TXT、Excel、PPTX 格式
- 🔄 **独立重新生成** - 每个版本可单独重新生成
- 🎯 **三段式结构** - 自动生成痛点、成果、团队三段式文案
- 🏷️ **智能小标题** - 并行生成生动的小标题（速度提升3倍）
- 📚 **历史记录** - 保存所有生成记录

## 🏗️ 项目结构

```
three-words-generator/
├── src/                       # 源代码目录
│   ├── __init__.py
│   ├── core/                  # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── generator.py       # 文案生成器
│   │   └── file_handler.py    # 文件处理
│   ├── api/                   # API 服务
│   │   ├── __init__.py
│   │   └── app.py             # FastAPI 应用
│   ├── web/                   # Web 界面
│   │   ├── __init__.py
│   │   └── app.py             # Streamlit 应用
│   └── utils/                 # 工具模块
│       ├── __init__.py
│       ├── config.py          # 配置管理
│       └── logger.py          # 日志管理
├── tests/                     # 测试文件
│   ├── __init__.py
│   └── test_generator.py      # 测试脚本
├── logs/                      # 日志目录（自动生成）
│   ├── app.log               # 应用日志
│   └── error.log             # 错误日志
├── uploads/                   # 上传文件临时目录（自动生成）
├── data/                      # 数据文件目录（存放测试文档）
│   └── README.md             # 数据文件使用说明
├── run.py                     # 主启动脚本
├── requirements.txt           # Python 依赖
├── .env                       # 环境变量（需自己创建）
├── .env.example              # 环境变量示例
├── .gitignore                # Git 忽略文件
└── README.md                 # 项目说明
```

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/你的用户名/three-words-generator.git
cd three-words-generator
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并添加你的 DeepSeek API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
DEEPSEEK_API_KEY=your_api_key_here
LOG_LEVEL=INFO  # 可选：DEBUG, INFO, WARNING, ERROR
```

> 💡 获取 API 密钥：访问 [DeepSeek 平台](https://platform.deepseek.com/) 注册并获取

### 4. 运行方式

#### 方式一：使用启动脚本（推荐）

```bash
python run.py
```

然后选择运行模式：
- **选项 1** - 启动 FastAPI 后端服务
- **选项 2** - 启动 Streamlit 前端界面
- **选项 3** - 同时启动后端和前端
- **选项 4** - 运行测试脚本（生成两份文案）

#### 方式二：手动启动

**启动后端服务：**
```bash
python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8081 --reload
```

**启动前端界面：**
```bash
streamlit run src/web/app.py
```

**运行测试脚本：**
```bash
# 方式一：直接运行（推荐）
python test.py

# 方式二：作为模块运行
python tests/test_generator.py
```

## 📖 使用说明

### 命令行模式

1. 将两个文档文件放在 `data/` 目录下（或项目根目录）
2. 运行 `python test.py`（推荐）或 `python run.py` 并选择选项 4
3. 等待生成完成，查看控制台输出

**支持的文件格式**：PDF、DOCX、TXT、XLSX、PPTX

**文件查找优先级**：
- 优先从 `data/` 目录查找（推荐）
- 如果 `data/` 目录为空，从项目根目录查找

**输出示例：**
```
========deepseek三段话生成器========
【让政策补贴不再"躺"在文件里】
企业常因看不懂、找不到而错失补贴...
(官方推荐版本A)
****************************************************
【告别政策补贴"迷宫"】
企业面对海量政策文件常常无从下手...
(官方推荐版本B)
```

### Web 界面模式

1. 上传两个文档文件
2. 点击"🚀 生成两个版本文案"按钮
3. 自动生成版本 A 和版本 B
4. 可独立重新生成任意版本

## 🎯 文案结构

生成的文案包含三个段落，每段带有生动的小标题：

1. **第一段：行业痛点 + AI解决方案**
   - 用生动比喻描述行业困境
   - 自然引出AI解决方案
   - 30-60字

2. **第二段：项目成果与价值**
   - 用具体案例、数据展现成果
   - 突出产品独特亮点
   - 30-60字

3. **第三段：团队优势与背景**
   - 强调专业能力和优势
   - 传递信任感和专业度
   - 30-60字

## 🛠️ 技术栈

- **后端**: FastAPI
- **前端**: Streamlit
- **AI**: DeepSeek API
- **文档处理**: PyPDF2, python-docx, pandas, python-pptx
- **并发**: ThreadPoolExecutor (3倍速度提升)
- **日志**: logging + RotatingFileHandler (自动轮转)
- **配置管理**: 统一配置文件

## ⚡ 性能优化

- ✅ 并行生成小标题（15秒 → 5秒）
- ✅ 全局 Session 复用（减少连接开销）
- ✅ 限制文件读取量（提升大文件处理速度）
- ✅ 优化的正则表达式分割
- ✅ 总体速度提升约 60-70%

## 📦 依赖说明

| 包名 | 版本 | 用途 |
|------|------|------|
| fastapi | 0.104.1 | Web API 框架 |
| streamlit | 1.28.1 | 前端界面 |
| requests | 2.31.0 | HTTP 请求 |
| PyPDF2 | 3.0.1 | PDF 文件处理 |
| python-docx | 1.1.0 | Word 文件处理 |
| pandas | 2.1.3 | Excel 文件处理 |
| python-pptx | 0.6.23 | PPT 文件处理 |

## 📝 环境要求

- Python 3.8+
- DeepSeek API 密钥

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [DeepSeek 官网](https://www.deepseek.com/)
- [DeepSeek API 文档](https://platform.deepseek.com/api-docs/)

## 📊 日志与调试

项目会自动在 `logs/` 目录生成日志文件：

- `logs/app.log` - 所有级别的日志（INFO、WARNING、ERROR）
- `logs/error.log` - 仅错误日志

**日志级别设置：**

在 `.env` 文件中配置：
```env
LOG_LEVEL=DEBUG   # 显示所有调试信息
LOG_LEVEL=INFO    # 显示一般信息（推荐）
LOG_LEVEL=WARNING # 仅显示警告和错误
LOG_LEVEL=ERROR   # 仅显示错误
```

**查看日志：**
```bash
tail -f logs/app.log      # 实时查看应用日志
tail -f logs/error.log    # 实时查看错误日志
```

## ⚙️ 配置说明

所有配置项都在 `config.py` 中统一管理，包括：

- API 配置（地址、密钥、超时设置）
- 文件处理配置（最大读取页数、段落数等）
- 文案生成配置（温度、token 数量等）
- 日志配置（级别、文件大小限制等）

修改配置后重启服务即可生效。

## ❓ 常见问题

### Q: API 调用失败怎么办？
A: 
1. 检查 `.env` 文件中的 API 密钥是否正确
2. 检查网络连接是否正常
3. 查看 `logs/error.log` 获取详细错误信息

### Q: 支持哪些文件格式？
A: 支持 PDF (.pdf), Word (.docx), 文本 (.txt), Excel (.xlsx), PowerPoint (.pptx)

### Q: 如何获得不同风格的文案？
A: 多次点击重新生成按钮，每次生成的文案都会有所不同。

### Q: 生成速度慢怎么办？
A: 
1. 确保网络连接良好，API 响应时间一般为 10-15 秒左右
2. 可以在 `config.py` 中调整超时设置
3. 检查日志查看具体耗时环节

### Q: 如何查看详细的运行日志？
A: 查看 `logs/app.log` 文件，或在 `.env` 中设置 `LOG_LEVEL=DEBUG` 获取更详细的日志

## 📧 联系方式

如有问题或建议，欢迎联系。

---

⭐ 如果这个项目对你有帮助，请给个 Star！

