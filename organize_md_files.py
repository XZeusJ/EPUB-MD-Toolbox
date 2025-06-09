#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown Files Merger
将每种杂志的多个MD文件按单词数限制整合成一个完整的文件，并根据日期范围命名
"""

import os
import re
from pathlib import Path
from datetime import datetime
import argparse

def extract_date_from_filename(filename):
    """
    从文件名中提取日期
    支持多种日期格式：2024.01.06, 2024-01-06, 20240106等
    
    Args:
        filename (str): 文件名
        
    Returns:
        datetime or None: 提取到的日期对象，失败返回None
    """
    # 各种日期格式的正则表达式
    date_patterns = [
        r'(\d{4})\.(\d{1,2})\.(\d{1,2})',  # 2024.01.06
        r'(\d{4})-(\d{1,2})-(\d{1,2})',   # 2024-01-06
        r'(\d{4})_(\d{1,2})_(\d{1,2})',   # 2024_01_06
        r'(\d{4})(\d{2})(\d{2})',         # 20240106
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, filename)
        if match:
            try:
                year = int(match.group(1))
                month = int(match.group(2))
                day = int(match.group(3))
                return datetime(year, month, day)
            except ValueError:
                continue
    
    return None

def get_date_range_from_files(md_files):
    """
    从文件列表中提取日期范围
    
    Args:
        md_files (list): MD文件路径列表
        
    Returns:
        tuple: (最早日期, 最晚日期, 日期格式化字符串)
    """
    dates = []
    
    for md_file in md_files:
        date_obj = extract_date_from_filename(md_file.name)
        if date_obj:
            dates.append(date_obj)
    
    if not dates:
        return None, None, "未知日期范围"
    
    dates.sort()
    earliest = dates[0]
    latest = dates[-1]
    
    # 格式化日期范围
    if earliest == latest:
        date_range = earliest.strftime("%Y.%m.%d")
    else:
        date_range = f"{earliest.strftime('%Y.%m.%d')}-{latest.strftime('%Y.%m.%d')}"
    
    return earliest, latest, date_range

def count_words(text):
    """
    计算文本中的单词数。
    简单的通过空格分割，并过滤空字符串。
    
    Args:
        text (str): 输入文本
        
    Returns:
        int: 单词数量
    """
    # 使用正则表达式匹配单词（字母、数字和下划线组成的序列）
    words = re.findall(r'\b\w+\b', text.lower())
    return len(words)

def merge_magazine_files_by_word_limit(magazine_dir, output_dir="merged_magazines", max_words=500000):
    """
    合并单个杂志目录下的所有MD文件，直接按单词数限制分卷
    
    Args:
        magazine_dir (Path): 杂志目录路径
        output_dir (str): 输出目录
        max_words (int): 每个文件的最大单词数限制
        
    Returns:
        bool: 是否成功合并
    """
    magazine_path = Path(magazine_dir)
    if not magazine_path.exists() or not magazine_path.is_dir():
        print(f"❌ 杂志目录不存在: {magazine_dir}")
        return False
    
    # 获取所有MD文件
    md_files = list(magazine_path.glob("*.md"))
    if not md_files:
        print(f"⚠️  {magazine_path.name} 目录下没有找到MD文件")
        return False
    
    # 按文件名排序（通常包含日期信息），确保合并顺序正确
    md_files.sort(key=lambda x: x.name)
    
    print(f"📚 处理杂志: {magazine_path.name}")
    print(f"📄 找到 {len(md_files)} 个MD文件")
    print(f"📏 每个文件最大单词数限制: {max_words:,}")
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    magazine_name = magazine_path.name
    
    try:
        merged_files_info = [] # Stores info about each created merged file

        current_part_content_parts = [] # List of content strings for the current part
        current_part_word_count = 0
        current_part_original_files = [] # List of original Path objects for the current part
        
        print(f"\n开始合并 {magazine_name} 的文件 (目标单词数: {max_words:,})")

        for k, md_file in enumerate(md_files, 1): # Iterate through all MD files
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if not content:
                    print(f"    ⚠️  文件 {md_file.name} 为空，跳过")
                    continue
                
                processed_content = adjust_header_levels(content)
                
                file_date = extract_date_from_filename(md_file.name)
                issue_title_text = file_date.strftime('%Y年%m月%d日') if file_date else md_file.stem
                # Use ### for individual issue titles to keep hierarchy below top-level file title
                issue_header = f"\n\n---\n\n### 第 {k} 期 - {issue_title_text}\n" 
                
                article_full_content = issue_header + processed_content
                article_word_count = count_words(article_full_content)

                # Check if adding this article exceeds max_words for the current part
                # And ensure we don't create an empty part if the current one is already empty
                if current_part_word_count > 0 and (current_part_word_count + article_word_count > max_words):
                    # Save current part and start a new one
                    file_info = save_merged_part_file(
                        magazine_name,
                        current_part_content_parts, 
                        current_part_original_files, 
                        output_path,
                        max_words # Pass max_words for display in file header
                    )
                    merged_files_info.append(file_info)
                    print(f"    📦 已生成文件: {file_info['filename']} ({file_info['word_count']:,} 单词)")
                    
                    # Reset for new part
                    current_part_content_parts = []
                    current_part_word_count = 0
                    current_part_original_files = []
                    
                # Add current article to current part (or new part)
                current_part_content_parts.append(article_full_content)
                current_part_word_count += article_word_count
                current_part_original_files.append(md_file)
                # The 'part_num' in this print statement is now internal to how many articles are in the current part
                print(f"    ✅ 添加文件 {md_file.name} 到当前合并部分 ({current_part_word_count:,} 单词)")

            except Exception as e:
                print(f"    ❌ 读取或处理文件 {md_file.name} 失败: {e}")
                continue
        
        # Save the last part (if it has content)
        if current_part_original_files:
            file_info = save_merged_part_file(
                magazine_name,
                current_part_content_parts, 
                current_part_original_files, 
                output_path,
                max_words # Pass max_words for display in file header
            )
            merged_files_info.append(file_info)
            print(f"    📦 已生成最后部分文件: {file_info['filename']} ({file_info['word_count']:,} 单词)")
        
        # Output statistics for the magazine
        print(f"\n✅ {magazine_name} 合并完成!")
        print(f"📚 共创建 {len(merged_files_info)} 个合并文件")
        
        total_words_in_merged_files = 0
        for info in merged_files_info:
            print(f"  📖 {info['filename']}: {info['word_count']:,} 单词, 包含 {info['file_count']} 期")
            total_words_in_merged_files += info['word_count']
        
        print(f"📊 该杂志总单词数: {total_words_in_merged_files:,}")
        
        return True
        
    except Exception as e:
        print(f"❌ 合并失败: {e}")
        return False

def save_merged_part_file(magazine_name, content_parts, original_files, output_path, max_words):
    """
    保存合并后的文件。
    文件名格式: 杂志名-YYYY.MM.DD[-YYYY.MM.DD][_partX].md
    内部标题格式: # 杂志名 -YYYY.MM.DD[-YYYY.MM.DD] (第 X 部分)
    
    Args:
        magazine_name (str): 杂志名称
        content_parts (list): 当前部分的内容片段列表
        original_files (list): 该部分包含的原始文件Path对象列表
        output_path (Path): 输出路径
        max_words (int): 最大单词限制 (用于信息显示)
        
    Returns:
        dict: 合并文件信息
    """
    
    # 获取日期范围用于文件名和信息显示
    earliest, latest, date_range_str = get_date_range_from_files(original_files)

    # Clean the magazine name for filename use (replace underscores with hyphens)
    clean_magazine_name = magazine_name.replace('_', '-')

    # 构建基于日期范围的基础文件名（不带partX）
    if earliest and latest:
        base_filename_no_part = f"{clean_magazine_name}-{date_range_str}"
    else:
        # Fallback if no dates could be extracted, use a generic name
        base_filename_no_part = f"{clean_magazine_name}_merged" 

    # 检查是否存在同名的文件，以确定是否需要添加 _partX 后缀
    # 这里我们只关心是否存在不带 _partX 的文件，或者已经存在的 _partX 文件
    existing_files_with_base_prefix = sorted(list(output_path.glob(f"{base_filename_no_part}*.md")))
    
    actual_part_num = 1 # 默认是第一部分

    if existing_files_with_base_prefix:
        # 如果已经存在文件，我们需要找到最大的 part number
        max_existing_part = 0
        for f in existing_files_with_base_prefix:
            match = re.search(r'_part(\d+)\.md$', f.name)
            if match:
                max_existing_part = max(max_existing_part, int(match.group(1)))
            elif f.name == f"{base_filename_no_part}.md":
                max_existing_part = max(max_existing_part, 1) # 基础文件名被认为是 part 1

        actual_part_num = max_existing_part + 1 # 新文件的 part number

    # 构建最终文件名
    if actual_part_num > 1:
        filename = f"{base_filename_no_part}_part{actual_part_num}.md"
    else:
        filename = f"{base_filename_no_part}.md"
        
    output_file = output_path / filename

    # 生成文件内部主标题
    volume_title = f"# {magazine_name.replace('_', ' ').title()}"
    if earliest and latest:
        volume_title += f" - {date_range_str}"
    if actual_part_num > 1: # 只有当实际part_num大于1时才在内部标题中显示
        volume_title += f" (第 {actual_part_num} 部分)"
    
    # 组装完整内容
    full_content_list = [
        volume_title,
        f"\n> 本部分包含 {len(original_files)} 期内容"
    ]
    if earliest and latest and earliest != latest: # Add date range if it's actually a range
        full_content_list.append(f"> 文件日期范围: {date_range_str}")
    
    full_content_list.append(f"> 目标单词数限制: {max_words:,} 单词\n")
        
    full_content_list.extend(content_parts)
    
    final_content = "".join(full_content_list)
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    return {
        'filename': filename,
        'char_count': len(final_content), 
        'word_count': count_words(final_content), 
        'file_count': len(original_files),
        'part_num': actual_part_num # 返回实际的 part_num
    }

def adjust_header_levels(content):
    """
    调整Markdown内容中的标题层级，避免与主标题冲突
    将原有的 # 转为 ###，## 转为 ####，以此类推
    
    Args:
        content (str): 原始内容
        
    Returns:
        str: 调整后的内容
    """
    lines = content.split('\n')
    adjusted_lines = []
    
    for line in lines:
        # 检查是否是标题行
        if line.strip().startswith('#'):
            # 计算原有的#数量
            hash_count = 0
            for char in line:
                if char == '#':
                    hash_count += 1
                else:
                    break
            
            # 调整标题层级：原来的#变成###（向下移动2级）
            adjusted_level = hash_count + 2
            title_text = line[hash_count:].strip()
            adjusted_line = '#' * adjusted_level + ' ' + title_text
            adjusted_lines.append(adjusted_line)
        else:
            adjusted_lines.append(line)
    
    return '\n'.join(adjusted_lines)

def merge_all_magazines(input_dir="converted_md", output_dir="merged_magazines", max_words=500000):
    """
    批量合并所有杂志的MD文件，直接按单词数限制分卷
    
    Args:
        input_dir (str): 输入目录（包含各杂志子目录）
        output_dir (str): 输出目录
        max_words (int): 每个文件的最大单词数限制
    """
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"❌ 输入目录不存在: {input_dir}")
        return
    
    # 获取所有杂志目录
    magazine_dirs = [d for d in input_path.iterdir() if d.is_dir()]
    
    if not magazine_dirs:
        print(f"❌ 在 {input_dir} 中没有找到杂志目录")
        return
    
    print(f"🔍 找到 {len(magazine_dirs)} 个杂志目录")
    print(f"📏 全局设置：每个文件最大单词数限制: {max_words:,}") 
    
    success_count = 0
    total_files_processed = 0 
    total_merged_volumes = 0 
    
    for magazine_dir in magazine_dirs:
        print(f"\n{'='*70}")
        # Call the new merge function
        if merge_magazine_files_by_word_limit(magazine_dir, output_dir, max_words):
            success_count += 1
        
        md_count = len(list(magazine_dir.glob("*.md")))
        total_files_processed += md_count
        
        output_path = Path(output_dir)
        # Match files that start with the clean magazine name and end with .md
        clean_magazine_name = magazine_dir.name.replace('_', '-')
        magazine_merged_files = [f for f in output_path.glob(f"{clean_magazine_name}-*.md") if f.is_file()]
        total_merged_volumes += len(magazine_merged_files)
    
    print(f"\n{'='*70}")
    print("🎉 批量合并完成！")
    print(f"📊 成功处理 {success_count}/{len(magazine_dirs)} 个杂志")
    print(f"📄 总计处理 {total_files_processed} 个原始MD文件")
    print(f"📚 总计生成 {total_merged_volumes} 个合并文件")
    print(f"📁 所有合并后的文件保存在: {output_dir}/")
    print(f"💡 每个文件单词数将限制在 {max_words:,} 单词以内，并根据日期范围命名。") 

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Markdown文件合并器（按单词数限制分卷，并根据日期范围命名）") 
    parser.add_argument("input", nargs="?", default="converted_md",
                       help="输入目录 (默认: converted_md)")
    parser.add_argument("-o", "--output", default="merged_magazines",
                       help="输出目录 (默认: merged_magazines)")
    parser.add_argument("--magazine", 
                       help="只合并指定的杂志目录")
    parser.add_argument("--max-words", type=int, default=500000, 
                       help="每个文件的最大单词数限制 (默认: 500000)") 
    
    args = parser.parse_args()
    
    print("📚 Markdown文件合并器（按单词数限制分卷，并根据日期范围命名）") 
    
    if args.magazine:
        magazine_path = Path(args.input) / args.magazine
        merge_magazine_files_by_word_limit(magazine_path, args.output, args.max_words) 
    else:
        merge_all_magazines(args.input, args.output, args.max_words) 

if __name__ == "__main__":
    main()
