# EPUB Tools Suite

一套完整的EPUB电子书下载、转换和整理工具，支持从GitHub仓库（[经济学人、纽约客等英语外刊杂志下载](https://github.com/hehonghui/awesome-english-ebooks) ）批量下载EPUB文件，转换为Markdown格式，并按单词数限制进行智能合并后上传至[NotebookLM](https://notebooklm.google/)学习。。

## 🌟 功能特性

- **📥 批量下载**: 从GitHub仓库递归扫描并下载所有EPUB文件
- **🔄 格式转换**: 高质量地将EPUB转换为Markdown格式
- **📚 智能合并**: 按单词数限制将多个Markdown文件合并成完整文档
- **📅 日期识别**: 自动识别文件名中的日期并进行排序
- **⚡ 断点续传**: 支持下载中断后继续，避免重复下载
- **🎯 速率控制**: 内置API调用和下载速率限制，避免被封禁

## 🛠️ 工具组成

### 1. GitHub EPUB 下载器 (`github_epub_downloader.py`)
从指定的GitHub仓库中递归搜索并下载所有EPUB文件。

**主要功能:**
- 递归扫描GitHub仓库的所有目录
- 智能重试机制和速率限制保护
- 支持GitHub Personal Access Token认证
- 按原始目录结构组织下载的文件

### 2. EPUB到Markdown转换器 (`epub_to_md_converter.py`)
将EPUB文件转换为高质量的Markdown格式。

**主要功能:**
- 保持原始章节结构和格式
- 优化的HTML到Markdown转换配置
- 支持单文件和批量转换模式
- 详细的转换统计信息

### 3. Markdown文件整理器 (`organize_md_files.py`)
将转换后的Markdown文件按杂志类型智能合并。

**主要功能:**
- 按单词数限制自动分卷
- 基于文件名日期进行排序和范围识别
- 智能的标题层级调整
- 生成包含详细信息的合并文档

## 🚀 快速开始

### 环境要求

- Python 3.6+
- 必需的Python包（见安装说明）

### 安装依赖

```bash
# 安装所有必需的包
pip install requests ebooklib html2text
```

### 使用流程

#### 1. 下载EPUB文件

```bash
# 配置下载器
python github_epub_downloader.py
```

**配置说明:**
- 在脚本中修改 `REPO_URL` 为目标GitHub仓库
- 建议设置 `GITHUB_TOKEN` 以提高API限制
- 调整 `DOWNLOAD_DIR` 设置下载目录

#### 2. 转换为Markdown

```bash
# 转换单个文件
python epub_to_md_converter.py path/to/file.epub

# 批量转换整个目录
python epub_to_md_converter.py downloaded_epubs --batch

# 指定输出目录
python epub_to_md_converter.py input.epub -o custom_output_dir
```

#### 3. 整理和合并文件

```bash
# 合并所有杂志（默认每个文件最多50万单词）
python organize_md_files.py

# 指定输入输出目录
python organize_md_files.py converted_md -o final_output

# 只合并特定杂志
python organize_md_files.py --magazine 01_economist

# 自定义单词数限制
python organize_md_files.py --max-words 300000
```

## 📁 目录结构

```
project/
├── github_epub_downloader.py      # GitHub EPUB下载器
├── epub_to_md_converter.py        # EPUB转换器
├── organize_md_files.py           # Markdown整理器
├── downloaded_epubs/              # 下载的EPUB文件
│   ├── 01_economist/
│   │   ├── te_2024.01.06/
│   │   └── te_2024.01.13/
│   └── 02_nature/
├── converted_md/                  # 转换后的Markdown文件
│   ├── 01_economist/
│   └── 02_nature/
└── merged_magazines/              # 最终合并的文件
    ├── 01-economist-2024.01.06-2024.12.30.md
    └── 02-nature-2024.01.01-2024.12.31.md
```

## ⚙️ 配置选项

### GitHub下载器配置

```python
# 在 github_epub_downloader.py 中修改
REPO_URL = "https://github.com/your-target/repo"  # 目标仓库
DOWNLOAD_DIR = "downloaded_epubs"                 # 下载目录
GITHUB_TOKEN = "your_token_here"                  # GitHub令牌
API_CALL_DELAY_SECONDS = 1.0                     # API调用延迟
DOWNLOAD_DELAY_SECONDS = 0.5                     # 下载延迟
```

### 转换器配置

转换器支持多种HTML到Markdown的优化选项，包括：
- 链接处理方式
- 图片保留
- 段落分隔
- 强调符号样式

### 合并器配置

- `--max-words`: 每个合并文件的最大单词数（默认500,000）
- 自动识别日期格式：`2024.01.06`, `2024-01-06`, `20240106`
- 智能标题层级调整

## 🔧 高级用法

### 自定义日期格式识别

如需支持新的日期格式，在 `organize_md_files.py` 中的 `extract_date_from_filename` 函数添加正则表达式：

```python
date_patterns = [
    r'(\d{4})\.(\d{1,2})\.(\d{1,2})',  # 2024.01.06
    r'(\d{4})-(\d{1,2})-(\d{1,2})',   # 2024-01-06
    # 添加您的自定义格式
    r'your_custom_pattern',
]
```

### GitHub Token设置

为避免API限制，建议设置GitHub Personal Access Token：

1. 访问 GitHub Settings → Developer settings → Personal access tokens
2. 生成新token，授予 `public_repo` 权限
3. 在 `github_epub_downloader.py` 中设置 `GITHUB_TOKEN`

### 批量处理优化

对于大量文件的处理，建议：
- 适当调整延迟时间避免被限流
- 监控磁盘空间使用
- 定期清理临时文件

## 📊 使用统计

每个工具都会提供详细的处理统计：

- **下载器**: 显示找到和成功下载的文件数量
- **转换器**: 显示处理的章节数、字符数转换情况
- **合并器**: 显示合并的文件数、总单词数、生成的卷数

## 🐛 故障排除

### 常见问题

**1. GitHub API限制错误**
- 设置 `GITHUB_TOKEN` 
- 增加 `API_CALL_DELAY_SECONDS`

**2. EPUB转换失败**
- 检查EPUB文件是否损坏
- 确认 `ebooklib` 和 `html2text` 已正确安装

**3. 日期识别失败**
- 检查文件名格式是否受支持
- 必要时添加自定义日期格式

**4. 内存使用过高**
- 减少 `--max-words` 参数值
- 分批处理大文件

### 调试模式

启用详细日志输出：

```python
# 在脚本开头添加
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📞 支持

如果您在使用过程中遇到问题，请：

1. 查看上述故障排除部分
2. 搜索现有的 [Issues](../../issues)
3. 创建新的 Issue 并提供详细信息

## 🙏 致谢

- [ebooklib](https://github.com/aerkalov/ebooklib) - EPUB文件处理
- [html2text](https://github.com/Alir3z4/html2text) - HTML到Markdown转换
- [requests](https://github.com/psf/requests) - HTTP请求处理

---

**Happy Reading! 📚✨**
