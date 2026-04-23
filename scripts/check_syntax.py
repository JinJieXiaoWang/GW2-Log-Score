"""
检查Python文件语法错误
"""

import os
import sys
import ast


def check_syntax(file_path):
    """
    检查单个Python文件的语法

    Args:
        file_path: 文件路径

    Returns:
        True if syntax is correct, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True
    except SyntaxError as e:
        print(f"Syntax error in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False


def main():
    """
    检查所有Python文件的语法
    """
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    error_count = 0

    for root, dirs, files in os.walk(root_dir):
        # 跳过不需要检查的目录
        dirs[:] = [d for d in dirs if d not in ['.git', '.idea', 'venv', '__pycache__', 'node_modules', 'dist']]

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if not check_syntax(file_path):
                    error_count += 1

    if error_count == 0:
        print("All Python files have correct syntax!")
        sys.exit(0)
    else:
        print(f"Found {error_count} syntax errors!")
        sys.exit(1)


if __name__ == '__main__':
    main()
