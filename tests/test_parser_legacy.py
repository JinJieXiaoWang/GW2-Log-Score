import os
from src.parser.gw2_log_parser import GW2LogParser

# 测试解析器
def test_parser():
    parser = GW2LogParser()
    
    # 测试1: 测试现有JSON解析
    print("测试1: 测试JSON解析")
    json_file = "data/samples/test.json"
    if os.path.exists(json_file):
        try:
            result = parser.parse_file(json_file)
            print(f"✓ JSON解析成功: {result['log_id']}")
            print(f"  模式: {result['mode']}")
            print(f"  玩家数量: {len(result['players'])}")
        except Exception as e:
            print(f"✗ JSON解析失败: {e}")
    else:
        print(f"✗ JSON测试文件不存在 {json_file}")
    
    # 测试2: 测试现有EVTC解析
    print("\n测试2: 测试EVTC解析")
    evtc_file = "data/samples/test.evtc"
    if os.path.exists(evtc_file):
        try:
            result = parser.parse_file(evtc_file)
            print(f"✓ EVTC解析成功: {result['log_id']}")
            print(f"  模式: {result['mode']}")
            print(f"  玩家数量: {len(result['players'])}")
        except Exception as e:
            print(f"✗ EVTC解析失败: {e}")
    else:
        print(f"✗ EVTC测试文件不存在 {evtc_file}")
    
    # 测试3: 测试现有ZEVTC解析
    print("\n测试3: 测试ZEVTC解析")
    zevtc_file = "data/samples/20260420-000535.zevtc"
    if os.path.exists(zevtc_file):
        try:
            result = parser.parse_file(zevtc_file)
            print(f"✓ ZEVTC解析成功: {result['log_id']}")
            print(f"  模式: {result['mode']}")
            print(f"  玩家数量: {len(result['players'])}")
        except Exception as e:
            print(f"✗ ZEVTC解析失败: {e}")
    else:
        print(f"✗ ZEVTC测试文件不存在 {zevtc_file}")
    
    # 测试4: 测试新的ZETVC解析
    print("\n测试4: 测试ZETVC解析")
    zetvc_file = "data/samples/20260420-000535.zetvc"
    if os.path.exists(zetvc_file):
        try:
            result = parser.parse_file(zetvc_file)
            print(f"✓ ZETVC解析成功: {result['log_id']}")
            print(f"  模式: {result['mode']}")
            print(f"  玩家数量: {len(result['players'])}")
        except Exception as e:
            print(f"✗ ZETVC解析失败: {e}")
    else:
        print(f"✗ ZETVC测试文件不存在 {zetvc_file}")

if __name__ == "__main__":
    test_parser()
