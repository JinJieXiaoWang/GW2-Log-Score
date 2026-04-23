"""
文件命名规范检查工具

识别并修复不符合命名规范的文件

规范：
- Python文件：小写字母，单词间用下划线分隔
- 配置文件：小写字母，单词间用下划线分隔
- 测试文件：以test_开头，小写字母，单词间用下划线分隔
- 脚本文件：小写字母，单词间用下划线分隔
"""

import os
import re
from typing import List, Tuple

# 支持的文件类型及其命名规范
FILE_RULES = {
    '.py': {
        'pattern': r'^[a-z0-9_]+\.py$',
        'test_pattern': r'^test_[a-z0-9_]+\.py$',
        'dir_exceptions': ['__pycache__']
    },
    '.json': {
        'pattern': r'^[a-z0-9_]+\.json$',
        'dir_exceptions': []
    },
    '.md': {
        'pattern': r'^[A-Za-z0-9_\-]+\.md$',
        'dir_exceptions': []
    },
    '.bat': {
        'pattern': r'^[a-z0-9_]+\.bat$',
        'dir_exceptions': []
    },
    '.sh': {
        'pattern': r'^[a-z0-9_]+\.sh$',
        'dir_exceptions': []
    },
    '.ps1': {
        'pattern': r'^[a-z0-9_]+\.ps1$',
        'dir_exceptions': []
    }
}

def is_valid_filename(filename: str, ext: str) -> bool:
    """
    检查文件名是否符合规范

    Args:
        filename: 文件名
        ext: 文件扩展名

    Returns:
        是否符合规范
    """
    # 特殊情况排除
    special_cases = [
        'package-lock.json',  # npm生成的文件
        'en-US.json', 'zh-CN.json'  # 语言文件
    ]
    if filename in special_cases:
        return True

    # 测试文件日期格式排除 (YYYYMMDD-HHMMSS_*.json)
    if ext == '.json' and re.match(r'^\d{8}-\d{6}_.*\.json$', filename):
        return True

    if ext not in FILE_RULES:
        return True  # 未知扩展名，默认为有效

    rule = FILE_RULES[ext]
    pattern = rule['pattern']

    # 测试文件有特殊规则
    if ext == '.py' and filename.startswith('test_'):
        pattern = rule['test_pattern']

    return bool(re.match(pattern, filename))

def should_skip_directory(dir_path: str) -> bool:
    """
    检查是否应该跳过某个目录

    Args:
        dir_path: 目录路径

    Returns:
        是否应该跳过
    """
    skip_dirs = ['.git', '.idea', 'venv', '__pycache__', 'node_modules', 'dist']
    dir_name = os.path.basename(dir_path)
    return dir_name in skip_dirs

def find_invalid_files(root_dir: str) -> List[Tuple[str, str]]:
    """
    查找不符合命名规范的文件

    Args:
        root_dir: 根目录

    Returns:
        不符合规范的文件列表，每个元素为(文件路径, 扩展名)
    """
    invalid_files = []

    for root, dirs, files in os.walk(root_dir):
        # 跳过不需要检查的目录
        dirs[:] = [d for d in dirs if not should_skip_directory(os.path.join(root, d))]

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in FILE_RULES:
                if not is_valid_filename(file, ext):
                    invalid_files.append((os.path.join(root, file), ext))

    return invalid_files

def fix_filename(filename: str) -> str:
    """
    修复文件名，使其符合规范

    Args:
        filename: 原始文件名

    Returns:
        修复后的文件名
    """
    name, ext = os.path.splitext(filename)

    # 转换为小写
    name = name.lower()

    # 替换空格和特殊字符为下划线
    name = re.sub(r'[^a-z0-9_]', '_', name)

    # 移除连续的下划线
    name = re.sub(r'_+', '_', name)

    # 移除开头和结尾的下划线
    name = name.strip('_')

    # 确保文件名不为空
    if not name:
        name = 'unnamed'

    return f"{name}{ext}"

def rename_files(invalid_files: List[Tuple[str, str]]) -> int:
    """
    重命名不符合规范的文件

    Args:
        invalid_files: 不符合规范的文件列表

    Returns:
        重命名的文件数量
    """
    renamed_count = 0

    for file_path, ext in invalid_files:
        dir_path = os.path.dirname(file_path)
        old_filename = os.path.basename(file_path)
        new_filename = fix_filename(old_filename)

        if old_filename != new_filename:
            new_file_path = os.path.join(dir_path, new_filename)
            
            # 检查新文件名是否已存在
            counter = 1
            while os.path.exists(new_file_path):
                name, ext = os.path.splitext(new_filename)
                new_filename = f"{name}_{counter}{ext}"
                new_file_path = os.path.join(dir_path, new_filename)
                counter += 1

            try:
                os.rename(file_path, new_file_path)
                print(f"Renamed: {old_filename} -> {new_filename}")
                renamed_count += 1
            except Exception as e:
                print(f"Error renaming {old_filename}: {e}")

    return renamed_count

def main():
    """
    主函数
    """
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    print(f"Scanning directory: {root_dir}")

    invalid_files = find_invalid_files(root_dir)

    if not invalid_files:
        print("No invalid filenames found.")
        return

    print(f"Found {len(invalid_files)} invalid filenames:")
    for file_path, ext in invalid_files:
        print(f"  - {os.path.relpath(file_path, root_dir)}")

    # 询问是否重命名
    answer = input("\nDo you want to rename these files? (y/n): ")
    if answer.lower() == 'y':
        renamed_count = rename_files(invalid_files)
        print(f"\nRenamed {renamed_count} files.")
    else:
        print("No files renamed.")

if __name__ == '__main__':
    main()
