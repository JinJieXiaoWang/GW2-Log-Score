#!/usr/bin/env python3
"""
测试日志解析功能
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parser.gw2_log_parser import GW2LogParser


def test_json_parsing():
    """测试JSON文件解析"""
    print("=== 测试JSON文件解析 ===")
    json_file = os.path.join(os.path.dirname(__file__), "data.json")
    
    if not os.path.exists(json_file):
        print(f"错误: JSON文件不存在 {json_file}")
        return False
    
    try:
        parser = GW2LogParser()
        result = parser.parse_file(json_file)
        print(f"解析成功!")
        print(f"战斗名称: {result['encounter_name']}")
        print(f"模式: {result['mode']}")
        print(f"时长: {result['duration']:.2f}秒")
        print(f"玩家数量: {len(result['players'])}")
        print(f"记录者: {result['recorded_by']}")
        print(f"日期: {result['date']}")
        
        if result['players']:
            print("\n玩家列表")
            for i, player in enumerate(result['players'][:3]):
                print(f"{i+1}. {player['name']} ({player['account']}) - {player['profession']} - DPS: {player['dps']}")
        
        return True
    except Exception as e:
        print(f"解析失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_zevtc_parsing():
    """测试ZEVTC文件解析"""
    print("\n=== 测试ZEVTC文件解析 ===")
    zevtc_file = os.path.join(os.path.dirname(__file__), "20260420-000535.zevtc")
    
    if not os.path.exists(zevtc_file):
        print(f"错误: ZEVTC文件不存在 {zevtc_file}")
        return False
    
    try:
        parser = GW2LogParser()
        result = parser.parse_file(zevtc_file)
        print(f"解析成功!")
        print(f"战斗名称: {result['encounter_name']}")
        print(f"模式: {result['mode']}")
        print(f"时长: {result['duration']:.2f}秒")
        print(f"玩家数量: {len(result['players'])}")
        print(f"记录者: {result['recorded_by']}")
        print(f"日期: {result['date']}")
        
        if result['players']:
            print("\n玩家列表")
            for i, player in enumerate(result['players'][:3]):
                print(f"{i+1}. {player['name']} ({player['account']}) - {player['profession']} - DPS: {player['dps']}")
        
        return True
    except Exception as e:
        print(f"解析失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("开始测试日志解析功能..\n")
    
    json_success = test_json_parsing()
    zevtc_success = test_zevtc_parsing()
    
    print("\n=== 测试结果 ===")
    print(f"JSON解析: {'成功' if json_success else '失败'}")
    print(f"ZEVTC解析: {'成功' if zevtc_success else '失败'}")
    
    if json_success and zevtc_success:
        print("\n所有测试都通过了")
        sys.exit(0)
    else:
        print("\n测试失败!")
        sys.exit(1)
