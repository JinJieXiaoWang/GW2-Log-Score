import os
import hashlib
import difflib
import json

# 计算文件哈希值
def get_file_hash(file_path):
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            buf = f.read(65536)
            while buf:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

# 计算文件相似度
def get_file_similarity(file1, file2):
    try:
        with open(file1, 'r', encoding='utf-8', errors='ignore') as f1:
            content1 = f1.read()
        with open(file2, 'r', encoding='utf-8', errors='ignore') as f2:
            content2 = f2.read()
        similarity = difflib.SequenceMatcher(None, content1, content2).ratio()
        return similarity
    except Exception as e:
        print(f"Error comparing {file1} and {file2}: {e}")
        return 0

# 扫描目录，识别重复文件
def scan_duplicates(root_dir):
    file_hashes = {}
    duplicate_groups = []
    
    # 遍历所有文件
    for root, dirs, files in os.walk(root_dir):
        # 跳过一些不需要扫描的目录
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', 'dist', 'build']]
        
        for file in files:
            # 跳过一些不需要扫描的文件
            if file.endswith(('.pyc', '.log', '.db', '.DS_Store')):
                continue
            
            file_path = os.path.join(root, file)
            file_hash = get_file_hash(file_path)
            
            if file_hash:
                if file_hash not in file_hashes:
                    file_hashes[file_hash] = []
                file_hashes[file_hash].append(file_path)
    
    # 找出完全重复的文件组
    for file_hash, file_paths in file_hashes.items():
        if len(file_paths) > 1:
            duplicate_groups.append({
                'type': 'exact',
                'hash': file_hash,
                'files': file_paths
            })
    
    # 找出内容高度相似的文件
    all_files = [f for paths in file_hashes.values() for f in paths]
    for i in range(len(all_files)):
        for j in range(i + 1, len(all_files)):
            file1 = all_files[i]
            file2 = all_files[j]
            similarity = get_file_similarity(file1, file2)
            if similarity > 0.9:
                # 检查是否已经在重复组中
                already_in_group = False
                for group in duplicate_groups:
                    if file1 in group['files'] or file2 in group['files']:
                        already_in_group = True
                        break
                if not already_in_group:
                    duplicate_groups.append({
                        'type': 'similar',
                        'similarity': similarity,
                        'files': [file1, file2]
                    })
    
    return duplicate_groups

# 分析重复文件的功能关联性
def analyze_duplicates(duplicate_groups):
    analysis = []
    
    for group in duplicate_groups:
        group_analysis = {
            'type': group['type'],
            'files': group['files'],
            'analysis': []
        }
        
        if group['type'] == 'exact':
            group_analysis['hash'] = group['hash']
        else:
            group_analysis['similarity'] = group['similarity']
        
        # 分析每个文件的作用和依赖关系
        for file_path in group['files']:
            file_analysis = {
                'path': file_path,
                'size': os.path.getsize(file_path),
                'dependencies': []
            }
            
            # 简单分析Python文件的依赖
            if file_path.endswith('.py'):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # 提取import语句
                        imports = []
                        for line in content.split('\n'):
                            line = line.strip()
                            if line.startswith('import ') or line.startswith('from '):
                                imports.append(line)
                        file_analysis['dependencies'] = imports
                except Exception as e:
                    print(f"Error analyzing {file_path}: {e}")
            
            group_analysis['analysis'].append(file_analysis)
        
        analysis.append(group_analysis)
    
    return analysis

# 主函数
def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Scanning directory: {root_dir}")
    
    # 扫描重复文件
    duplicate_groups = scan_duplicates(root_dir)
    
    # 分析重复文件
    analysis = analyze_duplicates(duplicate_groups)
    
    # 保存分析结果
    output_file = os.path.join(root_dir, 'duplicate_analysis.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"\nAnalysis complete. Results saved to: {output_file}")
    print(f"Found {len(duplicate_groups)} duplicate groups")
    
    # 打印简要结果
    for i, group in enumerate(analysis):
        print(f"\nGroup {i+1} ({group['type']}):")
        if group['type'] == 'exact':
            print(f"  Hash: {group['hash']}")
        else:
            print(f"  Similarity: {group['similarity']:.2f}")
        for file_info in group['analysis']:
            print(f"  - {file_info['path']} ({file_info['size']} bytes)")

if __name__ == "__main__":
    main()