#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EPUB to Markdown Converter
将EPUB文件转换为Markdown格式的脚本
"""

import os
import sys
from pathlib import Path
import argparse
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def check_dependencies():
    """检查必要的依赖是否已安装"""
    try:
        import ebooklib
        from ebooklib import epub
        import html2text
        return True
    except ImportError as e:
        logging.error("❌ 缺少必要的依赖包！")
        logging.error("请运行以下命令安装：")
        logging.error("pip install ebooklib html2text")
        logging.error(f"错误详情: {e}")
        return False

# 全局导入依赖
try:
    import ebooklib
    from ebooklib import epub
    import html2text
except ImportError:
    pass  # 在main函数中会检查

def convert_epub_to_markdown(epub_path, output_dir=None):
    """
    将EPUB文件转换为Markdown
    
    Args:
        epub_path (str): EPUB文件路径
        output_dir (str): 输出目录，默认为converted_md
    
    Returns:
        bool: 转换是否成功
    """
    
    epub_path = Path(epub_path)
    if not epub_path.exists():
        logging.error(f"❌ EPUB文件不存在: {epub_path}")
        return False
    
    # 设置输出目录
    if output_dir is None:
        output_dir = Path("converted_md")
    else:
        output_dir = Path(output_dir)
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 设置输出文件名
    output_file = output_dir / f"{epub_path.stem}.md"
    
    logging.info(f"📖 正在转换: {epub_path.name}")
    
    try:
        # 读取EPUB文件
        book = epub.read_epub(str(epub_path))
        
        # 获取书籍信息
        title = book.get_metadata('DC', 'title')
        book_title = title[0][0] if title else epub_path.stem
        logging.info(f"📚 书籍标题: {book_title}")
        
        # 配置HTML到Markdown转换器
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.body_width = 0          # 不限制行宽
        h.unicode_snob = True     # 更好的Unicode处理
        h.escape_snob = True      # 避免转义问题
        h.skip_internal_links = False # 尝试保留内部链接
        h.inline_links = True     # 链接直接显示在文本中
        # 关键修改：将 single_line_break 设置为 False，确保生成空行作为段落分隔
        h.single_line_break = False 
        h.emphasis_delimiter = '_' # 强调符号，避免和`*`冲突
        h.strong_delimiter = '__'  # 加粗符号

        markdown_content = []
        
        # 添加书籍标题作为一级标题
        markdown_content.append(f"# {book_title}\n\n")
        
        # 遍历EPUB中的所有项目
        processed_items = 0
        total_html_chars = 0
        total_md_chars = 0

        # 遍历book.spine来获取主要内容，而不是book.get_items()
        # spine 包含了阅读顺序中的主要文档项
        spine_items_count = len(book.spine)
        logging.debug(f"    调试: Spine 中共有 {spine_items_count} 个项目。")

        for i, (item_id, is_linear) in enumerate(book.spine):
            item = book.get_item_with_id(item_id) # 从item_id获取完整的item对象

            if item is None:
                logging.warning(f"⚠️  在 Spine 中找到 ID '{item_id}' 但无法获取对应的 Item 对象，跳过。")
                continue

            item_type = item.get_type()
            item_media_type = item.media_type # 获取媒体类型

            logging.debug(f"    调试: 处理 Spine 项目 '{item_id}', 类型: {item_type}, 媒体类型: {item_media_type}")

            # 仅处理文档类型的内容（HTML/XHTML），排除图片、CSS等辅助文件
            if item_media_type in ['application/xhtml+xml', 'text/html']:
                html_content = ""
                try:
                    # 首先尝试使用 get_body_content (标准HTML内容)
                    html_content_bytes = item.get_body_content()
                    html_content = html_content_bytes.decode('utf-8', errors='ignore')
                    logging.debug(f"        尝试 get_body_content 成功 for '{item_id}'.")
                except AttributeError:
                    # 如果没有 get_body_content 方法，则尝试 get_content (原始内容)
                    try:
                        html_content_bytes = item.get_content()
                        html_content = html_content_bytes.decode('utf-8', errors='ignore')
                        logging.debug(f"        get_body_content 失败，尝试 get_content 成功 for '{item_id}'.")
                    except Exception as e:
                        logging.error(f"❌ 无法从章节 '{item_id}' (Spine Item {i+1}) 获取内容: {e}，跳过。")
                        continue
                except Exception as e:
                    logging.error(f"❌ 获取章节 '{item_id}' (Spine Item {i+1}) HTML内容失败: {e}，跳过。")
                    continue
                
                html_len = len(html_content.strip())
                total_html_chars += html_len

                if not html_content.strip():
                    logging.warning(f"⚠️  章节 '{item_id}' (Spine Item {i+1}) HTML内容为空，跳过。")
                    continue
                
                md_content = h.handle(html_content)
                md_content = md_content.strip()
                
                md_len = len(md_content)
                total_md_chars += md_len

                if md_content:
                    markdown_content.append(md_content)
                    processed_items += 1
                    logging.info(f"    ✅ 章节 '{item_id}' (Spine Item {i+1}) 转换成功。HTML字符: {html_len}, MD字符: {md_len}")
                else:
                    logging.warning(f"⚠️  章节 '{item_id}' (Spine Item {i+1}) 转换后Markdown内容为空，跳过。HTML字符: {html_len}")
                        
            else:
                logging.debug(f"    调试: 忽略非 HTML/XHTML 类型 Spine 项目 '{item_id}', 媒体类型: {item_media_type}")
        
        if processed_items == 0:
            logging.error("❌ 没有找到可转换的内容或所有章节均为空。")
            return False
        
        # 写入Markdown文件
        final_content = "\n\n---\n\n".join(markdown_content)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        logging.info(f"✅ 转换成功!")
        logging.info(f"📄 处理了 {processed_items} 个有效章节")
        logging.info(f"📊 原始HTML总字符: {total_html_chars:,}, 转换后MD总字符: {total_md_chars:,}")
        logging.info(f"💾 输出文件: {output_file}")
        logging.info(f"📊 文件大小: {output_file.stat().st_size / 1024:.1f} KB")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ 转换失败: {e}")
        return False

def convert_single_file(epub_path, output_dir=None):
    """转换单个EPUB文件"""
    return convert_epub_to_markdown(epub_path, output_dir)

def convert_directory(input_dir, output_base_dir="converted_md"):
    """批量转换目录中的所有EPUB文件"""
    input_path = Path(input_dir)
    if not input_path.exists():
        logging.error(f"❌ 输入目录不存在: {input_dir}")
        return
    
    epub_files = list(input_path.rglob("*.epub"))
    if not epub_files:
        logging.error(f"❌ 在 {input_dir} 中没有找到EPUB文件")
        return
    
    logging.info(f"🔍 找到 {len(epub_files)} 个EPUB文件")
    
    # 按杂志类型分组统计
    magazine_stats = {}
    
    success_count = 0
    for epub_file in epub_files:
        # 获取杂志类型（一级目录名）
        # 例如：downloaded_epubs/01_economist/te_2024.01.06/file.epub
        # 提取 "01_economist"
        relative_path = epub_file.relative_to(input_path)
        magazine_type = relative_path.parts[0]  # 获取第一级目录名
        
        # 设置输出目录为二级结构：converted_md/01_economist/
        output_dir = Path(output_base_dir) / magazine_type
        
        # 统计信息
        if magazine_type not in magazine_stats:
            magazine_stats[magazine_type] = {'total': 0, 'success': 0}
        magazine_stats[magazine_type]['total'] += 1
        
        logging.info(f"\n{'='*60}")
        logging.info(f"📁 杂志类型: {magazine_type}")
        logging.info(f"📂 输出目录: {output_dir}")
        
        if convert_epub_to_markdown(epub_file, output_dir):
            success_count += 1
            magazine_stats[magazine_type]['success'] += 1
    
    # 显示详细统计
    logging.info(f"\n{'='*60}")
    logging.info("🎉 批量转换完成！")
    logging.info(f"📊 总计：成功转换 {success_count}/{len(epub_files)} 个文件")
    logging.info("\n📈 各杂志转换统计:")
    for mag_type, stats in magazine_stats.items():
        logging.info(f"  📖 {mag_type}: {stats['success']}/{stats['total']} 个文件")
    logging.info(f"\n📁 所有转换后的文件都保存在: {output_base_dir}/")
    logging.info("目录结构: converted_md/杂志类型/文件名.md")

def main():
    """主函数"""
    if not check_dependencies():
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description="EPUB to Markdown 转换器")
    parser.add_argument("input", nargs="?", # 允许0个或1个输入路径
                       help="输入的EPUB文件或目录路径")
    parser.add_argument("-o", "--output", 
                       help="输出目录 (默认: converted_md)")
    parser.add_argument("--batch", action="store_true",
                       help="批量转换模式")
    
    args = parser.parse_args()
    
    # 如果没有提供参数，使用默认设置
    if not args.input:
        # 默认转换特定文件
        default_epub = "downloaded_epubs/01_economist/te_2024.01.06/TheEconomist.2024.01.06.epub"
        logging.info(f"🔧 使用默认文件: {default_epub}")
        
        if not Path(default_epub).exists():
            logging.error("❌ 默认文件不存在，请指定要转换的EPUB文件")
            logging.error("用法示例:")
            logging.error("  python convert.py path/to/your/file.epub")
            logging.error("  python convert.py downloaded_epubs --batch")
            sys.exit(1)
            
        convert_single_file(default_epub, args.output)
    
    elif args.batch or Path(args.input).is_dir():
        # 批量转换模式
        convert_directory(args.input, args.output or "converted_md")
    
    else:
        # 单文件转换模式
        convert_single_file(args.input, args.output)

if __name__ == "__main__":
    # 将日志级别设置为 DEBUG 以查看所有项目类型
    logging.getLogger().setLevel(logging.DEBUG)
    main()
