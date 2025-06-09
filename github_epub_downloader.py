import requests
import os
import re
import time
from datetime import datetime

# --- 配置 ---
# GitHub 仓库 URL，这里依然使用同一个示例仓库
REPO_URL = "https://github.com/hehonghui/awesome-english-ebooks"
# 下载 EPUB 文件的本地目录
DOWNLOAD_DIR = "downloaded_epubs" 

# 每次 GitHub API 调用之间等待的秒数，降低速率限制风险
API_CALL_DELAY_SECONDS = 1.0 
# 每次文件下载之间等待的秒数，防止过快下载
DOWNLOAD_DELAY_SECONDS = 0.5 

# *** 重要：GitHub个人访问令牌 (PAT) 配置 ***
# 如果您频繁遇到 'rate limit exceeded' 错误，请在GitHub生成一个PAT
# 并在下面替换 'YOUR_GITHUB_TOKEN'。PAT能将您的API请求限制从 60 提升到 5000/小时。
# 生成PAT的步骤：GitHub -> Settings -> Developer settings -> Personal access tokens -> Tokens (classic) -> Generate new token
# 授予 'public_repo' 或 'repo' (如果仓库是私有的) 权限
GITHUB_TOKEN = "" # 将此行替换为您的令牌

# 创建必要的目录
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def get_github_tree(owner, repo, branch='master', path=''):
    """
    获取GitHub仓库的文件或目录内容列表。
    包含速率限制重试机制。
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
    }
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    max_retries = 5
    retry_delay = 2 # 初始重试延迟 (秒)

    for attempt in range(max_retries):
        try:
            print(f"正在获取: {url} (尝试 {attempt + 1}/{max_retries})")
            response = requests.get(url, headers=headers)
            response.raise_for_status() # 如果HTTP请求失败，抛出异常
            time.sleep(API_CALL_DELAY_SECONDS) # API调用后延迟
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code in [403, 429] and attempt < max_retries - 1:
                print(f"警告: 速率限制或服务不可用 ({e.response.status_code})。在 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
                retry_delay *= 2 # 指数退避
            else:
                print(f"错误: 获取文件列表失败 ({e.response.status_code}): {e}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"网络错误: {e}")
            return None
        except Exception as e:
            print(f"意外错误: {e}")
            return None
    return None # 达到最大重试次数仍失败

def get_all_epub_urls_from_github_repo(owner, repo, branch='master', current_path=''):
    """
    递归地从GitHub仓库中获取所有EPUB文件的URL信息。
    """
    epub_info_list = []
    contents = get_github_tree(owner, repo, branch, current_path)
    
    if contents is None: # 处理API调用失败的情况
        print(f"错误: 无法获取 {current_path} 的内容，跳过此目录。")
        return []

    for item in contents:
        # 检查文件类型是否为 .epub
        if item['type'] == 'file' and item['name'].lower().endswith('.epub'): 
            # 构建原始文件URL
            epub_url = item['download_url'] # GitHub API直接提供download_url
            
            epub_info = {
                'name': item['name'],
                'path': item['path'], # 仓库中的相对路径
                'url': epub_url,
            }
            epub_info_list.append(epub_info)
            # print(f"发现EPUB: {item['path']}") # 调试信息
            
        elif item['type'] == 'dir':
            # 递归查找子目录
            sub_epubs = get_all_epub_urls_from_github_repo(owner, repo, branch, item['path'])
            epub_info_list.extend(sub_epubs) # 合并子目录的结果
    
    return epub_info_list

def download_all_epubs_to_local(epub_urls_info):
    """
    下载所有找到的EPUB文件到本地DOWNLOAD_DIR。
    """
    downloaded_files = []
    print("\n--- 开始下载EPUB文件到本地 ---")
    
    for i, epub_info in enumerate(epub_urls_info):
        filename = epub_info['name']
        # 为了避免文件名冲突和更好地组织，可以使用原始仓库路径构建本地路径
        # 例如: downloaded_epubs/some_category/book_name.epub
        local_dir = os.path.join(DOWNLOAD_DIR, os.path.dirname(epub_info['path']))
        os.makedirs(local_dir, exist_ok=True)
        download_path = os.path.join(local_dir, filename)
        
        # 检查文件是否已存在且不为空，避免重复下载
        if os.path.exists(download_path) and os.path.getsize(download_path) > 0:
            print(f"[{i+1}/{len(epub_urls_info)}] 跳过下载，文件已存在且不为空: {filename}")
            downloaded_files.append(download_path)
        else:
            print(f"[{i+1}/{len(epub_urls_info)}] 正在下载: {filename}")
            try:
                # 使用 stream=True 进行大文件下载，并设置超时
                response = requests.get(epub_info['url'], stream=True, timeout=60) 
                response.raise_for_status() # 检查HTTP请求是否成功
                with open(download_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                downloaded_files.append(download_path)
            except requests.exceptions.RequestException as e:
                print(f"下载 {filename} 失败: {e}")
            except Exception as e:
                print(f"下载 {filename} 时发生意外错误: {e}")
        
        time.sleep(DOWNLOAD_DELAY_SECONDS) # 下载后延迟
            
    print(f"\n成功下载/找到 {len(downloaded_files)} 个EPUB文件。")
    return downloaded_files

def main():
    # 配置信息 - awesome-english-ebooks仓库
    OWNER = "hehonghui"
    REPO = "awesome-english-ebooks"
    BRANCH = "master" # 假设主分支是 'master'

    print("--- 开始 EPUB 文件下载过程 ---")
    print(f"目标仓库: {OWNER}/{REPO}/{BRANCH}")
    
    # 1. 获取所有 EPUB 文件的 URL 信息
    print("\n🔍 正在扫描 GitHub 仓库以获取 EPUB 文件 URL...")
    # 调用新的函数名，用于获取 EPUB 文件信息
    all_epub_urls_info = get_all_epub_urls_from_github_repo(OWNER, REPO, BRANCH) 
    
    if not all_epub_urls_info:
        print("❌ 未找到任何 EPUB 文件 URL，请检查仓库 URL 或权限。")
        return
    
    print(f"成功找到 {len(all_epub_urls_info)} 个 EPUB 文件 URL。")
    
    # 2. 下载所有 EPUB 文件到本地
    # 调用新的函数名，用于下载 EPUB 文件
    downloaded_files = download_all_epubs_to_local(all_epub_urls_info)
    
    if not downloaded_files:
        print("❌ 没有成功下载任何 EPUB 文件。")
        return

    print(f"\n--- 所有 EPUB 下载过程完成。共下载了 {len(downloaded_files)} 个文件 ---")

if __name__ == "__main__":
    # 首次运行需要安装依赖，现在只需要 requests
    try:
        import requests
    except ImportError:
        print("请先安装依赖包:")
        print("pip install requests") 
        exit(1)
    
    main()
