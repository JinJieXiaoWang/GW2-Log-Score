#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证字典分组命名标准化
"""

import os
import sys
import sqlite3

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.db_manager import DBManager
from app.database.dict_init import DictionaryDataInitializer

def verify_dict_naming():
    """
    验证字典分组命名是否符合 gw2_ 前缀规范
    """
    print("=== 验证字典分组命名标准化 ===")
    
    # 创建数据库管理器
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "database",
        "gw2_logs.db"
    )
    
    print(f"数据库路径: {db_path}")
    
    try:
        # 初始化数据库管理器
        db = DBManager(db_path)
        print("✓ 数据库管理器初始化成功")
        
        # 检查字典类型
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            
            # 获取所有字典类型
            cursor.execute("SELECT dict_type, dict_name FROM sys_dict_type ORDER BY sort_order")
            dict_types = cursor.fetchall()
            
            print("\n当前字典类型:")
            print("-" * 60)
            
            all_valid = True
            for dict_type, dict_name in dict_types:
                is_valid = dict_type.startswith('gw2_')
                status = "✓" if is_valid else "✗"
                print(f"{status} {dict_type:<40} {dict_name}")
                if not is_valid:
                    all_valid = False
            
            print("-" * 60)
            
            # 统计结果
            total_types = len(dict_types)
            valid_types = sum(1 for dt, _ in dict_types if dt.startswith('gw2_'))
            
            print(f"\n统计结果:")
            print(f"总字典类型数量: {total_types}")
            print(f"符合规范的类型数量: {valid_types}")
            print(f"不符合规范的类型数量: {total_types - valid_types}")
            
            if all_valid:
                print("\n✓ 所有字典分组命名都符合 'gw2_' 前缀规范")
            else:
                print("\n✗ 存在不符合规范的字典分组命名")
            
            # 检查字典数据
            print("\n检查字典数据:")
            for dict_type, dict_name in dict_types:
                cursor.execute("SELECT COUNT(*) FROM sys_dict_data WHERE dict_type = ?", (dict_type,))
                count = cursor.fetchone()[0]
                print(f"{dict_type}: {count} 条数据")
        
        print("\n=== 验证完成 ===")
        return all_valid
        
    except Exception as e:
        print(f"✗ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def reinitialize_dict():
    """
    重新初始化字典数据
    """
    print("\n=== 重新初始化字典数据 ===")
    
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "database",
        "gw2_logs.db"
    )
    
    try:
        # 初始化数据库管理器
        db = DBManager(db_path)
        
        # 创建字典初始化器
        initializer = DictionaryDataInitializer(db)
        
        # 执行初始化
        results = initializer.initialize_all()
        
        print("\n初始化结果:")
        for dict_type, result in results.items():
            print(f"{dict_type}: 创建 {result['created']} 条, 跳过 {result['skipped']} 条")
        
        print("\n✓ 字典数据重新初始化成功")
        return True
        
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 先验证当前状态
    current_valid = verify_dict_naming()
    
    # 如果存在问题，重新初始化
    if not current_valid:
        print("\n重新初始化字典数据...")
        reinitialize_dict()
        
        # 再次验证
        print("\n重新验证:")
        verify_dict_naming()
