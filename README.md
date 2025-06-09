# EPUB-MD-Toolbox
一个Python工具集，用于从GitHub下载EPUB电子书，将其转换为Markdown，并按单词数限制智能合并，便于上传至NotebookLM学习和整理。

📚 电子书内容整理工具集这是一个Python脚本工具集，旨在帮助用户从GitHub仓库「经济学人、纽约客等英语外刊杂志下载」（https://github.com/hehonghui/awesome-english-ebooks）下载EPUB格式的电子书，将其转换为易于阅读和整理的Markdown格式，并根据自定义规则（如文件大小限制和日期范围）智能合并这些Markdown文件，限制在50万字以内，最终用来上传到NotebookLM用以学习。✨ 主要功能本工具集包含三个独立的Python脚本，共同实现以下功能：github_epub_downloader.py: 从指定的GitHub仓库递归扫描并下载所有EPUB文件到本地。convert.py: 将本地的EPUB文件批量或单个转换为Markdown（.md）格式，并优化内容，使其在各种Markdown阅读器中都能良好显示（包括NotebookLM）。merge_md.py: 智能合并转换后的Markdown文件。它可以将一个杂志/系列的多期Markdown文件按顺序合并成更大的文件，并严格控制每个文件的单词数（例如不超过50万单词），同时根据文件包含的最早和最晚日期自动命名文件。🚀 快速开始1. 环境准备确保你已安装Python 3。然后安装必要的依赖库：pip install requests ebooklib html2text
2. 下载EPUB文件 (github_epub_downloader.py)这个脚本用于从GitHub下载EPUB文件。配置:打开 github_epub_downloader.py，你可能需要修改以下配置：OWNER 和 REPO: 目标GitHub仓库的拥有者和仓库名。默认配置为 hehonghui/awesome-english-ebooks。BRANCH: 仓库分支，默认为 master。DOWNLOAD_DIR: EPUB文件的下载目录，默认为 downloaded_epubs。GITHUB_TOKEN: 重要！ 如果你频繁下载文件遇到GitHub API速率限制，请在此处填写你的GitHub个人访问令牌 (PAT)。PAT可以大幅提高你的API请求限制。如何生成PAT:登录GitHub。进入 Settings -> Developer settings -> Personal access tokens -> Tokens (classic)。点击 Generate new token。为你的令牌命名（例如：epub-downloader），并授予 public_repo 或 repo (如果仓库是私有的) 权限。复制生成的令牌，替换 github_epub_downloader.py 中的 GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"。运行:python github_epub_downloader.py
脚本将递归扫描并下载所有找到的EPUB文件到 DOWNLOAD_DIR 指定的目录中，并保持原有的目录结构。3. 转换EPUB到Markdown (convert.py)这个脚本用于将EPUB文件转换为Markdown文件。运行:你可以选择转换单个文件或批量转换整个目录。转换单个EPUB文件 (使用默认示例文件):python convert.py
这将转换 downloaded_epubs/01_economist/te_2024.01.06/TheEconomist.2024.01.06.epub。转换指定的单个EPUB文件:python convert.py path/to/your/epub_file.epub
例如：python convert.py downloaded_epubs/01_economist/te_2024.05.18/TheEconomist.2024.05.18.epub
批量转换目录中的所有EPUB文件:python convert.py downloaded_epubs --batch
# 或者，如果 'downloaded_epubs' 是你的输入目录，可以直接：
python convert.py downloaded_epubs
转换后的Markdown文件将保存在 converted_md/杂志类型/文件名.md 的目录结构中。4. 合并Markdown文件 (merge_md.py)这个脚本用于将转换后的Markdown文件合并成更大的文件，并限制文件大小。运行:批量合并所有杂志的Markdown文件:python merge_md.py
这将使用默认的 converted_md 作为输入目录，merged_magazines 作为输出目录，并将每个合并文件限制在50万单词以内。自定义输入/输出目录和单词数限制:python merge_md.py --input your_converted_md_dir --output your_merged_output_dir --max-words 400000
例如，将 converted_md 目录下的文件合并到 my_final_docs 目录，每个文件不超过40万单词：python merge_md.py --input converted_md --output my_final_docs --max-words 400000
只合并特定杂志的Markdown文件:假设 converted_md 目录下有一个 01_economist 文件夹：python merge_md.py --magazine 01_economist --max-words 500000
输出文件命名规则:合并后的Markdown文件将根据其包含的最早日期和最晚日期来命名，格式为：杂志名-YYYY.MM.DD[-YYYY.MM.DD][_partX].md示例:01-economist-2024.01.06.md (如果只包含一天的内容)01-economist-2024.01.06-2024.02.10.md (如果包含多天的内容)01-economist-2024.01.06-2024.02.10_part2.md (如果因为单词数限制，同一日期范围被拆分成多部分)📁 项目结构.
├── github_epub_downloader.py  # EPUB下载脚本
├── convert.py                 # EPUB转MD脚本
├── merge_md.py                # MD合并脚本
├── downloaded_epubs/          # (自动创建) 下载的EPUB文件存放目录
│   └── 01_economist/
│       └── te_2024.01.06/
│           └── TheEconomist.2024.01.06.epub
│       └── ...
├── converted_md/              # (自动创建) 转换后的MD文件存放目录
│   └── 01_economist/
│       └── TheEconomist.2024.01.06.md
│       └── ...
└── merged_magazines/          # (自动创建) 合并后的MD文件存放目录
    └── 01-economist-2024.01.06-2024.02.10.md
    └── 01-economist-2024.02.17-2024.03.23.md
    └── ...
⚠️ 注意事项GitHub API 速率限制: 在使用 github_epub_downloader.py 时，如果没有设置 GITHUB_TOKEN，可能会很快遇到GitHub API的速率限制。强烈建议配置PAT。EPUB 结构多样性: EPUB文件内部HTML结构复杂多样，convert.py 脚本使用 html2text 库进行转换，并已进行优化以处理常见情况。但对于某些非常特殊或格式不规范的EPUB，转换效果可能不完美。单词计数准确性: merge_md.py 中的单词计数是基于简单的正则表达式匹配（字母、数字和下划线组成的序列）。对于某些特殊语言或复杂文本，这可能不是100%精确的学术级计数，但对于一般内容整理已足够。中文支持: 脚本默认使用UTF-8编码处理文件，理论上支持中文内容，但 html2text 在处理某些复杂的中文排版或特殊字符时，可能需要额外的测试和调优。🤝 贡献欢迎任何形式的贡献！如果你发现Bug，有改进建议，或者想添加新功能，请随时提交Issue或Pull Request。📄 许可证[待定，例如 MIT License 或 Apache License 2.0]
