#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试字典数据初始化
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.db_manager import DBManager
from app.database.dict_init import DictionaryDataInitializer

def test_dict_initialization():
    """
    测试字典数据初始化
    """
    print("=== 测试字典数据初始化 ===")
    
    # 创建数据库管理器
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "database",
        "gw2_logs.db"
    )
    
    print(f"数据库路径: {db_path}")
    
    try:
        # 初始化数据库管理器
        db_manager = DBManager(db_path)
        print("✓ 数据库管理器初始化成功")
        
        # 初始化字典数据
        initializer = DictionaryDataInitializer(db_manager)
        print("✓ 字典数据初始化器创建成功")
        
        # 执行初始化
        results = initializer.initialize_all()
        print("✓ 字典数据初始化执行成功")
        
        # 打印初始化结果
        print("\n初始化结果:")
        for dict_type, result in results.items():
            print(f"{dict_type}: 创建 {result['created']} 条, 跳过 {result['skipped']} 条")
        
        # 验证字典类型是否正确创建
        print("\n验证字典类型:")
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT dict_type, dict_name FROM sys_dict_type ORDER BY sort_order")
            dict_types = cursor.fetchall()
            
            print("\n已创建的字典类型:")
            for dict_type, dict_name in dict_types:
                print(f"- {dict_type}: {dict_name}")
            
            # 验证所有字典类型都以 gw2_ 开头
            gw2_types = [dt for dt, _ in dict_types if dt.startswith('gw2_')]
            print(f"\n以 'gw2_' 开头的字典类型数量: {len(gw2_types)}")
            print(f"总字典类型数量: {len(dict_types)}")
            
            if len(gw2_types) == len(dict_types):
                print("✓ 所有字典类型都以 'gw2_' 开头")
            else:
                print("✗ 存在不以 'gw2_' 开头的字典类型")
        
        print("\n=== 测试完成 ===")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_dict_initialization()
