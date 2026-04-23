#!/usr/bin/env python3
"""
数据清空脚本
用于清空数据库中的测试数据
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.database.db_manager import DBManager

def main():
    print("=" * 60)
    print("           GW2日志评分系统 - 数据清空工具")
    print("=" * 60)
    print()
    
    db_manager = DBManager()
    
    while True:
        print("请选择操作:")
        print("  1 - 清空当日数据")
        print("  2 - 清空所有数据")
        print("  0 - 退出")
        print()
        
        choice = input("请输入选项编号 (0-2): ").strip()
        
        if choice == "0":
            print("感谢使用，再见！")
            break
        elif choice == "1":
            confirm = input("【警告】即将清空当日数据！确定要继续吗？(y/N): ").strip().lower()
            if confirm == "y":
                db_manager.clear_today_data(backup=True)
            else:
                print("操作已取消")
        elif choice == "2":
            confirm = input("【警告】即将清空所有数据！确定要继续吗？(y/N): ").strip().lower()
            if confirm == "y":
                double_confirm = input("再次确认：真的要清空所有数据吗？(yes/N): ").strip().lower()
                if double_confirm == "yes":
                    db_manager.clear_all_data(backup=True)
                else:
                    print("操作已取消")
            else:
                print("操作已取消")
        else:
            print("无效选项，请重试")
        print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n操作已中断")
        sys.exit(1)
