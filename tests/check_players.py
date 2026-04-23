#!/usr/bin/env python3
"""
检查测试数据中的玩家数量
"""

import json
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_data_json():
    """检查data.json中的玩家数量"""
    json_file = os.path.join(os.path.dirname(__file__), "data.json")
    
    print("=== 检查 data.json ===")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    players = data.get('players', [])
    print(f"players 数组长度: {len(players)}")
    
    if players:
        print("\n前5个玩家:")
        for i, p in enumerate(players[:5]):
            print(f"  {i+1}. {p.get('account')} - {p.get('profession')}")
        
        if len(players) > 5:
            print(f"\n... 还有 {len(players) - 5} 个玩家")
            
            print("\n最后5个玩家:")
            for i, p in enumerate(players[-5:], len(players) - 4):
                print(f"  {i}. {p.get('account')} - {p.get('profession')}")
    
    return len(players)


def test_parsing():
    """测试解析器是否能正确解析所有玩家"""
    from src.parser.ei_parser import EIParser
    
    print("\n=== 测试解析器 ===")
    json_file = os.path.join(os.path.dirname(__file__), "data.json")
    
    parser = EIParser()
    result = parser.parse_file(json_file)
    
    print(f"解析到的玩家数量: {len(result['players'])}")
    
    if result['players']:
        print("\n解析到的前5个玩家:")
        for i, p in enumerate(result['players'][:5]):
            print(f"  {i+1}. {p['account']} - {p['profession']}")
        
        if len(result['players']) > 5:
            print(f"\n解析到的最后5个玩家:")
            for i, p in enumerate(result['players'][-5:], len(result['players']) - 4):
                print(f"  {i}. {p['account']} - {p['profession']}")
    
    return len(result['players'])


if __name__ == "__main__":
    data_count = check_data_json()
    parsed_count = test_parsing()
    
    print("\n=== 对比结果 ===")
    print(f"data.json 中有: {data_count} 个玩家")
    print(f"解析器解析到: {parsed_count} 个玩家")
    print(f"匹配: {'✓' if data_count == parsed_count else '✗'}")
